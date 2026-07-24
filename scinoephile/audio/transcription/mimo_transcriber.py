#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Transcribes audio using MiMo ASR plus forced timestamp alignment."""

from __future__ import annotations

import hashlib
import json
import platform
from collections.abc import Mapping, Sequence
from logging import getLogger
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from scinoephile.common.file import get_temp_file_path
from scinoephile.common.validation import val_output_dir_path
from scinoephile.core import Language

from .forced_alignment import (
    CTC_MODEL_NAME,
    TranscriptionAlignmentError,
    align_mimo_transcription,
)
from .mimo_inference import MimoInferenceResult, transcribe_with_mimo
from .transcribed_segment import TranscribedSegment
from .transcribed_word import TranscribedWord

__all__ = [
    "MimoInferenceError",
    "MimoTranscriptEmptyError",
    "MimoTranscriber",
    "MimoTranscriptionError",
]

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = getLogger(__name__)

_LOW_INFORMATION_CHARACTERS = frozenset("啊呀吖哦噢嗯嘶")
"""Standalone vocalizations rejected as unusable transcripts."""

_VAD_CACHE_VERSION = "silero-v1"
"""Cache identity for the current MiMo VAD implementation."""

_VAD_MIN_SILENCE_DURATION_SECONDS = 1.0
"""Minimum silence separating MiMo speech intervals."""

_VAD_PADDING_SECONDS = 0.5
"""Context retained around each MiMo speech interval."""

_VAD_SAMPLE_RATE = 16000
"""Sample rate expected by the Silero VAD model."""

_MIMO_MODEL_NAME = "mlx-community/MiMo-V2.5-ASR-MLX"
"""Default MLX MiMo model."""

_MIMO_LANGUAGE_CODES = {
    Language.eng: "en",
    Language.yue_hans: "zh",
    Language.yue_hant: "zh",
    Language.zho_hans: "zh",
    Language.zho_hant: "zh",
}
"""Maps Scinoephile languages to MiMo ASR language codes."""


class MimoTranscriptionError(RuntimeError):
    """Raised when MiMo transcription cannot produce timestamped output."""


class MimoTranscriptEmptyError(MimoTranscriptionError):
    """Raised when MiMo returns no transcript text."""


class MimoInferenceError(MimoTranscriptionError):
    """Raised when direct MiMo inference fails or returns malformed output."""


class MimoTranscriber:
    """Transcribes audio using MiMo ASR and a timestamp alignment stage."""

    def __init__(
        self,
        model_name: str = _MIMO_MODEL_NAME,
        language: Language = Language.yue_hant,
        max_tokens: int | None = None,
        chunk_duration_seconds: float | None = None,
        chunk_overlap_seconds: float = 1.0,
        cache_dir_path: Path | None = None,
        use_demucs: bool = False,
        use_vad: bool = False,
        retry_without_vad: bool = False,
    ):
        """Initialize.

        Arguments:
            model_name: MiMo ASR model name or local model path
            language: language to transcribe
            max_tokens: optional maximum number of MiMo text tokens to generate
            chunk_duration_seconds: optional chunk duration for MiMo inference
            chunk_overlap_seconds: context overlap applied to each MiMo chunk
            cache_dir_path: directory in which to cache
            use_demucs: whether Demucs preprocessing was applied
            use_vad: whether to remove non-speech audio using Silero VAD
            retry_without_vad: whether to retry unfiltered audio after VAD failure
        Raises:
            ValueError: if the language or numeric configuration is invalid
        """
        self.model_name = model_name
        self.language = language
        try:
            self.mimo_language_code = _MIMO_LANGUAGE_CODES[self.language]
        except (KeyError, ValueError) as exc:
            raise ValueError(
                f"{language} is not supported by MiMo transcription"
            ) from exc
        self.max_tokens = max_tokens
        self.chunk_duration_seconds = chunk_duration_seconds
        self.chunk_overlap_seconds = chunk_overlap_seconds
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("MiMo max tokens must be positive.")
        if self.chunk_duration_seconds is not None and self.chunk_duration_seconds <= 0:
            raise ValueError("MiMo chunk duration must be positive.")
        if self.chunk_overlap_seconds < 0:
            raise ValueError("MiMo chunk overlap must be non-negative.")
        self.use_demucs = use_demucs
        self.use_vad = use_vad
        self.retry_without_vad = retry_without_vad
        if self.retry_without_vad and not self.use_vad:
            raise ValueError("MiMo cannot retry without VAD when VAD is disabled.")
        self.cache_dir_path = None
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)

    def __call__(
        self,
        audio: AudioSegment,
        *,
        cache_audio: AudioSegment | None = None,
        use_cache: bool = True,
    ) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: audio to transcribe
            cache_audio: optional audio used for cache-key generation
            use_cache: whether to return a cached transcription when available
        Returns:
            transcription, split into timestamped segments
        """
        return self.transcribe(
            audio,
            cache_audio=cache_audio,
            use_cache=use_cache,
        )

    def get_cached_transcription(
        self, cache_audio: AudioSegment
    ) -> list[TranscribedSegment] | None:
        """Get cached transcription for audio if available.

        Arguments:
            cache_audio: audio used for cache-key generation
        Returns:
            cached transcription, if present
        """
        cache_path = self._get_cache_path(cache_audio)
        if cache_path is None or not cache_path.exists():
            return None

        logger.info(f"Loaded MiMo transcription from cache: {cache_path}")
        with cache_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        if not isinstance(payload, Mapping):
            raise MimoInferenceError(f"Malformed MiMo cache payload: {cache_path}")
        raw_segments = payload.get("segments")
        if not isinstance(raw_segments, list):
            raise MimoInferenceError(f"Malformed MiMo cache payload: {cache_path}")
        segments = [TranscribedSegment.model_validate(s) for s in raw_segments]
        cache_path.touch()
        return segments

    def transcribe(
        self,
        audio: AudioSegment,
        *,
        cache_audio: AudioSegment | None = None,
        use_cache: bool = True,
    ) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: audio to transcribe
            cache_audio: optional audio used for cache-key generation
            use_cache: whether to return a cached transcription when available
        Returns:
            transcription, split into timestamped segments
        """
        cache_audio = cache_audio or audio
        if (
            use_cache
            and (segments := self.get_cached_transcription(cache_audio)) is not None
        ):
            return segments

        segments = self._transcribe_uncached(audio)

        cache_path = self._get_cache_path(cache_audio)
        if cache_path is not None:
            with cache_path.open("w", encoding="utf-8") as file:
                json.dump(
                    self._get_cache_payload(segments),
                    file,
                    ensure_ascii=False,
                    indent=2,
                )
            logger.info(f"Saved MiMo transcription to cache: {cache_path}")

        return segments

    def _get_cache_path(self, audio: AudioSegment) -> Path | None:
        """Get cache path based on hash of audio data and MiMo configuration.

        Arguments:
            audio: audio used to derive the cache key
        Returns:
            path to cache file
        """
        if self.cache_dir_path is None:
            return None

        cache_hash = hashlib.sha256(audio.raw_data)
        cache_hash.update(b"\0")
        cache_hash.update(
            json.dumps(
                {
                    "audio_channels": audio.channels,
                    "audio_frame_rate": audio.frame_rate,
                    "audio_sample_width": audio.sample_width,
                    **self._get_cache_metadata(),
                },
                ensure_ascii=False,
                sort_keys=True,
            ).encode("utf-8")
        )
        return self.cache_dir_path / f"{cache_hash.hexdigest()}.json"

    def _get_cache_metadata(self) -> dict[str, object]:
        """Get metadata that identifies cached MiMo output.

        Returns:
            cache identity metadata
        """
        self._validate_platform()
        vad_version = None
        if self.use_vad:
            vad_version = _VAD_CACHE_VERSION
        return {
            "backend": "mimo",
            "model_name": self.model_name,
            "runtime": "mlx",
            "language": self.language.code,
            "mimo_language_code": self.mimo_language_code,
            "max_tokens": self.max_tokens,
            "chunk_duration_seconds": self.chunk_duration_seconds,
            "chunk_overlap_seconds": self.chunk_overlap_seconds,
            "aligner": "ctc",
            "aligner_model_name": CTC_MODEL_NAME,
            "use_demucs": self.use_demucs,
            "vad_version": vad_version,
            "retry_without_vad": self.retry_without_vad,
        }

    def _get_cache_payload(
        self, segments: Sequence[TranscribedSegment]
    ) -> dict[str, object]:
        """Get JSON-serializable MiMo cache payload.

        Arguments:
            segments: timestamped segments to cache
        Returns:
            cache payload
        """
        return {
            **self._get_cache_metadata(),
            "segments": [segment.model_dump() for segment in segments],
        }

    @staticmethod
    def _validate_platform():
        """Validate that direct MLX MiMo inference is supported."""
        if platform.system() == "Darwin" and platform.machine() in {"arm64", "aarch64"}:
            return
        raise MimoTranscriptionError(
            "MiMo support currently requires Apple Silicon MLX. "
            "CUDA support is not included in this initial implementation."
        )

    @staticmethod
    def _get_vad_speech_intervals(audio: AudioSegment) -> list[tuple[int, int]]:
        """Get padded speech intervals using Whisper's Silero VAD implementation.

        Arguments:
            audio: source audio
        Returns:
            speech start and end offsets in milliseconds
        Raises:
            MimoTranscriptionError: if Silero VAD is unavailable or fails
        """
        try:
            import torch  # noqa: PLC0415
            from whisper_timestamped.transcribe import (  # noqa: E501, PLC0415
                get_vad_segments,
            )
        except ImportError as exc:
            raise MimoTranscriptionError(
                "MiMo VAD requires the optional transcription dependencies."
            ) from exc

        normalized_audio = (
            audio.set_channels(1).set_frame_rate(_VAD_SAMPLE_RATE).set_sample_width(2)
        )
        samples = (
            np.array(
                normalized_audio.get_array_of_samples(),
                dtype=np.float32,
            )
            / np.iinfo(np.int16).max
        )
        audio_tensor = torch.from_numpy(samples)
        try:
            raw_intervals = get_vad_segments(
                audio_tensor,
                sample_rate=_VAD_SAMPLE_RATE,
                output_sample=False,
                min_silence_duration=_VAD_MIN_SILENCE_DURATION_SECONDS,
                dilatation=_VAD_PADDING_SECONDS,
                method="silero",
            )
        except (AssertionError, OSError, RuntimeError, ValueError) as exc:
            raise MimoTranscriptionError(f"Unable to run MiMo VAD: {exc}") from exc

        intervals = []
        for raw_interval in raw_intervals:
            start = raw_interval.get("start")
            end = raw_interval.get("end")
            if not isinstance(start, int | float) or not isinstance(end, int | float):
                raise MimoTranscriptionError("MiMo VAD returned malformed timestamps.")
            start_ms = max(0, round(float(start) * 1000))
            end_ms = min(len(audio), round(float(end) * 1000))
            if end_ms > start_ms:
                intervals.append((start_ms, end_ms))
        return intervals

    def _run_mimo(self, audio_path: Path) -> MimoInferenceResult:
        """Run MiMo directly in the current process.

        Arguments:
            audio_path: temporary WAV path to transcribe
        Returns:
            MiMo inference result
        Raises:
            MimoInferenceError: if direct inference fails
        """
        self._validate_platform()
        try:
            return transcribe_with_mimo(
                audio_path,
                model_name=self.model_name,
                language=self.mimo_language_code,
                max_tokens=self.max_tokens,
            )
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            raise MimoInferenceError(f"Unable to run MiMo inference: {exc}") from exc

    def _transcribe_audio_window(
        self,
        audio: AudioSegment,
    ) -> list[TranscribedSegment]:
        """Run MiMo transcription and timestamp alignment for one audio window.

        Arguments:
            audio: audio to transcribe
        Returns:
            timestamped transcription segments
        Raises:
            MimoTranscriptionError: if MiMo returns unusable text
            TranscriptionAlignmentError: if forced alignment fails
        """
        with get_temp_file_path(suffix=".wav") as temp_audio_path:
            audio.export(temp_audio_path, format="wav")
            inference_result = self._run_mimo(temp_audio_path)
            text = inference_result.text
            if not text.strip():
                raise MimoTranscriptEmptyError("MiMo returned empty transcript.")
            content_characters = {char for char in text if char.isalnum()}
            if content_characters and content_characters <= _LOW_INFORMATION_CHARACTERS:
                raise MimoTranscriptionError(
                    f"MiMo returned only low-information vocalizations: {text!r}"
                )
            return align_mimo_transcription(
                temp_audio_path,
                text,
                duration_seconds=inference_result.duration_seconds,
            )

    def _transcribe_chunked_audio(
        self,
        audio: AudioSegment,
    ) -> list[TranscribedSegment]:
        """Run MiMo transcription over shorter overlapping chunks.

        Arguments:
            audio: audio to transcribe
        Returns:
            timestamped transcription segments
        """
        assert self.chunk_duration_seconds is not None
        chunk_duration_ms = int(round(self.chunk_duration_seconds * 1000))
        chunk_overlap_ms = int(round(self.chunk_overlap_seconds * 1000))
        segments: list[TranscribedSegment] = []

        core_start_ms = 0
        while core_start_ms < len(audio):
            core_end_ms = min(len(audio), core_start_ms + chunk_duration_ms)
            window_start_ms = max(0, core_start_ms - chunk_overlap_ms)
            window_end_ms = min(len(audio), core_end_ms + chunk_overlap_ms)
            window_audio = audio[window_start_ms:window_end_ms]
            try:
                window_segments = self._transcribe_audio_window(window_audio)
            except MimoTranscriptEmptyError:
                logger.info(
                    f"Skipping empty MiMo audio window "
                    f"{window_start_ms / 1000:.2f}s-"
                    f"{window_end_ms / 1000:.2f}s"
                )
            else:
                segments.extend(
                    self._get_offset_core_segments(
                        window_segments,
                        offset_seconds=window_start_ms / 1000,
                        core_start_seconds=core_start_ms / 1000,
                        core_end_seconds=core_end_ms / 1000,
                        start_id=len(segments),
                    )
                )
            core_start_ms = core_end_ms

        if not segments:
            raise MimoTranscriptEmptyError(
                "MiMo returned no transcript across audio chunks."
            )
        return segments

    def _transcribe_uncached(self, audio: AudioSegment) -> list[TranscribedSegment]:
        """Run MiMo transcription and timestamp alignment without cache lookup.

        Arguments:
            audio: audio to transcribe
        Returns:
            timestamped transcription segments
        Raises:
            MimoTranscriptionError: if MiMo returns unusable text
            TranscriptionAlignmentError: if forced alignment fails
        """
        if self.use_vad:
            try:
                return self._transcribe_vad_audio(audio)
            except (MimoTranscriptionError, TranscriptionAlignmentError) as exc:
                if not self.retry_without_vad:
                    raise
                logger.info(
                    f"Retrying MiMo without VAD after the VAD attempt failed: {exc}"
                )
        return self._transcribe_unfiltered_audio(audio)

    def _transcribe_unfiltered_audio(
        self,
        audio: AudioSegment,
    ) -> list[TranscribedSegment]:
        """Transcribe audio without applying VAD.

        Arguments:
            audio: audio to transcribe
        Returns:
            timestamped transcription segments
        """
        if self.chunk_duration_seconds is None:
            return self._transcribe_audio_window(audio)
        if len(audio) <= int(round(self.chunk_duration_seconds * 1000)):
            return self._transcribe_audio_window(audio)
        return self._transcribe_chunked_audio(audio)

    def _transcribe_vad_audio(
        self,
        audio: AudioSegment,
    ) -> list[TranscribedSegment]:
        """Transcribe detected speech and restore original-audio timestamps.

        Arguments:
            audio: original audio containing speech and non-speech regions
        Returns:
            timestamped transcription segments on the original audio timeline
        Raises:
            MimoTranscriptEmptyError: if VAD finds no speech
        """
        speech_intervals = self._get_vad_speech_intervals(audio)
        if not speech_intervals:
            raise MimoTranscriptEmptyError("MiMo VAD found no speech.")

        logger.info(
            f"MiMo VAD retained {len(speech_intervals)} speech interval(s) "
            f"from {len(audio) / 1000:.2f}s of audio"
        )
        speech_audio = audio[0:0]
        for start_ms, end_ms in speech_intervals:
            speech_audio += audio[start_ms:end_ms]

        speech_segments = self._transcribe_unfiltered_audio(speech_audio)
        return self._restore_vad_timestamps(speech_segments, speech_intervals)

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
        compressed_intervals = []
        compressed_start_ms = 0
        for original_start_ms, original_end_ms in speech_intervals:
            duration_ms = original_end_ms - original_start_ms
            compressed_end_ms = compressed_start_ms + duration_ms
            compressed_intervals.append(
                (
                    compressed_start_ms,
                    compressed_end_ms,
                    original_start_ms,
                    original_end_ms,
                )
            )
            compressed_start_ms = compressed_end_ms

        output_segments: list[TranscribedSegment] = []
        current_interval_idx = -1
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
                    "MiMo VAD cannot restore a segment without word timings."
                )
            for word in segment.words:
                word_start_ms = round(word.start * 1000)
                word_end_ms = round(word.end * 1000)
                word_midpoint_ms = (word_start_ms + word_end_ms) / 2
                interval_idx = len(compressed_intervals) - 1
                for candidate_idx, compressed_interval in enumerate(
                    compressed_intervals
                ):
                    if word_midpoint_ms <= compressed_interval[1]:
                        interval_idx = candidate_idx
                        break

                if interval_idx != current_interval_idx:
                    append_current_segment()
                    current_interval_idx = interval_idx

                (
                    interval_compressed_start_ms,
                    interval_compressed_end_ms,
                    interval_original_start_ms,
                    interval_original_end_ms,
                ) = compressed_intervals[interval_idx]
                mapped_start_ms = interval_original_start_ms + max(
                    0,
                    min(
                        word_start_ms - interval_compressed_start_ms,
                        interval_compressed_end_ms - interval_compressed_start_ms,
                    ),
                )
                mapped_end_ms = interval_original_start_ms + max(
                    0,
                    min(
                        word_end_ms - interval_compressed_start_ms,
                        interval_compressed_end_ms - interval_compressed_start_ms,
                    ),
                )
                mapped_end_ms = min(mapped_end_ms, interval_original_end_ms)
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
        *,
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
                    "MiMo chunk cannot trim an aligned segment without word timings."
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
                            "start": global_start,
                            "end": global_end,
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
