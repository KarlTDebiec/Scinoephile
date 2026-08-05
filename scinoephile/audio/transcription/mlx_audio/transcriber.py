#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Transcribes audio through MLX-Audio plus forced timestamp alignment."""

from __future__ import annotations

import platform
from collections.abc import Sequence
from logging import getLogger
from math import ceil
from pathlib import Path
from typing import TYPE_CHECKING

from scinoephile.audio.transcription.ctc_aligner import CtcAligner
from scinoephile.audio.transcription.demucs import DemucsSeparator
from scinoephile.audio.transcription.exceptions import (
    TranscriptionAlignmentError,
    TranscriptionAlignmentIncompleteError,
    TranscriptionEmptyError,
    TranscriptionError,
    TranscriptionInferenceError,
)
from scinoephile.audio.transcription.preprocessing_settings import (
    DemucsMode,
    TranscriptionPreprocessingSettings,
    VADMode,
)
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcribed_word import TranscribedWord
from scinoephile.audio.transcription.transcriber import Transcriber
from scinoephile.audio.transcription.vad import VADImplementation, VoiceActivityDetector
from scinoephile.common.file import get_temp_file_path
from scinoephile.core import Language

from .backend import MIMO_MODEL_NAME, MlxAudioBackend

__all__ = ["MlxAudioTranscriber"]

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = getLogger(__name__)

_CHUNK_POSTPROCESSING_VERSION = "2"
"""Version of overlapping chunk ownership and timestamp clipping."""

_LOW_INFORMATION_CHARACTERS = frozenset("啊呀吖哦噢嗯嘶")
"""Standalone vocalizations rejected as unusable transcripts."""

_TOKEN_LIMIT_GUARD_FRACTION = 0.95
"""Generation-budget fraction treated as suspicious under the opt-in guard."""


class _MlxAudioTokenLimitError(TranscriptionInferenceError):
    """Raised when MLX-Audio exhausts its text-token generation budget."""


class MlxAudioTranscriber(Transcriber):
    """Transcribes audio using MLX-Audio and a timestamp alignment stage."""

    backend_name = "mlx-audio"
    """Stable backend name stored in cache metadata."""

    backend_label = "MLX-Audio"
    """Human-readable backend name used in log messages."""

    def __init__(
        self,
        model_name: str = MIMO_MODEL_NAME,
        language: Language = Language.yue_hant,
        ctc_model_name: str | None = None,
        max_tokens: int | None = None,
        chunk_duration_seconds: float | None = None,
        chunk_overlap_seconds: float = 1.0,
        token_limit_guard: bool = False,
        demucs_mode: DemucsMode = DemucsMode.OFF,
        vad_mode: VADMode = VADMode.OFF,
        cache_root_path: Path | None = None,
        overwrite_cache: bool = False,
        demucs_separator: DemucsSeparator | None = None,
        vad_implementation: VADImplementation = VADImplementation.SILERO,
        vad_detector: VoiceActivityDetector | None = None,
    ):
        """Initialize.

        Arguments:
            model_name: supported MLX-Audio model name or local model path
            language: language to transcribe
            ctc_model_name: optional CTC model name or local model path
            max_tokens: optional maximum number of text tokens to generate
            chunk_duration_seconds: optional chunk duration for inference
            chunk_overlap_seconds: context overlap applied to each chunk
            token_limit_guard: whether to proactively guard model-family token limits
            demucs_mode: Demucs preprocessing mode
            vad_mode: voice activity detection mode
            cache_root_path: root directory beneath which to cache
            overwrite_cache: whether to replace matching cache files
            demucs_separator: optional shared Demucs vocal separator
            vad_implementation: voice activity detection implementation
            vad_detector: optional shared voice activity detector
        Raises:
            TranscriptionError: if the platform does not support MLX-Audio
            ValueError: if the language or numeric configuration is invalid
        """
        # Reject runtimes that cannot execute MLX-Audio
        system = platform.system()
        machine = platform.machine()
        if system != "Darwin" or machine != "arm64":
            raise TranscriptionError(
                "MLX-Audio support requires macOS on Apple Silicon "
                f"(detected platform.system()={system!r}, "
                f"platform.machine()={machine!r}). "
                "CUDA support is not included."
            )

        self.backend = MlxAudioBackend(model_name, language)
        """Direct MLX-Audio inference backend."""

        self.ctc_aligner = CtcAligner(language, ctc_model_name)
        self.max_tokens = max_tokens
        self.chunk_duration_seconds = chunk_duration_seconds
        self.chunk_overlap_seconds = chunk_overlap_seconds
        self.token_limit_guard = token_limit_guard
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("MLX-Audio max tokens must be positive.")
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
            vad_implementation,
            vad_detector,
        )

    @property
    def language(self) -> Language:
        """Get the transcription language."""
        return self.backend.language

    @property
    def model_name(self) -> str:
        """Get the MLX-Audio model name or local model path."""
        return self.backend.model_name

    @property
    def _effective_max_tokens(self) -> int:
        """Get the explicit or model-family default generation token limit."""
        if self.max_tokens is not None:
            return self.max_tokens
        return self.backend.default_max_tokens

    def _get_backend_cache_metadata(
        self, settings: TranscriptionPreprocessingSettings
    ) -> dict[str, object]:
        """Get metadata that identifies cached MLX-Audio output.

        Arguments:
            settings: preprocessing settings
        Returns:
            cache identity metadata
        """
        return {
            "model_family": self.backend.model_family,
            "model_name": self.model_name,
            "runtime": "mlx",
            "language": self.language.code,
            "mlx_audio_language": self.backend.mlx_audio_language,
            "max_tokens": self._effective_max_tokens,
            "chunk_duration_seconds": self.chunk_duration_seconds,
            "chunk_overlap_seconds": self.chunk_overlap_seconds,
            "chunk_postprocessing_version": _CHUNK_POSTPROCESSING_VERSION,
            "aligner": "ctc",
            "aligner_model_name": self.ctc_aligner.model_name,
        }

    def _get_cache_metadata_for_audio(
        self, audio: AudioSegment, settings: TranscriptionPreprocessingSettings
    ) -> dict[str, object]:
        """Get cache metadata for MLX-Audio behavior used by one audio input.

        Arguments:
            audio: audio whose duration selects guarded chunking
            settings: preprocessing settings
        Returns:
            configuration identifying the output
        """
        metadata = super()._get_cache_metadata_for_audio(audio, settings)
        metadata["chunk_duration_seconds"] = self._get_effective_chunk_duration_seconds(
            audio
        )
        if self._uses_token_limit_guard(audio):
            metadata["token_limit_guard_fraction"] = _TOKEN_LIMIT_GUARD_FRACTION
        return metadata

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
            TranscriptionInferenceError: if an optional dependency or assertion fails
        """
        try:
            guard_token_limit = self._uses_token_limit_guard(audio)
            if settings.use_vad:
                return self._transcribe_vad_audio(audio, guard_token_limit)
            return self._transcribe_unfiltered_audio(audio, guard_token_limit)
        except (AssertionError, ImportError) as exc:
            raise TranscriptionInferenceError(
                f"Unable to run MLX-Audio transcription: {exc}"
            ) from exc

    def _transcribe_audio_window(
        self, audio: AudioSegment, guard_token_limit: bool = False
    ) -> list[TranscribedSegment]:
        """Run MLX-Audio transcription and timestamp alignment for one audio window.

        Arguments:
            audio: audio to transcribe
            guard_token_limit: whether to reserve generation-token headroom
        Returns:
            timestamped transcription segments
        Raises:
            TranscriptionError: if MLX-Audio returns unusable text
            TranscriptionAlignmentError: if forced alignment fails
        """
        with get_temp_file_path(suffix=".wav") as temp_audio_path:
            audio.export(temp_audio_path, format="wav")
            max_tokens = self._effective_max_tokens
            try:
                inference_result = self.backend.transcribe(temp_audio_path, max_tokens)
            except (ImportError, OSError, RuntimeError, ValueError) as exc:
                raise TranscriptionInferenceError(
                    f"Unable to run MLX-Audio inference: {exc}"
                ) from exc
            generation_tokens = inference_result.generation_tokens
            guarded_limit = ceil(max_tokens * _TOKEN_LIMIT_GUARD_FRACTION)
            if generation_tokens is not None and (
                generation_tokens >= max_tokens
                or (guard_token_limit and generation_tokens >= guarded_limit)
            ):
                raise _MlxAudioTokenLimitError(
                    f"MLX-Audio used {generation_tokens} of its {max_tokens} "
                    "generation tokens."
                )
            text = inference_result.text
            if not text.strip():
                raise TranscriptionEmptyError("MLX-Audio returned empty transcript.")
            content_characters = {char for char in text if char.isalnum()}
            if content_characters and content_characters <= _LOW_INFORMATION_CHARACTERS:
                raise TranscriptionEmptyError(
                    f"MLX-Audio returned only low-information vocalizations: {text!r}"
                )
            return self.ctc_aligner(audio, text)

    def _transcribe_audio_window_with_retry(
        self, audio: AudioSegment, guard_token_limit: bool = False
    ) -> list[TranscribedSegment]:
        """Transcribe a window, splitting it after recoverable length failures.

        Arguments:
            audio: audio window to transcribe
            guard_token_limit: whether to reserve generation-token headroom
        Returns:
            timestamped transcription segments
        Raises:
            TranscriptionError: if a one-millisecond window still fails
        """
        try:
            return self._transcribe_audio_window(audio, guard_token_limit)
        except (_MlxAudioTokenLimitError, TranscriptionAlignmentIncompleteError) as exc:
            if len(audio) <= 1:
                raise
            if isinstance(exc, _MlxAudioTokenLimitError):
                retry_reason = "generation token exhaustion"
            else:
                retry_reason = "incomplete CTC alignment"

        chunk_duration_ms = max(1, len(audio) // 2)
        maximum_overlap_ms = max(0, (chunk_duration_ms - 1) // 2)
        configured_overlap_ms = int(round(self.chunk_overlap_seconds * 1000))
        chunk_overlap_ms = min(configured_overlap_ms, maximum_overlap_ms)
        logger.info(
            f"Retrying MLX-Audio after {retry_reason} with "
            f"{chunk_duration_ms / 1000:.3f}s chunks"
        )
        return self._transcribe_chunked_audio(
            audio, chunk_duration_ms, chunk_overlap_ms, guard_token_limit
        )

    def _transcribe_chunked_audio(
        self,
        audio: AudioSegment,
        chunk_duration_ms: int,
        chunk_overlap_ms: int,
        guard_token_limit: bool = False,
    ) -> list[TranscribedSegment]:
        """Run MLX-Audio transcription over shorter overlapping chunks.

        Arguments:
            audio: audio to transcribe
            chunk_duration_ms: core chunk duration in milliseconds
            chunk_overlap_ms: context overlap in milliseconds
            guard_token_limit: whether to reserve generation-token headroom
        Returns:
            timestamped transcription segments
        """
        segments: list[TranscribedSegment] = []

        for core_start_ms in range(0, len(audio), chunk_duration_ms):
            core_end_ms = min(len(audio), core_start_ms + chunk_duration_ms)
            window_start_ms = max(0, core_start_ms - chunk_overlap_ms)
            window_end_ms = min(len(audio), core_end_ms + chunk_overlap_ms)
            window_audio = audio[window_start_ms:window_end_ms]
            try:
                window_segments = self._transcribe_audio_window_with_retry(
                    window_audio, guard_token_limit
                )
            except TranscriptionEmptyError:
                logger.info(
                    f"Skipping empty MLX-Audio audio window "
                    f"{window_start_ms / 1000:.2f}s-"
                    f"{window_end_ms / 1000:.2f}s"
                )
            else:
                segments.extend(
                    self._get_offset_core_segments(
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

    def _transcribe_unfiltered_audio(
        self, audio: AudioSegment, guard_token_limit: bool = False
    ) -> list[TranscribedSegment]:
        """Transcribe audio without applying VAD.

        Arguments:
            audio: audio to transcribe
            guard_token_limit: whether to reserve generation-token headroom
        Returns:
            timestamped transcription segments
        """
        chunk_duration_seconds = self._get_effective_chunk_duration_seconds(audio)
        if chunk_duration_seconds is None:
            return self._transcribe_audio_window_with_retry(audio, guard_token_limit)
        chunk_duration_ms = int(round(chunk_duration_seconds * 1000))
        if len(audio) <= chunk_duration_ms:
            return self._transcribe_audio_window_with_retry(audio, guard_token_limit)
        if guard_token_limit and chunk_duration_seconds != self.chunk_duration_seconds:
            logger.info(
                f"Guarding MLX-Audio generation token limit with "
                f"{chunk_duration_seconds:.3f}s chunks for "
                f"{len(audio) / 1000:.3f}s of audio"
            )
        chunk_overlap_ms = int(round(self.chunk_overlap_seconds * 1000))
        return self._transcribe_chunked_audio(
            audio, chunk_duration_ms, chunk_overlap_ms, guard_token_limit
        )

    def _transcribe_vad_audio(
        self, audio: AudioSegment, guard_token_limit: bool = False
    ) -> list[TranscribedSegment]:
        """Transcribe detected speech and restore original-audio timestamps.

        Arguments:
            audio: original audio containing speech and non-speech regions
            guard_token_limit: whether to reserve generation-token headroom
        Returns:
            timestamped transcription segments on the original audio timeline
        Raises:
            TranscriptionEmptyError: if VAD finds no speech
        """
        voice_activity_trace = self._get_voice_activity_trace(audio)
        speech_intervals = self.vad_detector.get_speech_intervals(voice_activity_trace)
        if not speech_intervals:
            raise TranscriptionEmptyError("MLX-Audio VAD found no speech.")

        logger.info(
            f"MLX-Audio VAD retained {len(speech_intervals)} speech interval(s) "
            f"from {len(audio) / 1000:.2f}s of audio"
        )
        speech_audio = audio[0:0]
        for start_ms, end_ms in speech_intervals:
            speech_audio += audio[start_ms:end_ms]

        speech_segments = self._transcribe_unfiltered_audio(
            speech_audio, guard_token_limit
        )
        restored_segments = self._restore_vad_timestamps(
            speech_segments, speech_intervals
        )
        return self._add_voice_activity_scores(restored_segments, voice_activity_trace)

    def _get_effective_chunk_duration_seconds(
        self, audio: AudioSegment
    ) -> float | None:
        """Get the explicit or guarded chunk duration for one audio input.

        Arguments:
            audio: audio whose duration selects guarded chunking
        Returns:
            effective chunk duration, or None for unchunked inference
        """
        chunk_duration_seconds = self.chunk_duration_seconds
        if not self._uses_token_limit_guard(audio):
            return chunk_duration_seconds

        guarded_duration_seconds = self.backend.token_limit_guard_chunk_duration_seconds
        assert guarded_duration_seconds is not None
        if (
            chunk_duration_seconds is None
            or chunk_duration_seconds > guarded_duration_seconds
        ):
            return guarded_duration_seconds
        return chunk_duration_seconds

    def _uses_token_limit_guard(self, audio: AudioSegment) -> bool:
        """Check whether the opt-in token-limit guard changes this audio's behavior.

        Arguments:
            audio: audio whose duration selects guarded chunking
        Returns:
            whether guarded inference is active
        """
        guarded_duration_seconds = self.backend.token_limit_guard_chunk_duration_seconds
        if not self.token_limit_guard or guarded_duration_seconds is None:
            return False
        return len(audio) > round(guarded_duration_seconds * 1000)

    @staticmethod
    def _restore_vad_timestamps(
        segments: Sequence[TranscribedSegment],
        speech_intervals: Sequence[tuple[int, int]],
    ) -> list[TranscribedSegment]:
        """Map speech-only word timings back to the original audio timeline.

        Arguments:
            segments: transcription timed against concatenated speech audio
            speech_intervals: original-audio speech intervals in milliseconds
        Returns:
            segments split and timed against the original audio
        Raises:
            TranscriptionAlignmentError: if aligned output lacks word timings
        """
        compressed_intervals: list[tuple[int, int, int]] = []
        compressed_start_ms = 0
        for original_start_ms, original_end_ms in speech_intervals:
            duration_ms = original_end_ms - original_start_ms
            compressed_end_ms = compressed_start_ms + duration_ms
            compressed_intervals.append(
                (compressed_start_ms, compressed_end_ms, original_start_ms)
            )
            compressed_start_ms = compressed_end_ms

        output_segments: list[TranscribedSegment] = []
        interval_idx = 0
        current_words: list[TranscribedWord] = []

        def append_current_segment():
            """Append accumulated words as one original-timeline segment."""
            nonlocal current_words
            if not current_words:
                return
            output_segments.append(
                TranscribedSegment(
                    id=len(output_segments),
                    seek=0,
                    start=current_words[0].start,
                    end=current_words[-1].end,
                    text="".join(word.text for word in current_words),
                    words=current_words,
                )
            )
            current_words = []

        for segment in segments:
            if not segment.words:
                raise TranscriptionAlignmentError(
                    "MLX-Audio VAD cannot restore a segment without word timings."
                )
            for word in segment.words:
                word_start_ms = round(word.start * 1000)
                word_end_ms = round(word.end * 1000)
                word_midpoint_ms = (word_start_ms + word_end_ms) / 2
                while (
                    interval_idx < len(compressed_intervals) - 1
                    and word_midpoint_ms > compressed_intervals[interval_idx][1]
                ):
                    append_current_segment()
                    interval_idx += 1

                (
                    interval_compressed_start_ms,
                    interval_compressed_end_ms,
                    interval_original_start_ms,
                ) = compressed_intervals[interval_idx]
                interval_duration_ms = (
                    interval_compressed_end_ms - interval_compressed_start_ms
                )
                mapped_start_ms = interval_original_start_ms + max(
                    0,
                    min(
                        word_start_ms - interval_compressed_start_ms,
                        interval_duration_ms,
                    ),
                )
                mapped_end_ms = interval_original_start_ms + max(
                    0,
                    min(
                        word_end_ms - interval_compressed_start_ms, interval_duration_ms
                    ),
                )
                current_words.append(
                    word.model_copy(
                        update={
                            "start": mapped_start_ms / 1000,
                            "end": mapped_end_ms / 1000,
                        }
                    )
                )

        append_current_segment()
        return output_segments

    @staticmethod
    def _get_offset_core_segments(
        segments: Sequence[TranscribedSegment],
        offset_seconds: float,
        core_start_seconds: float,
        core_end_seconds: float,
        start_id: int,
    ) -> list[TranscribedSegment]:
        """Offset chunk-local segments and keep only core-window segments.

        Arguments:
            segments: chunk-local timestamped segments
            offset_seconds: offset from chunk-local time to original audio time
            core_start_seconds: inclusive start of non-overlap core
            core_end_seconds: exclusive end of non-overlap core
            start_id: first segment id to assign
        Returns:
            offset segments containing only words assigned to the core window
        Raises:
            TranscriptionAlignmentError: if an aligned segment lacks word timings
        """
        offset_segments = []
        for segment in segments:
            if not segment.words:
                raise TranscriptionAlignmentError(
                    "MLX-Audio chunk cannot trim an aligned segment without word "
                    "timings."
                )
            words = []
            for word in segment.words:
                global_start = word.start + offset_seconds
                global_end = word.end + offset_seconds
                midpoint = (global_start + global_end) / 2
                if midpoint < core_start_seconds or midpoint >= core_end_seconds:
                    continue
                words.append(
                    word.model_copy(
                        update={
                            "start": max(global_start, core_start_seconds),
                            "end": min(global_end, core_end_seconds),
                        }
                    )
                )
            if not words:
                continue
            offset_segments.append(
                segment.model_copy(
                    update={
                        "id": start_id + len(offset_segments),
                        "start": words[0].start,
                        "end": words[-1].end,
                        "text": "".join(word.text for word in words),
                        "words": words,
                    }
                )
            )
        return offset_segments
