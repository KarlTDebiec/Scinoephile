#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Transcribes audio using Whisper."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from logging import getLogger
from math import ceil
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from scinoephile.common.file import get_temp_file_path, open_atomic_text_file
from scinoephile.common.validation import val_output_dir_path
from scinoephile.core.ml import get_torch_device

from .exceptions import TranscriptionInferenceError
from .transcribed_segment import TranscribedSegment

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


class WhisperTranscriber:
    """Transcribes audio using Whisper."""

    _models: ClassVar[dict[tuple[str, str], Any]] = {}
    """Loaded models shared by model name and device within the current process."""

    def __init__(
        self,
        model_name: str = "khleeloo/whisper-large-v3-cantonese",
        language: str = "yue",
        cache_dir_path: Path | None = None,
        use_demucs: bool = False,
        use_vad: bool = True,
        temperature: float | Sequence[float] = 0.0,
        condition_on_previous_text: bool = True,
    ):
        """Initialize.

        Arguments:
            model_name: name of Whisper model to use
            language: language code for transcription
            cache_dir_path: directory in which to cache
            use_demucs: whether Demucs preprocessing was applied
            use_vad: whether to enable Whisper VAD
            temperature: decoding temperature or fallback schedule
            condition_on_previous_text: whether to condition each decoding window on
                the preceding window
        """
        self.model_name = model_name
        self._model: Any | None = None
        self.language = language
        self.use_demucs = use_demucs
        self.use_vad = use_vad
        self.temperature = temperature
        self.condition_on_previous_text = condition_on_previous_text
        self.cache_dir_path = None
        if cache_dir_path is not None:
            self.cache_dir_path = val_output_dir_path(cache_dir_path)

    def __call__(
        self,
        audio: AudioSegment,
        *,
        cache_audio: AudioSegment | None = None,
        use_cache: bool = True,
        overwrite_cache: bool = False,
    ) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: audio to transcribe
            cache_audio: optional audio used for cache-key generation
            use_cache: whether to return a cached transcription when available
            overwrite_cache: whether to replace the matching cache file
        Returns:
            transcription, split into segments
        """
        return self.transcribe(
            audio,
            cache_audio=cache_audio,
            use_cache=use_cache,
            overwrite_cache=overwrite_cache,
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

            whisper = self._import_whisper_timestamped()
            try:
                self._model = whisper.load_model(self.model_name, device=device)
            except FileNotFoundError:
                if not self._model_name_is_huggingface_repo_id():
                    raise
                logger.warning(
                    "Whisper model load failed due to missing cache file; "
                    "re-downloading HuggingFace snapshot and retrying."
                )
                snapshot_download = self._import_huggingface_hub_snapshot_download()
                snapshot_download(repo_id=self.model_name)
                self._model = whisper.load_model(self.model_name, device=device)
            self._models[model_key] = self._model
        return self._model

    def get_cached_transcription(
        self,
        cache_audio: AudioSegment,
        *,
        overwrite_cache: bool = False,
    ) -> list[TranscribedSegment] | None:
        """Get cached transcription for audio if available.

        Arguments:
            cache_audio: audio used for cache-key generation
            overwrite_cache: whether to remove the matching cache file
        Returns:
            cached transcription, if present
        """
        cache_path = self._get_cache_path(cache_audio)
        if cache_path is None or not cache_path.exists():
            return None
        if overwrite_cache:
            cache_path.unlink()
            logger.info(f"Removed Whisper transcription cache: {cache_path}")
            return None

        logger.info(f"Loaded Whisper transcription from cache: {cache_path}")
        try:
            with cache_path.open("r", encoding="utf-8") as file:
                payload = json.load(file)
            if not isinstance(payload, list):
                raise TranscriptionInferenceError(
                    f"Malformed Whisper cache payload: {cache_path}"
                )
            segments = [TranscribedSegment.model_validate(s) for s in payload]
        except TranscriptionInferenceError:
            raise
        except (OSError, TypeError, ValueError) as exc:
            raise TranscriptionInferenceError(
                f"Unable to read Whisper transcription cache {cache_path}: {exc}"
            ) from exc
        segments = self._normalize_transcription_segments(
            segments,
            source="cache",
            cache_path=cache_path,
        )
        cache_path.touch()
        return segments

    def transcribe(
        self,
        audio: AudioSegment,
        *,
        cache_audio: AudioSegment | None = None,
        use_cache: bool = True,
        overwrite_cache: bool = False,
    ) -> list[TranscribedSegment]:
        """Transcribe audio.

        Arguments:
            audio: audio to transcribe
            cache_audio: optional audio used for cache-key generation
            use_cache: whether to return a cached transcription when available
            overwrite_cache: whether to replace the matching cache file
        Returns:
            transcription, split into segments
        """
        cache_audio = cache_audio or audio
        cache_path = self._get_cache_path(cache_audio)
        if use_cache or overwrite_cache:
            try:
                segments = self.get_cached_transcription(
                    cache_audio,
                    overwrite_cache=overwrite_cache,
                )
            except TranscriptionInferenceError as exc:
                logger.warning(f"Unable to read Whisper transcription cache: {exc}")
            else:
                if segments is not None:
                    return segments

        # Transcribe using Whisper
        whisper = self._import_whisper_timestamped()
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
                vad=self.use_vad,
                temperature=self.temperature,
                condition_on_previous_text=self.condition_on_previous_text,
                sample_len=sample_len,
            )
        segments = [TranscribedSegment(**s) for s in result["segments"]]
        segments = self._normalize_transcription_segments(
            segments,
            source="whisper",
            cache_path=cache_path,
        )

        # Update cache
        if cache_path is not None:
            with open_atomic_text_file(cache_path) as file:
                json.dump(
                    [segment.model_dump() for segment in segments],
                    file,
                    ensure_ascii=False,
                    indent=2,
                )
            logger.info(f"Saved Whisper transcription to cache: {cache_path}")

        return segments

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
            self._import_huggingface_hub_utils_repo_validation()
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
    ) -> list[TranscribedSegment]:
        """Normalize malformed transcription segments from Whisper output.

        Arguments:
            segments: raw transcription segments
            source: source of the segments, for logging
            cache_path: cache path associated with the segments, if any
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
                        f"model={self.model_name} vad={self.use_vad} "
                        f"source={source} cache={cache_path} "
                        f"segment_idxs=({segment_idx},{segment_idx + 1}) "
                        f"ids=({segment.id},{next_segment.id}) "
                        f"text={segment_text_from_words!r}"
                    )
                    normalized_segments.append(
                        self._get_coalesced_segment(
                            segment,
                            next_segment,
                            text=segment_text_from_words,
                        )
                    )
                    segment_idx += 2
                    continue

            if segment.text.strip() and not segment.words:
                logger.warning(
                    f"Whisper segment is missing word timings for "
                    f"model={self.model_name} vad={self.use_vad} "
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
        *,
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
    def _import_huggingface_hub_snapshot_download() -> Any:
        """Import HuggingFace snapshot downloader on demand."""
        try:
            from huggingface_hub import (  # noqa: PLC0415
                snapshot_download,
            )
        except ImportError as exc:
            raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
        return snapshot_download

    @staticmethod
    def _import_huggingface_hub_utils_repo_validation() -> tuple[type[Exception], Any]:
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
    def _import_whisper_timestamped() -> Any:
        """Import whisper-timestamped on demand."""
        try:
            import whisper_timestamped as whisper  # noqa: E501, PLC0415
        except ImportError as exc:
            raise ImportError(_TRANSCRIPTION_EXTRA_MESSAGE) from exc
        return whisper

    def _get_cache_path(self, audio: AudioSegment) -> Path | None:
        """Get cache path based on hash of audio data.

        Arguments:
            audio: audio used to derive the cache key
        Returns:
            path to cache file
        """
        if self.cache_dir_path is None:
            return None

        audio_sha256 = hashlib.sha256(audio.raw_data).hexdigest()
        cache_key = (
            f"{audio_sha256}_{self.model_name}_{self.language}_"
            f"demucs-{'on' if self.use_demucs else 'off'}_"
            f"vad-{'on' if self.use_vad else 'off'}"
        )
        if self.temperature != 0.0 or not self.condition_on_previous_text:
            if isinstance(self.temperature, Sequence):
                temperature_key = ",".join(
                    f"{temperature:g}" for temperature in self.temperature
                )
            else:
                temperature_key = f"{self.temperature:g}"
            cache_key += (
                f"_temperature-{temperature_key}_"
                "condition-on-previous-text-"
                f"{'on' if self.condition_on_previous_text else 'off'}"
            )
        cache_sha256 = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir_path / f"{cache_sha256}.json"
