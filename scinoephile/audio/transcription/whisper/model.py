#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Executable Whisper speech-to-text model."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from functools import cached_property
from logging import getLogger
from math import ceil
from pathlib import Path
from typing import TYPE_CHECKING, cast

from scinoephile.audio.transcription.exceptions import (
    TranscriptionEmptyError,
    TranscriptionRecognitionError,
)
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.core.dependencies.transcription import (
    import_huggingface_hub,
    import_whisper_timestamped,
)
from scinoephile.core.language import Language
from scinoephile.core.ml import get_huggingface_snapshot_dir_path, get_torch_device

from .model_spec import WhisperModelSpec
from .types import WhisperNativeResult

__all__ = ["WhisperModel"]

logger = getLogger(__name__)

_MAX_SAMPLE_LEN = 224
"""Maximum token budget supported by the configured Whisper models."""

_MAX_TOKENS_PER_SECOND = 16
"""Generous decode budget per second of source audio."""

_MIN_SAMPLE_LEN = 32
"""Minimum token budget for very short source audio."""

if TYPE_CHECKING:
    from pydub import AudioSegment
    from whisper import Whisper


class WhisperModel:
    """Configured executable Whisper speech-to-text model."""

    def __init__(
        self, spec: WhisperModelSpec, language: Language, device: str | None = None
    ):
        """Initialize.

        Arguments:
            spec: Whisper model specification
            language: language to transcribe
            device: Torch device, or None to select the available accelerator
        Raises:
            ValueError: if the model does not support the language
        """
        self.spec = spec
        """Whisper model specification."""

        try:
            language_code = spec.languages[language]
        except KeyError as exc:
            raise ValueError(
                f"{language} is not supported by Whisper model {spec.name}"
            ) from exc
        self.language_code = language_code
        """Whisper language code used for inference."""

        self._device = device
        """Explicit Torch device, or None to select one when first needed."""

    def __call__(
        self,
        audio_path: Path,
        *,
        vad: bool | list[tuple[float, float]],
        temperature: float | Sequence[float],
        condition_on_previous_text: bool,
        sample_len: int,
    ) -> list[TranscribedSegment]:
        """Recognize speech with Whisper Timestamped.

        Arguments:
            audio_path: audio file to transcribe
            vad: Whisper-compatible VAD configuration
            temperature: decoding temperature or fallback schedule
            condition_on_previous_text: whether to condition each decode window on
                the preceding window
            sample_len: maximum number of tokens decoded per window
        Returns:
            timestamped transcription segments
        Raises:
            AssertionError: if Whisper Timestamped alignment fails
            DependencyError: if Whisper dependencies are unavailable
            ValueError: if Whisper returns malformed output
        """
        whisper_timestamped = import_whisper_timestamped()
        result = whisper_timestamped.transcribe(
            self.model,
            str(audio_path),
            language=self.language_code,
            vad=vad,
            temperature=temperature,
            condition_on_previous_text=condition_on_previous_text,
            sample_len=sample_len,
        )

        if not isinstance(result, Mapping):
            raise ValueError("Whisper Timestamped returned malformed output.")
        segment_data = result.get("segments")
        if not isinstance(segment_data, Sequence) or isinstance(
            segment_data, str | bytes
        ):
            raise ValueError("Whisper Timestamped output contains malformed segments.")
        try:
            segments = [
                TranscribedSegment.model_validate(segment) for segment in segment_data
            ]
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Whisper Timestamped output contains malformed segments."
            ) from exc
        return segments

    @cached_property
    def device(self) -> str:
        """Get the Torch device used for inference.

        Raises:
            DependencyError: if Torch is unavailable
        """
        if self._device is None:
            self._device = get_torch_device()
        return self._device

    @cached_property
    def model(self) -> Whisper:
        """Load and get the configured Whisper model.

        Returns:
            loaded Whisper model
        Raises:
            DependencyError: if Whisper dependencies are unavailable
        """
        whisper_timestamped = import_whisper_timestamped()
        model_dir_path = get_huggingface_snapshot_dir_path(
            self.spec.name, self.spec.revision
        )
        try:
            return whisper_timestamped.load_model(
                str(model_dir_path), device=self.device
            )
        except FileNotFoundError:
            logger.warning(
                "Whisper model load failed due to a missing cache file; "
                "downloading the complete Hugging Face snapshot and retrying."
            )
            huggingface_hub = import_huggingface_hub()
            snapshot_download = cast(
                "Callable[..., str]", huggingface_hub.snapshot_download
            )
            model_dir_path = Path(
                snapshot_download(repo_id=self.spec.name, revision=self.spec.revision)
            )
            return whisper_timestamped.load_model(
                str(model_dir_path), device=self.device
            )

    def get_sample_len(self, audio: AudioSegment) -> int:
        """Get a bounded token budget for one Whisper decode.

        Whisper Timestamped retains decoder attention maps for word alignment.
        Repetitive decoding can otherwise run to the model-wide token limit even for
        a short clip, consuming excessive time and memory.

        Arguments:
            audio: audio to be transcribed
        Returns:
            maximum number of tokens Whisper may decode
        """
        duration_seconds = len(audio) / 1000
        return min(
            _MAX_SAMPLE_LEN,
            max(_MIN_SAMPLE_LEN, ceil(duration_seconds * _MAX_TOKENS_PER_SECOND)),
        )

    def transcribe_native(
        self,
        audio_path: Path,
        *,
        temperature: float | Sequence[float],
        condition_on_previous_text: bool,
        sample_len: int,
    ) -> WhisperNativeResult:
        """Recognize text using native Whisper without word timestamps.

        Arguments:
            audio_path: audio file to transcribe
            temperature: decoding temperature or fallback schedule
            condition_on_previous_text: whether to condition each decode window on
                the preceding window
            sample_len: maximum number of tokens decoded per window
        Returns:
            native recognition result
        Raises:
            DependencyError: if Whisper dependencies are unavailable
            TranscriptionEmptyError: if native Whisper returns empty text
            TranscriptionRecognitionError: if inference fails or returns malformed
                output
        """
        native_temperature: float | tuple[float, ...]
        if isinstance(temperature, int | float):
            native_temperature = float(temperature)
        else:
            native_temperature = tuple(temperature)
        try:
            result = self.model.transcribe(
                str(audio_path),
                language=self.language_code,
                temperature=native_temperature,
                condition_on_previous_text=condition_on_previous_text,
                sample_len=sample_len,
                word_timestamps=False,
                verbose=False,
            )
        except (
            AssertionError,
            ImportError,
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as exc:
            raise TranscriptionRecognitionError(
                f"Unable to run native Whisper fallback: {exc}"
            ) from exc
        if not isinstance(result, Mapping):
            raise TranscriptionRecognitionError(
                "Native Whisper fallback returned malformed output."
            )
        text = result.get("text")
        if not isinstance(text, str):
            raise TranscriptionRecognitionError(
                "Native Whisper fallback output is missing transcript text."
            )
        if not text.strip():
            raise TranscriptionEmptyError(
                "Native Whisper fallback returned empty transcript."
            )
        segment_data = result.get("segments")
        if (
            not isinstance(segment_data, Sequence)
            or isinstance(segment_data, str | bytes)
            or not segment_data
        ):
            raise TranscriptionRecognitionError(
                "Native Whisper fallback output contains malformed segments."
            )
        try:
            segments = [
                TranscribedSegment.model_validate(segment) for segment in segment_data
            ]
        except (TypeError, ValueError) as exc:
            raise TranscriptionRecognitionError(
                "Native Whisper fallback output contains malformed segments."
            ) from exc
        return WhisperNativeResult(text=text, segments=segments)
