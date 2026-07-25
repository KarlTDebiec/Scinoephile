#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Transcribes audio using Whisper."""

from __future__ import annotations

from collections.abc import Sequence
from logging import getLogger
from math import ceil
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from scinoephile.common.file import get_temp_file_path
from scinoephile.core.ml import get_torch_device

from .attempt import DemucsMode, TranscriptionAttempt, VADMode
from .exceptions import TranscriptionInferenceError
from .transcribed_segment import TranscribedSegment
from .transcriber import Transcriber

__all__ = ["WhisperTranscriber"]

_LOCAL_MODEL_PATH_PREFIXES = {"checkpoint", "checkpoints", "model", "models"}
_MAX_SAMPLE_LEN = 224
"""Maximum token budget supported by the configured Whisper models."""

_MAX_TOKENS_PER_SECOND = 16
"""Generous decode budget per second of source audio."""

_MIN_SAMPLE_LEN = 32
"""Minimum token budget for very short source audio."""

_TRANSCRIPTION_EXTRA_MESSAGE = (
    "Whisper transcription support requires optional transcription dependencies. "
    "Install scinoephile with the 'transcription' extra."
)

if TYPE_CHECKING:
    from pydub import AudioSegment

logger = getLogger(__name__)


class WhisperTranscriber(Transcriber):
    """Transcribes audio using Whisper."""

    backend_name = "whisper"
    """Stable backend name stored in cache metadata."""

    backend_label = "Whisper"
    """Human-readable backend name used in log messages."""

    _models: ClassVar[dict[tuple[str, str], Any]] = {}
    """Loaded models shared by model name and device within the current process."""

    def __init__(
        self,
        model_name: str = "khleeloo/whisper-large-v3-cantonese",
        language: str = "yue",
        demucs_mode: DemucsMode = DemucsMode.AUTO,
        vad_mode: VADMode = VADMode.AUTO,
        cache_dir_path: Path | None = None,
        demucs_cache_dir_path: Path | None = None,
        temperature: float | Sequence[float] = 0.0,
        condition_on_previous_text: bool = True,
    ):
        """Initialize.

        Arguments:
            model_name: name of Whisper model to use
            language: language code for transcription
            demucs_mode: Demucs preprocessing mode
            vad_mode: voice activity detection mode
            cache_dir_path: directory in which to cache
            demucs_cache_dir_path: directory in which to cache Demucs output
            temperature: decoding temperature or fallback schedule
            condition_on_previous_text: whether to condition each decoding window on
                the preceding window
        """
        self.model_name = model_name
        self._model: Any | None = None
        self.language = language
        self.temperature: float | Sequence[float] = temperature
        self.condition_on_previous_text = condition_on_previous_text
        super().__init__(
            cache_dir_path,
            demucs_cache_dir_path,
            demucs_mode,
            vad_mode,
        )

    @property
    def model(self) -> Any:
        """Get the cached Whisper model, loading it if needed.

        Returns:
            loaded Whisper model
        """
        if self._model is None:
            device = get_torch_device()
            model_key = (self.model_name, device)
            if model_key in self._models:
                self._model = self._models[model_key]
                return self._model

            whisper = self._get_whisper_module()
            try:
                self._model = whisper.load_model(self.model_name, device=device)
            except FileNotFoundError:
                if not self._model_name_is_huggingface_repo_id():
                    raise
                logger.warning(
                    "Whisper model load failed due to missing cache file; "
                    "re-downloading HuggingFace snapshot and retrying."
                )
                snapshot_download = self._get_snapshot_download()
                snapshot_download(repo_id=self.model_name)
                self._model = whisper.load_model(self.model_name, device=device)
            self._models[model_key] = self._model
        return self._model

    @staticmethod
    def _get_sample_len(audio: AudioSegment) -> int:
        """Get a bounded token budget for one Whisper decode.

        The timestamped Whisper implementation retains decoder attention maps for
        word alignment. Repetitive decoding can otherwise run to the model-wide
        token limit even for a very short clip, consuming excessive time and memory.

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

    def _model_name_is_huggingface_repo_id(self) -> bool:
        """Determine whether model name looks like a HuggingFace repo ID.

        Returns:
            whether the model name should be passed to HuggingFace Hub
        """
        model_path = Path(self.model_name)
        model_path_parts = model_path.parts
        if (
            model_path.is_absolute()
            or model_path.suffix
            or (
                len(model_path_parts) > 0
                and model_path_parts[0] in {".", "..", "~", *_LOCAL_MODEL_PATH_PREFIXES}
            )
        ):
            return False
        hf_validation_error_cls, validate_repo_id = (
            self._get_huggingface_repo_validation()
        )
        try:
            validate_repo_id(self.model_name)
        except hf_validation_error_cls:
            return False
        return "/" in self.model_name

    def _normalize_transcription_segments(
        self,
        segments: Sequence[TranscribedSegment],
        *,
        source: str,
        cache_path: Path | None,
        use_vad: bool,
    ) -> list[TranscribedSegment]:
        """Normalize malformed transcription segments from Whisper output.

        Arguments:
            segments: raw transcription segments
            source: source of the segments, for logging
            cache_path: cache path associated with the segments, if any
            use_vad: whether Whisper VAD produced the segments
        Returns:
            normalized transcription segments
        """
        normalized_segments: list[TranscribedSegment] = []
        segment_idx = 0
        while segment_idx < len(segments):
            segment = segments[segment_idx].model_copy(deep=True)

            if segment_idx + 1 < len(segments):
                next_segment = segments[segment_idx + 1]
                if segment_text_from_words := self._get_duplicate_segment_pair_text(
                    segment,
                    next_segment,
                ):
                    logger.warning(
                        f"Coalescing malformed Whisper segment pair for "
                        f"model={self.model_name} vad={use_vad} "
                        f"source={source} cache={cache_path} "
                        f"segment_idxs=({segment_idx},{segment_idx + 1}) "
                        f"ids=({segment.id},{next_segment.id}) "
                        f"text={segment_text_from_words!r}"
                    )
                    normalized_segments.append(
                        self._get_coalesced_segment(
                            segment,
                            next_segment,
                            segment_text_from_words,
                        )
                    )
                    segment_idx += 2
                    continue

            if segment.text.strip() and not segment.words:
                logger.warning(
                    f"Whisper segment is missing word timings for "
                    f"model={self.model_name} vad={use_vad} "
                    f"source={source} cache={cache_path} "
                    f"segment_idx={segment_idx} id={segment.id} "
                    f"start={segment.start} end={segment.end} "
                    f"text={segment.text!r}"
                )

            normalized_segments.append(segment)
            segment_idx += 1

        return normalized_segments

    @staticmethod
    def _get_coalesced_segment(
        segment_with_words: TranscribedSegment,
        duplicate_segment: TranscribedSegment,
        text: str,
    ) -> TranscribedSegment:
        """Coalesce a malformed empty-text/timed and text-only duplicate pair.

        Arguments:
            segment_with_words: first segment containing word timings
            duplicate_segment: following duplicate segment lacking word timings
            text: repaired segment text
        Returns:
            coalesced segment
        """
        coalesced_segment = duplicate_segment.model_copy(deep=True)
        coalesced_segment.start = min(segment_with_words.start, duplicate_segment.start)
        coalesced_segment.end = max(segment_with_words.end, duplicate_segment.end)
        coalesced_segment.text = text
        coalesced_segment.words = [
            word.model_copy(deep=True) for word in (segment_with_words.words or [])
        ]
        return coalesced_segment

    @staticmethod
    def _get_duplicate_segment_pair_text(
        segment: TranscribedSegment,
        next_segment: TranscribedSegment,
    ) -> str | None:
        """Get repaired text for a known malformed duplicate-segment pair.

        Arguments:
            segment: current segment
            next_segment: following segment
        Returns:
            repaired text if the pair matches the known malformed pattern
        """
        if (
            not segment.words
            or next_segment.words
            or segment.text.strip()
            or not next_segment.text.strip()
            or next_segment.start > segment.end
        ):
            return None

        segment_text_from_words = "".join(word.text for word in segment.words)
        if not segment_text_from_words or next_segment.text != segment_text_from_words:
            return None

        return segment_text_from_words

    @staticmethod
    def _get_huggingface_repo_validation() -> tuple[type[Exception], Any]:
        """Import HuggingFace repo validation helpers on demand."""
        try:
            from huggingface_hub.utils import (  # noqa: E501, PLC0415
                HFValidationError,
                validate_repo_id,
            )
        except ImportError as exc:
            raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
        return HFValidationError, validate_repo_id

    @staticmethod
    def _get_snapshot_download() -> Any:
        """Import HuggingFace snapshot downloader on demand."""
        try:
            from huggingface_hub import (  # noqa: PLC0415
                snapshot_download,
            )
        except ImportError as exc:
            raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
        return snapshot_download

    @staticmethod
    def _get_whisper_module() -> Any:
        """Import whisper-timestamped on demand."""
        try:
            import whisper_timestamped as whisper  # noqa: E501, PLC0415
        except ImportError as exc:
            raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
        return whisper

    def _get_backend_cache_metadata(
        self,
        attempt: TranscriptionAttempt,
    ) -> dict[str, object]:
        """Get cache metadata identifying configured Whisper output.

        Arguments:
            attempt: preprocessing attempt
        Returns:
            backend configuration identifying the output
        """
        temperature: object = self.temperature
        if not isinstance(self.temperature, int | float):
            temperature = list(self.temperature)
        vad_implementation = None
        if attempt.use_vad:
            vad_implementation = "whisper-timestamped"
        return {
            "condition_on_previous_text": self.condition_on_previous_text,
            "language": self.language,
            "model_name": self.model_name,
            "temperature": temperature,
            "vad_implementation": vad_implementation,
        }

    def _prepare_cached_segments(
        self,
        segments: list[TranscribedSegment],
        cache_path: Path,
        attempt: TranscriptionAttempt,
    ) -> list[TranscribedSegment]:
        """Normalize cached Whisper segments.

        Arguments:
            segments: cached transcription segments
            cache_path: path from which the segments were loaded
            attempt: preprocessing attempt that produced the segments
        Returns:
            normalized cached segments
        """
        return self._normalize_transcription_segments(
            segments,
            source="cache",
            cache_path=cache_path,
            use_vad=attempt.use_vad,
        )

    def _transcribe_attempt(
        self,
        audio: AudioSegment,
        attempt: TranscriptionAttempt,
    ) -> list[TranscribedSegment]:
        """Run one uncached Whisper transcription attempt.

        Arguments:
            audio: original or Demucs-separated audio to transcribe
            attempt: preprocessing attempt
        Returns:
            normalized transcription segments
        Raises:
            TranscriptionInferenceError: if Whisper fails with an assertion
        """
        whisper = self._get_whisper_module()
        try:
            with get_temp_file_path(suffix=".wav") as temp_audio_path:
                audio.export(temp_audio_path, format="wav")
                sample_len = self._get_sample_len(audio)
                logger.info(
                    f"Limiting Whisper decoding to {sample_len} tokens for "
                    f"{len(audio) / 1000:.2f}s of audio"
                )
                result = whisper.transcribe(
                    self.model,
                    str(temp_audio_path),
                    language=self.language,
                    vad=attempt.use_vad,
                    temperature=self.temperature,
                    condition_on_previous_text=self.condition_on_previous_text,
                    sample_len=sample_len,
                )
        except AssertionError as exc:
            raise TranscriptionInferenceError(
                f"Whisper inference failed with an assertion: {exc}"
            ) from exc

        segments = [TranscribedSegment(**segment) for segment in result["segments"]]
        return self._normalize_transcription_segments(
            segments,
            source="whisper",
            cache_path=None,
            use_vad=attempt.use_vad,
        )
