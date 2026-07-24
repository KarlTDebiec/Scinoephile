#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Transcribes audio through MLX-Audio plus forced timestamp alignment."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING

import numpy as np

from scinoephile.common.file import get_temp_file_path
from scinoephile.common.validation import val_output_dir_path
from scinoephile.core import Language
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.paths import get_runtime_cache_dir_path

from .demucs_separator import DemucsSeparator
from .forced_alignment import (
    CTC_MODEL_NAME,
    TranscriptionAlignmentError,
    align_transcription,
)
from .mlx_audio_inference import MlxAudioInferenceResult, transcribe_with_mlx_audio
from .transcribed_segment import TranscribedSegment
from .transcribed_word import TranscribedWord

__all__ = [
    "MIMO_MODEL_NAME",
    "MlxAudioInferenceError",
    "MlxAudioModelProfile",
    "MlxAudioTranscriptEmptyError",
    "MlxAudioTranscriber",
    "MlxAudioTranscriptionError",
    "QWEN3_ASR_MODEL_NAME",
    "get_mlx_audio_model_profile",
]

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = getLogger(__name__)

_LOW_INFORMATION_CHARACTERS = frozenset("啊呀吖哦噢嗯嘶")
"""Standalone vocalizations rejected as unusable transcripts."""

_VAD_CACHE_VERSION = "silero-v1"
"""Cache identity for the current MLX-Audio VAD implementation."""

_VAD_MIN_SILENCE_DURATION_SECONDS = 1.0
"""Minimum silence separating MLX-Audio speech intervals."""

_VAD_PADDING_SECONDS = 0.5
"""Context retained around each MLX-Audio speech interval."""

_VAD_SAMPLE_RATE = 16000
"""Sample rate expected by the Silero VAD model."""

MIMO_MODEL_NAME = "mlx-community/MiMo-V2.5-ASR-MLX"
"""Default MLX MiMo model."""

QWEN3_ASR_MODEL_NAME = "mlx-community/Qwen3-ASR-0.6B-8bit"
"""Default MLX Qwen3-ASR model."""


@dataclass(frozen=True, slots=True)
class MlxAudioModelProfile:
    """Model-specific configuration for an MLX-Audio STT family."""

    family_name: str
    """Stable model-family name used in cache metadata."""
    default_model_name: str
    """Default Hugging Face model identifier for the family."""
    model_name_markers: tuple[str, ...]
    """Case-insensitive substrings identifying the model family."""
    language_identifiers: Mapping[Language, str]
    """Model-specific language identifiers keyed by Scinoephile language."""

    def get_language_identifier(self, language: Language) -> str:
        """Get the model-specific identifier for a language.

        Arguments:
            language: transcription language
        Returns:
            model-specific language identifier
        Raises:
            ValueError: if the model family does not support the language
        """
        try:
            return self.language_identifiers[language]
        except KeyError as exc:
            raise ValueError(
                f"{language} is not supported by MLX-Audio "
                f"{self.family_name} transcription"
            ) from exc


_MLX_AUDIO_MODEL_PROFILES = (
    MlxAudioModelProfile(
        family_name="mimo",
        default_model_name=MIMO_MODEL_NAME,
        model_name_markers=("mimo-v2.5-asr",),
        language_identifiers=MappingProxyType(
            {
                Language.eng: "en",
                Language.yue_hans: "zh",
                Language.yue_hant: "zh",
                Language.zho_hans: "zh",
                Language.zho_hant: "zh",
            }
        ),
    ),
    MlxAudioModelProfile(
        family_name="qwen3-asr",
        default_model_name=QWEN3_ASR_MODEL_NAME,
        model_name_markers=("qwen3-asr",),
        language_identifiers=MappingProxyType(
            {
                Language.eng: "English",
                Language.yue_hans: "Cantonese",
                Language.yue_hant: "Cantonese",
                Language.zho_hans: "Chinese",
                Language.zho_hant: "Chinese",
            }
        ),
    ),
)
"""Supported MLX-Audio model profiles."""


def get_mlx_audio_model_profile(model_name: str) -> MlxAudioModelProfile:
    """Get the supported model profile matching an MLX-Audio model name.

    Arguments:
        model_name: Hugging Face model identifier or local model path
    Returns:
        matching model profile
    Raises:
        ValueError: if the model family has not been integrated and tested
    """
    lowered_model_name = model_name.lower()
    for profile in _MLX_AUDIO_MODEL_PROFILES:
        if any(marker in lowered_model_name for marker in profile.model_name_markers):
            return profile
    supported_families = ", ".join(
        profile.family_name for profile in _MLX_AUDIO_MODEL_PROFILES
    )
    raise ValueError(
        f"Unsupported MLX-Audio model {model_name!r}; supported families: "
        f"{supported_families}."
    )


class MlxAudioTranscriptionError(ScinoephileError):
    """Raised when MLX-Audio cannot produce timestamped transcription output."""


class MlxAudioTranscriptEmptyError(MlxAudioTranscriptionError):
    """Raised when MLX-Audio returns no transcript text."""


class MlxAudioInferenceError(MlxAudioTranscriptionError):
    """Raised when direct MLX-Audio inference fails or returns malformed output."""


class MlxAudioTranscriber:
    """Transcribes audio using MLX-Audio and a timestamp alignment stage."""

    def __init__(
        self,
        model_name: str = MIMO_MODEL_NAME,
        language: Language = Language.yue_hant,
        max_tokens: int | None = None,
        chunk_duration_seconds: float | None = None,
        chunk_overlap_seconds: float = 1.0,
        cache_dir_path: Path | None = None,
        use_demucs: bool = False,
        use_vad: bool = False,
        retry_without_demucs: bool = False,
        retry_without_vad: bool = False,
    ):
        """Initialize.

        Arguments:
            model_name: supported MLX-Audio model name or local model path
            language: language to transcribe
            max_tokens: optional maximum number of text tokens to generate
            chunk_duration_seconds: optional chunk duration for inference
            chunk_overlap_seconds: context overlap applied to each chunk
            cache_dir_path: directory in which to cache
            use_demucs: whether to apply Demucs vocal separation
            use_vad: whether to remove non-speech audio using Silero VAD
            retry_without_demucs: whether to retry original audio after Demucs
            retry_without_vad: whether to retry unfiltered audio after VAD failure
        Raises:
            MlxAudioTranscriptionError: if the platform does not support MLX-Audio
            ValueError: if the language or numeric configuration is invalid
        """
        self._validate_platform()
        self.model_name = model_name
        self.model_profile = get_mlx_audio_model_profile(model_name)
        self.language = language
        self.mlx_audio_language = self.model_profile.get_language_identifier(language)
        self.max_tokens = max_tokens
        self.chunk_duration_seconds = chunk_duration_seconds
        self.chunk_overlap_seconds = chunk_overlap_seconds
        if self.max_tokens is not None and self.max_tokens <= 0:
            raise ValueError("MLX-Audio max tokens must be positive.")
        if self.chunk_duration_seconds is not None and self.chunk_duration_seconds <= 0:
            raise ValueError("MLX-Audio chunk duration must be positive.")
        if self.chunk_overlap_seconds < 0:
            raise ValueError("MLX-Audio chunk overlap must be non-negative.")
        self.use_demucs = use_demucs
        self.use_vad = use_vad
        self.retry_without_demucs = retry_without_demucs
        self.retry_without_vad = retry_without_vad
        if self.retry_without_demucs and not self.use_demucs:
            raise ValueError(
                "MLX-Audio cannot retry without Demucs when Demucs is disabled."
            )
        if self.retry_without_vad and not self.use_vad:
            raise ValueError("MLX-Audio cannot retry without VAD when VAD is disabled.")
        self.demucs_separator = None
        if self.use_demucs:
            self.demucs_separator = DemucsSeparator(
                cache_dir_path=get_runtime_cache_dir_path("demucs")
            )
        self.cache_dir_path = None
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)

    def __call__(
        self,
        audio: AudioSegment,
        *,
        cache_audio: AudioSegment | None = None,
        is_usable: Callable[[list[TranscribedSegment]], bool] | None = None,
        use_cache: bool = True,
    ) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: audio to transcribe
            cache_audio: optional audio used for cache-key generation
            is_usable: optional callback used to reject output and trigger retries
            use_cache: whether to return a cached transcription when available
        Returns:
            transcription, split into timestamped segments
        """
        return self.transcribe(
            audio,
            cache_audio=cache_audio,
            is_usable=is_usable,
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
        return self._get_cached_transcription(
            cache_audio,
            use_demucs=self.use_demucs,
            use_vad=self.use_vad,
        )

    def transcribe(
        self,
        audio: AudioSegment,
        *,
        cache_audio: AudioSegment | None = None,
        is_usable: Callable[[list[TranscribedSegment]], bool] | None = None,
        use_cache: bool = True,
    ) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: audio to transcribe
            cache_audio: optional audio used for cache-key generation
            is_usable: optional callback used to reject output and trigger retries
            use_cache: whether to return a cached transcription when available
        Returns:
            transcription, split into timestamped segments
        """
        cache_audio = cache_audio or audio
        attempts = self._get_attempt_configurations()
        cached_segments, rejected_attempts, last_error = self._get_cached_attempt(
            cache_audio,
            attempts=attempts,
            is_usable=is_usable,
            use_cache=use_cache,
        )
        if cached_segments is not None:
            return cached_segments
        return self._transcribe_attempts(
            audio,
            cache_audio=cache_audio,
            attempts=attempts,
            rejected_attempts=rejected_attempts,
            is_usable=is_usable,
            last_error=last_error,
        )

    def _get_attempt_configurations(self) -> tuple[tuple[bool, bool], ...]:
        """Get Demucs and VAD configurations in retry order.

        Returns:
            tuples of whether to use Demucs and VAD for each attempt
        """
        attempts = [(self.use_demucs, self.use_vad)]
        if self.retry_without_vad:
            attempts.append((self.use_demucs, False))
        if self.retry_without_demucs:
            attempts.append((False, self.use_vad))
            if self.retry_without_vad:
                attempts.append((False, False))
        return tuple(dict.fromkeys(attempts))

    def _get_cache_path(
        self,
        audio: AudioSegment,
        *,
        use_demucs: bool | None = None,
        use_vad: bool | None = None,
    ) -> Path | None:
        """Get cache path based on hash of audio data and MLX-Audio configuration.

        Arguments:
            audio: audio used to derive the cache key
            use_demucs: whether Demucs preprocessing identifies the cache entry
            use_vad: whether VAD preprocessing identifies the cache entry
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
                    **self._get_cache_metadata(
                        use_demucs=use_demucs,
                        use_vad=use_vad,
                    ),
                },
                ensure_ascii=False,
                sort_keys=True,
            ).encode("utf-8")
        )
        return self.cache_dir_path / f"{cache_hash.hexdigest()}.json"

    def _get_cache_metadata(
        self,
        *,
        use_demucs: bool | None = None,
        use_vad: bool | None = None,
    ) -> dict[str, object]:
        """Get metadata that identifies cached MLX-Audio output.

        Arguments:
            use_demucs: whether Demucs preprocessing identifies the cache entry
            use_vad: whether VAD preprocessing identifies the cache entry
        Returns:
            cache identity metadata
        """
        if use_demucs is None:
            use_demucs = self.use_demucs
        if use_vad is None:
            use_vad = self.use_vad
        vad_version = None
        if use_vad:
            vad_version = _VAD_CACHE_VERSION
        return {
            "backend": "mlx-audio",
            "model_family": self.model_profile.family_name,
            "model_name": self.model_name,
            "runtime": "mlx",
            "language": self.language.code,
            "mlx_audio_language": self.mlx_audio_language,
            "max_tokens": self.max_tokens,
            "chunk_duration_seconds": self.chunk_duration_seconds,
            "chunk_overlap_seconds": self.chunk_overlap_seconds,
            "aligner": "ctc",
            "aligner_model_name": CTC_MODEL_NAME,
            "use_demucs": use_demucs,
            "vad_version": vad_version,
        }

    def _get_cache_payload(
        self,
        segments: Sequence[TranscribedSegment],
        *,
        use_demucs: bool | None = None,
        use_vad: bool | None = None,
    ) -> dict[str, object]:
        """Get JSON-serializable MLX-Audio cache payload.

        Arguments:
            segments: timestamped segments to cache
            use_demucs: whether Demucs preprocessing identifies the cache entry
            use_vad: whether VAD preprocessing identifies the cache entry
        Returns:
            cache payload
        """
        return {
            **self._get_cache_metadata(
                use_demucs=use_demucs,
                use_vad=use_vad,
            ),
            "segments": [segment.model_dump() for segment in segments],
        }

    def _get_cached_attempt(
        self,
        cache_audio: AudioSegment,
        *,
        attempts: Sequence[tuple[bool, bool]],
        is_usable: Callable[[list[TranscribedSegment]], bool] | None,
        use_cache: bool,
    ) -> tuple[
        list[TranscribedSegment] | None,
        set[tuple[bool, bool]],
        Exception | None,
    ]:
        """Find a usable cached attempt and identify rejected configurations.

        Arguments:
            cache_audio: audio used for cache-key generation
            attempts: Demucs and VAD configurations in retry order
            is_usable: optional callback used to reject cached output
            use_cache: whether to inspect cached transcriptions
        Returns:
            usable cached segments, rejected configurations, and last cache error
        """
        rejected_attempts: set[tuple[bool, bool]] = set()
        last_error: Exception | None = None
        if not use_cache:
            return None, rejected_attempts, last_error

        for use_demucs, use_vad in attempts:
            try:
                segments = self._get_cached_transcription(
                    cache_audio,
                    use_demucs=use_demucs,
                    use_vad=use_vad,
                )
            except (MlxAudioTranscriptionError, TranscriptionAlignmentError) as exc:
                logger.warning(f"Unable to read MLX-Audio transcription cache: {exc}")
                last_error = exc
                continue
            if segments is None:
                continue
            if is_usable is None or is_usable(segments):
                return segments, rejected_attempts, last_error
            rejected_attempts.add((use_demucs, use_vad))
        return None, rejected_attempts, last_error

    def _get_cached_transcription(
        self,
        cache_audio: AudioSegment,
        *,
        use_demucs: bool,
        use_vad: bool,
    ) -> list[TranscribedSegment] | None:
        """Get cached transcription for one preprocessing configuration.

        Arguments:
            cache_audio: audio used for cache-key generation
            use_demucs: whether Demucs preprocessing identifies the cache entry
            use_vad: whether VAD preprocessing identifies the cache entry
        Returns:
            cached transcription, if present
        """
        cache_path = self._get_cache_path(
            cache_audio,
            use_demucs=use_demucs,
            use_vad=use_vad,
        )
        if cache_path is None or not cache_path.exists():
            return None

        logger.info(f"Loaded MLX-Audio transcription from cache: {cache_path}")
        with cache_path.open("r", encoding="utf-8") as file:
            payload = json.load(file)
        if not isinstance(payload, Mapping):
            raise MlxAudioInferenceError(
                f"Malformed MLX-Audio cache payload: {cache_path}"
            )
        raw_segments = payload.get("segments")
        if not isinstance(raw_segments, list):
            raise MlxAudioInferenceError(
                f"Malformed MLX-Audio cache payload: {cache_path}"
            )
        segments = [TranscribedSegment.model_validate(s) for s in raw_segments]
        cache_path.touch()
        return segments

    @staticmethod
    def _validate_platform():
        """Validate that direct MLX-Audio inference is supported."""
        machine = platform.machine()
        if sys.platform == "darwin" and machine == "arm64":
            return
        raise MlxAudioTranscriptionError(
            "MLX-Audio support requires macOS on Apple Silicon "
            f"(detected sys.platform={sys.platform!r}, "
            f"platform.machine()={machine!r}). "
            "CUDA support is not included."
        )

    @staticmethod
    def _get_vad_speech_intervals(audio: AudioSegment) -> list[tuple[int, int]]:
        """Get padded speech intervals using Whisper's Silero VAD implementation.

        Arguments:
            audio: source audio
        Returns:
            speech start and end offsets in milliseconds
        Raises:
            MlxAudioTranscriptionError: if Silero VAD is unavailable or fails
        """
        try:
            import torch  # noqa: PLC0415
            from whisper_timestamped.transcribe import (  # noqa: E501, PLC0415
                get_vad_segments,
            )
        except ImportError as exc:
            raise MlxAudioTranscriptionError(
                "MLX-Audio VAD requires the optional transcription dependencies."
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
            raise MlxAudioTranscriptionError(
                f"Unable to run MLX-Audio VAD: {exc}"
            ) from exc

        intervals = []
        for raw_interval in raw_intervals:
            start = raw_interval.get("start")
            end = raw_interval.get("end")
            if not isinstance(start, int | float) or not isinstance(end, int | float):
                raise MlxAudioTranscriptionError(
                    "MLX-Audio VAD returned malformed timestamps."
                )
            start_ms = max(0, round(float(start) * 1000))
            end_ms = min(len(audio), round(float(end) * 1000))
            if end_ms > start_ms:
                intervals.append((start_ms, end_ms))
        return intervals

    def _run_mlx_audio(self, audio_path: Path) -> MlxAudioInferenceResult:
        """Run MLX-Audio directly in the current process.

        Arguments:
            audio_path: temporary WAV path to transcribe
        Returns:
            MLX-Audio inference result
        Raises:
            MlxAudioInferenceError: if direct inference fails
        """
        try:
            return transcribe_with_mlx_audio(
                audio_path,
                model_name=self.model_name,
                language=self.mlx_audio_language,
                max_tokens=self.max_tokens,
            )
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            raise MlxAudioInferenceError(
                f"Unable to run MLX-Audio inference: {exc}"
            ) from exc

    def _transcribe_attempts(
        self,
        audio: AudioSegment,
        *,
        cache_audio: AudioSegment,
        attempts: Sequence[tuple[bool, bool]],
        rejected_attempts: set[tuple[bool, bool]],
        is_usable: Callable[[list[TranscribedSegment]], bool] | None,
        last_error: Exception | None,
    ) -> list[TranscribedSegment]:
        """Run uncached MLX-Audio attempts in preprocessing retry order.

        Arguments:
            audio: original audio to transcribe
            cache_audio: audio used for cache-key generation
            attempts: Demucs and VAD configurations in retry order
            rejected_attempts: configurations with unusable cached output
            is_usable: optional callback used to reject output and trigger retries
            last_error: last error encountered while reading cached attempts
        Returns:
            first usable transcription, or an empty list when output was rejected
        """
        separated_audio = None
        separation_attempted = False
        for use_demucs, use_vad in attempts:
            if (use_demucs, use_vad) in rejected_attempts:
                continue

            transcription_audio = audio
            if use_demucs:
                if not separation_attempted:
                    separation_attempted = True
                    assert self.demucs_separator is not None
                    logger.info("Applying Demucs vocal separation before MLX-Audio")
                    try:
                        separated_audio = self.demucs_separator(audio)
                    except ScinoephileError as exc:
                        if not self.retry_without_demucs:
                            raise
                        logger.warning(
                            "Demucs separation failed; retrying MLX-Audio with "
                            f"original audio: {exc}"
                        )
                if separated_audio is None:
                    continue
                transcription_audio = separated_audio

            if not use_vad and self.use_vad:
                logger.info("Retrying MLX-Audio without VAD")
            try:
                segments = self._transcribe_uncached(
                    transcription_audio,
                    use_vad=use_vad,
                )
            except (
                AssertionError,
                ImportError,
                MlxAudioTranscriptionError,
                TranscriptionAlignmentError,
            ) as exc:
                logger.warning(f"MLX-Audio transcription attempt failed: {exc}")
                last_error = exc
                continue

            cache_path = self._get_cache_path(
                cache_audio,
                use_demucs=use_demucs,
                use_vad=use_vad,
            )
            if cache_path is not None:
                with cache_path.open("w", encoding="utf-8") as file:
                    json.dump(
                        self._get_cache_payload(
                            segments,
                            use_demucs=use_demucs,
                            use_vad=use_vad,
                        ),
                        file,
                        ensure_ascii=False,
                        indent=2,
                    )
                logger.info(f"Saved MLX-Audio transcription to cache: {cache_path}")
            if is_usable is None or is_usable(segments):
                return segments

        if last_error is not None:
            raise last_error
        return []

    def _transcribe_audio_window(
        self,
        audio: AudioSegment,
    ) -> list[TranscribedSegment]:
        """Run MLX-Audio transcription and timestamp alignment for one audio window.

        Arguments:
            audio: audio to transcribe
        Returns:
            timestamped transcription segments
        Raises:
            MlxAudioTranscriptionError: if MLX-Audio returns unusable text
            TranscriptionAlignmentError: if forced alignment fails
        """
        with get_temp_file_path(suffix=".wav") as temp_audio_path:
            audio.export(temp_audio_path, format="wav")
            inference_result = self._run_mlx_audio(temp_audio_path)
            text = inference_result.text
            if not text.strip():
                raise MlxAudioTranscriptEmptyError(
                    "MLX-Audio returned empty transcript."
                )
            content_characters = {char for char in text if char.isalnum()}
            if content_characters and content_characters <= _LOW_INFORMATION_CHARACTERS:
                raise MlxAudioTranscriptionError(
                    f"MLX-Audio returned only low-information vocalizations: {text!r}"
                )
            return align_transcription(
                temp_audio_path,
                text,
                duration_seconds=inference_result.duration_seconds,
            )

    def _transcribe_chunked_audio(
        self,
        audio: AudioSegment,
    ) -> list[TranscribedSegment]:
        """Run MLX-Audio transcription over shorter overlapping chunks.

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
            except MlxAudioTranscriptEmptyError:
                logger.info(
                    f"Skipping empty MLX-Audio audio window "
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
            raise MlxAudioTranscriptEmptyError(
                "MLX-Audio returned no transcript across audio chunks."
            )
        return segments

    def _transcribe_uncached(
        self,
        audio: AudioSegment,
        *,
        use_vad: bool,
    ) -> list[TranscribedSegment]:
        """Run MLX-Audio transcription and timestamp alignment without cache lookup.

        Arguments:
            audio: audio to transcribe
            use_vad: whether to remove non-speech audio before transcription
        Returns:
            timestamped transcription segments
        Raises:
            MlxAudioTranscriptionError: if MLX-Audio returns unusable text
            TranscriptionAlignmentError: if forced alignment fails
        """
        if use_vad:
            return self._transcribe_vad_audio(audio)
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
            MlxAudioTranscriptEmptyError: if VAD finds no speech
        """
        speech_intervals = self._get_vad_speech_intervals(audio)
        if not speech_intervals:
            raise MlxAudioTranscriptEmptyError("MLX-Audio VAD found no speech.")

        logger.info(
            f"MLX-Audio VAD retained {len(speech_intervals)} speech interval(s) "
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
                    "MLX-Audio VAD cannot restore a segment without word timings."
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
