#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Transcribes audio through MLX-Audio plus forced timestamp alignment."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.audio.separation import DemucsSeparator
from scinoephile.audio.transcription.ctc.aligner import CtcAligner
from scinoephile.audio.transcription.exceptions import (
    TranscriptionAlignmentIncompleteError,
    TranscriptionEmptyError,
    TranscriptionRecognitionError,
)
from scinoephile.audio.transcription.preprocessing_settings import (
    DemucsMode,
    TranscriptionPreprocessingSettings,
    VadMode,
)
from scinoephile.audio.transcription.quality import is_low_information_text
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcriber import Transcriber
from scinoephile.audio.vad import VoiceActivityDetector
from scinoephile.common.file import get_temp_file_path
from scinoephile.core import Language
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.core.cache.runtime import get_distribution_identity

from .exceptions import MlxAudioTokenLimitError
from .model import MlxAudioModel
from .timing import offset_core_segments, restore_vad_timestamps

__all__ = ["MlxAudioTranscriber"]

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = getLogger(__name__)

_CHUNK_POSTPROCESSING_VERSION = "2"
"""Version of overlapping chunk ownership and timestamp clipping."""


class MlxAudioTranscriber(Transcriber):
    """Transcribes audio using MLX-Audio and a timestamp alignment stage."""

    cache_namespace = AudioCacheNamespace.TRANSCRIPTION_MLX_AUDIO
    """Registered namespace for cached MLX-Audio output."""

    backend_name = "mlx-audio"
    """Stable backend name stored in cache identities."""

    backend_label = "MLX-Audio"
    """Human-readable backend name used in log messages."""

    def __init__(
        self,
        model: MlxAudioModel,
        ctc_aligner: CtcAligner,
        language: Language,
        chunk_duration_seconds: float | None = None,
        chunk_overlap_seconds: float = 1.0,
        demucs_mode: DemucsMode = DemucsMode.OFF,
        vad_mode: VadMode = VadMode.OFF,
        cache_root_path: Path | None = None,
        overwrite_cache: bool = False,
        demucs_separator: DemucsSeparator | None = None,
        vad_detector: VoiceActivityDetector | None = None,
    ):
        """Initialize.

        Arguments:
            model: configured executable MLX-Audio model
            ctc_aligner: configured CTC timestamp aligner
            language: language to transcribe
            chunk_duration_seconds: optional chunk duration for inference
            chunk_overlap_seconds: context overlap applied to each chunk
            demucs_mode: Demucs preprocessing mode
            vad_mode: voice activity detection mode
            cache_root_path: root directory beneath which to cache
            overwrite_cache: whether to replace matching cache files
            demucs_separator: optional shared Demucs vocal separator
            vad_detector: optional shared voice activity detector
        Raises:
            ValueError: if a component language or numeric configuration is invalid
        """
        if language is not ctc_aligner.language:
            raise ValueError(
                "MLX-Audio transcriber and CTC aligner languages must match "
                f"({language} != {ctc_aligner.language})."
            )
        try:
            model_language = model.spec.languages[language]
        except KeyError as exc:
            raise ValueError(
                f"{language} is not supported by MLX-Audio "
                f"{model.spec.model_type} transcription"
            ) from exc
        if model.generate_kw.get("language") != model_language:
            raise ValueError(
                "MLX-Audio model and transcriber languages must match "
                f"({model.generate_kw.get('language')} != {model_language})."
            )
        self.language = language
        """Language to transcribe."""

        self.model = model
        """Configured executable MLX-Audio model."""

        self.ctc_aligner = ctc_aligner
        """Configured CTC timestamp aligner."""
        self.chunk_duration_seconds = chunk_duration_seconds
        self.chunk_overlap_seconds = chunk_overlap_seconds
        if (
            self.chunk_duration_seconds is not None
            and round(self.chunk_duration_seconds * 1000) <= 0
        ):
            raise ValueError(
                "MLX-Audio chunk duration must round to at least one millisecond."
            )
        if self.chunk_overlap_seconds < 0:
            raise ValueError("MLX-Audio chunk overlap must be non-negative.")
        super().__init__(
            cache_root_path,
            demucs_mode,
            vad_mode,
            overwrite_cache,
            demucs_separator,
            vad_detector,
        )

    def _get_effective_chunking(self, audio: AudioSegment) -> tuple[int | None, int]:
        """Get effective core and overlap durations for one audio input.

        Arguments:
            audio: audio whose duration may require model-safe chunking
        Returns:
            core chunk duration and overlap in milliseconds
        """
        chunk_overlap_ms = int(round(self.chunk_overlap_seconds * 1000))
        chunk_duration_ms = None
        if self.chunk_duration_seconds is not None:
            chunk_duration_ms = int(round(self.chunk_duration_seconds * 1000))

        max_audio_duration_seconds = self.model.spec.max_safe_audio_duration_seconds
        if max_audio_duration_seconds is None:
            return chunk_duration_ms, chunk_overlap_ms

        max_audio_duration_ms = int(round(max_audio_duration_seconds * 1000))
        if len(audio) <= max_audio_duration_ms:
            return chunk_duration_ms, chunk_overlap_ms

        if chunk_duration_ms is not None and chunk_duration_ms < max_audio_duration_ms:
            maximum_overlap_ms = (max_audio_duration_ms - chunk_duration_ms) // 2
            return chunk_duration_ms, min(chunk_overlap_ms, maximum_overlap_ms)

        maximum_overlap_ms = (max_audio_duration_ms - 1) // 2
        chunk_overlap_ms = min(chunk_overlap_ms, maximum_overlap_ms)
        chunk_duration_ms = max_audio_duration_ms - (2 * chunk_overlap_ms)
        return chunk_duration_ms, chunk_overlap_ms

    def _get_transcriber_cache_identity(self, audio: AudioSegment) -> CacheIdentity:
        """Get the cache identity for configured MLX-Audio output.

        Arguments:
            audio: audio whose duration selects effective chunking
        Returns:
            cache identity
        """
        chunk_duration_ms, chunk_overlap_ms = self._get_effective_chunking(audio)
        chunk_duration_seconds = None
        chunk_overlap_seconds = None
        chunk_postprocessing_version = None
        if chunk_duration_ms is not None:
            chunk_duration_seconds = chunk_duration_ms / 1000
            chunk_overlap_seconds = chunk_overlap_ms / 1000
            chunk_postprocessing_version = _CHUNK_POSTPROCESSING_VERSION
        return {
            "model_type": self.model.spec.model_type,
            "model_name": self.model.spec.name,
            "model_revision": self.model.spec.revision,
            "runtime": get_distribution_identity("mlx-audio"),
            "language": self.language.code,
            "generate_kw": dict(self.model.generate_kw),
            "chunk_duration_seconds": chunk_duration_seconds,
            "chunk_overlap_seconds": chunk_overlap_seconds,
            "chunk_postprocessing_version": chunk_postprocessing_version,
            "aligner": self.ctc_aligner.cache_configuration,
        }

    def _transcribe_attempt(
        self, audio: AudioSegment, settings: TranscriptionPreprocessingSettings
    ) -> list[TranscribedSegment]:
        """Run one uncached MLX-Audio transcription attempt.

        Arguments:
            audio: original or Demucs-separated audio to transcribe
            settings: preprocessing settings
        Returns:
            timestamped transcription segments
        Raises:
            TranscriptionEmptyError: if VAD finds no speech
        """
        trace = None
        speech_intervals = None
        if settings.use_vad:
            trace = self._get_voice_activity_trace(audio)
            speech_intervals = self.vad_detector.get_speech_intervals(trace)
            if not speech_intervals:
                raise TranscriptionEmptyError("MLX-Audio VAD found no speech.")

            logger.info(
                f"MLX-Audio VAD retained {len(speech_intervals)} speech interval(s) "
                f"from {len(audio) / 1000:.2f}s of audio"
            )
            speech_audio = audio[0:0]
            for start_ms, end_ms in speech_intervals:
                speech_audio += audio[start_ms:end_ms]
            audio = speech_audio

        chunk_duration_ms, chunk_overlap_ms = self._get_effective_chunking(audio)
        segments = self._transcribe_audio(audio, chunk_duration_ms, chunk_overlap_ms)

        if trace is None or speech_intervals is None:
            return segments
        restored_segments = restore_vad_timestamps(segments, speech_intervals)
        return self._add_voice_activity_scores(restored_segments, trace)

    def _transcribe_audio(
        self, audio: AudioSegment, chunk_duration_ms: int | None, chunk_overlap_ms: int
    ) -> list[TranscribedSegment]:
        """Transcribe audio, recursively splitting recoverable failures.

        Arguments:
            audio: audio to transcribe
            chunk_duration_ms: core chunk duration in milliseconds, if chunking
            chunk_overlap_ms: context overlap in milliseconds
        Returns:
            timestamped transcription segments
        Raises:
            TranscriptionEmptyError: if the audio contains no usable transcript
            TranscriptionError: if recognition or alignment fails
        """
        configured_overlap_ms = int(round(self.chunk_overlap_seconds * 1000))
        if chunk_duration_ms is None or len(audio) <= chunk_duration_ms:
            try:
                return self._transcribe_window(audio)
            except MlxAudioTokenLimitError:
                if len(audio) <= 1:
                    raise
                retry_reason = "generation token exhaustion"
            except TranscriptionAlignmentIncompleteError:
                if len(audio) <= 1:
                    raise
                retry_reason = "incomplete CTC alignment"

            chunk_duration_ms = max(1, len(audio) // 2)
            maximum_overlap_ms = max(0, (chunk_duration_ms - 1) // 2)
            chunk_overlap_ms = min(configured_overlap_ms, maximum_overlap_ms)
            logger.info(
                f"Retrying MLX-Audio after {retry_reason} with "
                f"{chunk_duration_ms / 1000:.3f}s chunks"
            )

        segments: list[TranscribedSegment] = []
        for core_start_ms in range(0, len(audio), chunk_duration_ms):
            core_end_ms = min(len(audio), core_start_ms + chunk_duration_ms)
            window_start_ms = max(0, core_start_ms - chunk_overlap_ms)
            window_end_ms = min(len(audio), core_end_ms + chunk_overlap_ms)
            window_audio = audio[window_start_ms:window_end_ms]
            try:
                window_segments = self._transcribe_audio(
                    window_audio, None, configured_overlap_ms
                )
            except TranscriptionEmptyError:
                logger.info(
                    f"Skipping empty MLX-Audio audio window "
                    f"{window_start_ms / 1000:.2f}s-"
                    f"{window_end_ms / 1000:.2f}s"
                )
            else:
                segments.extend(
                    offset_core_segments(
                        window_segments,
                        window_start_ms / 1000,
                        core_start_ms / 1000,
                        core_end_ms / 1000,
                        len(segments),
                    )
                )
        if not segments:
            raise TranscriptionEmptyError(
                "MLX-Audio returned no transcript across audio chunks."
            )
        return segments

    def _transcribe_window(self, audio: AudioSegment) -> list[TranscribedSegment]:
        """Run MLX-Audio inference and timestamp alignment for one audio window.

        Arguments:
            audio: audio to transcribe
        Returns:
            timestamped transcription segments
        Raises:
            DependencyError: if MLX-Audio dependencies are unavailable
            TranscriptionError: if MLX-Audio returns unusable text
            TranscriptionAlignmentError: if forced alignment fails
        """
        with get_temp_file_path(suffix=".wav") as temp_audio_path:
            audio.export(temp_audio_path, format="wav")
            try:
                inference_result = self.model(temp_audio_path)
            except (ImportError, OSError, RuntimeError, ValueError) as exc:
                raise TranscriptionRecognitionError(
                    f"Unable to run MLX-Audio inference: {exc}"
                ) from exc
            generation_tokens = inference_result.generation_tokens
            max_tokens = self.model.spec.max_tokens
            if max_tokens is not None and generation_tokens >= max_tokens:
                raise MlxAudioTokenLimitError(
                    f"MLX-Audio used {generation_tokens} of its {max_tokens} "
                    "generation tokens."
                )
            text = inference_result.text
            if not text.strip():
                raise TranscriptionEmptyError("MLX-Audio returned empty transcript.")
            if is_low_information_text(text):
                raise TranscriptionEmptyError(
                    f"MLX-Audio returned only low-information vocalizations: {text!r}"
                )
            return self.ctc_aligner(audio, text)
