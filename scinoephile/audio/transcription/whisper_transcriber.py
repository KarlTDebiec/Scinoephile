#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Transcribes audio using Whisper."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from logging import getLogger
from math import ceil
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, cast

from scinoephile.common.file import get_temp_file_path
from scinoephile.core.dependencies.transcription import (
    import_huggingface_hub,
    import_huggingface_hub_utils,
    import_whisper_timestamped,
)
from scinoephile.core.ml import get_torch_device

from .ctc_aligner import CtcAligner
from .demucs import DemucsSeparator
from .exceptions import TranscriptionEmptyError, TranscriptionInferenceError
from .preprocessing_settings import (
    DemucsMode,
    TranscriptionPreprocessingSettings,
    VADMode,
)
from .transcribed_segment import TranscribedSegment
from .transcriber import Transcriber

__all__ = ["SUBTITLE_CREDIT_HALLUCINATION_MARKERS", "WhisperTranscriber"]

SUBTITLE_CREDIT_HALLUCINATION_MARKERS = ("amara.org", "字幕由", "字幕提供者")
"""Markers indicating an ASR-generated subtitle-credit hallucination."""

_LOCAL_MODEL_PATH_PREFIXES = {"checkpoint", "checkpoints", "model", "models"}
_MAX_SAMPLE_LEN = 224
"""Maximum token budget supported by the configured Whisper models."""

_MAX_TOKENS_PER_SECOND = 16
"""Generous decode budget per second of source audio."""

_MIN_SAMPLE_LEN = 32
"""Minimum token budget for very short source audio."""

_SUBTITLE_CREDIT_MAX_NO_SPEECH_PROBABILITY = 0.6
"""Minimum no-speech probability for discarding a terminal subtitle credit."""

if TYPE_CHECKING:
    from pydub import AudioSegment
    from torch import Tensor
    from whisper.decoding import DecodingOptions, DecodingResult

    from scinoephile.core.dependencies.transcription import WhisperModel

logger = getLogger(__name__)


class WhisperTranscriber(Transcriber):
    """Transcribes audio using Whisper."""

    backend_name = "whisper"
    """Stable backend name stored in cache metadata."""

    backend_label = "Whisper"
    """Human-readable backend name used in log messages."""

    _models: ClassVar[dict[tuple[str, str], WhisperModel]] = {}
    """Loaded models shared by model name and device within the current process."""

    def __init__(
        self,
        model_name: str = "khleeloo/whisper-large-v3-cantonese",
        language: str = "yue",
        demucs_mode: DemucsMode = DemucsMode.OFF,
        vad_mode: VADMode = VADMode.OFF,
        cache_root_path: Path | None = None,
        overwrite_cache: bool = False,
        temperature: float | Sequence[float] = 0.0,
        condition_on_previous_text: bool = True,
        ctc_aligner: CtcAligner | None = None,
        demucs_separator: DemucsSeparator | None = None,
    ):
        """Initialize.

        Arguments:
            model_name: name of Whisper model to use
            language: language code for transcription
            demucs_mode: Demucs preprocessing mode
            vad_mode: voice activity detection mode
            cache_root_path: root directory beneath which to cache
            overwrite_cache: whether to replace matching cache files
            temperature: decoding temperature or fallback schedule
            condition_on_previous_text: whether to condition each decoding window on
                the preceding window
            ctc_aligner: optional CTC aligner used when Whisper timestamping fails
            demucs_separator: optional shared Demucs vocal separator
        """
        self.model_name = model_name
        self._model: WhisperModel | None = None
        self.language = language
        self.temperature: float | Sequence[float] = temperature
        self.condition_on_previous_text = condition_on_previous_text
        self.ctc_aligner = ctc_aligner
        super().__init__(
            cache_root_path, demucs_mode, vad_mode, overwrite_cache, demucs_separator
        )

    @property
    def model(self) -> WhisperModel:
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

            whisper_timestamped = import_whisper_timestamped()
            try:
                self._model = whisper_timestamped.load_model(
                    self.model_name, device=device
                )
            except FileNotFoundError:
                if not self._model_name_is_huggingface_repo_id():
                    raise
                logger.warning(
                    "Whisper model load failed due to missing cache file; "
                    "re-downloading HuggingFace snapshot and retrying."
                )
                huggingface_hub = import_huggingface_hub()
                huggingface_hub.snapshot_download(repo_id=self.model_name)
                self._model = whisper_timestamped.load_model(
                    self.model_name, device=device
                )
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
        huggingface_hub_utils = import_huggingface_hub_utils()
        try:
            huggingface_hub_utils.validate_repo_id(self.model_name)
        except huggingface_hub_utils.HFValidationError:
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
        text_segment_indexes = [
            idx for idx, segment in enumerate(segments) if segment.text.strip()
        ]
        last_text_segment_idx = None
        if text_segment_indexes:
            last_text_segment_idx = text_segment_indexes[-1]
        segment_idx = 0
        while segment_idx < len(segments):
            segment = segments[segment_idx].model_copy(deep=True)

            normalized_text = segment.text.casefold()
            if (
                segment_idx == last_text_segment_idx
                and segment.no_speech_prob is not None
                and segment.no_speech_prob >= _SUBTITLE_CREDIT_MAX_NO_SPEECH_PROBABILITY
                and any(
                    marker in normalized_text
                    for marker in SUBTITLE_CREDIT_HALLUCINATION_MARKERS
                )
            ):
                logger.warning(
                    f"Discarding terminal Whisper subtitle-credit hallucination for "
                    f"model={self.model_name} vad={use_vad} "
                    f"source={source} cache={cache_path} "
                    f"segment_idx={segment_idx} id={segment.id} "
                    f"no_speech_prob={segment.no_speech_prob:.3f} "
                    f"text={segment.text!r}"
                )
                segment_idx += 1
                continue

            if segment_idx + 1 < len(segments):
                next_segment = segments[segment_idx + 1]
                if segment_text_from_words := self._get_duplicate_segment_pair_text(
                    segment, next_segment
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
                            segment, next_segment, segment_text_from_words
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
        segment: TranscribedSegment, next_segment: TranscribedSegment
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

    def _get_backend_cache_metadata(
        self, audio: AudioSegment, settings: TranscriptionPreprocessingSettings
    ) -> dict[str, object]:
        """Get cache metadata identifying configured Whisper output.

        Arguments:
            audio: audio whose properties may affect backend behavior
            settings: preprocessing settings
        Returns:
            backend configuration identifying the output
        """
        temperature: object = self.temperature
        if not isinstance(self.temperature, int | float):
            temperature = list(self.temperature)
        vad_implementation = None
        if settings.use_vad:
            vad_implementation = "whisper-timestamped"
        metadata: dict[str, object] = {
            "condition_on_previous_text": self.condition_on_previous_text,
            "language": self.language,
            "model_name": self.model_name,
            "temperature": temperature,
            "vad_implementation": vad_implementation,
        }
        if self.ctc_aligner is not None:
            metadata.update(
                {
                    "timestamp_fallback": "ctc",
                    "timestamp_fallback_language": self.ctc_aligner.language.code,
                    "timestamp_fallback_model_name": self.ctc_aligner.model_name,
                }
            )
        return metadata

    def _prepare_cached_segments(
        self,
        segments: list[TranscribedSegment],
        cache_path: Path,
        settings: TranscriptionPreprocessingSettings,
    ) -> list[TranscribedSegment]:
        """Normalize cached Whisper segments.

        Arguments:
            segments: cached transcription segments
            cache_path: path from which the segments were loaded
            settings: preprocessing settings that produced the segments
        Returns:
            normalized cached segments
        """
        return self._normalize_transcription_segments(
            segments, source="cache", cache_path=cache_path, use_vad=settings.use_vad
        )

    def _transcribe_attempt(
        self, audio: AudioSegment, settings: TranscriptionPreprocessingSettings
    ) -> list[TranscribedSegment]:
        """Run one uncached Whisper transcription attempt.

        Arguments:
            audio: original or Demucs-separated audio to transcribe
            settings: preprocessing settings
        Returns:
            normalized transcription segments
        Raises:
            TranscriptionInferenceError: if Whisper fails with an assertion
        """
        whisper_timestamped = import_whisper_timestamped()
        try:
            with get_temp_file_path(suffix=".wav") as temp_audio_path:
                audio.export(temp_audio_path, format="wav")
                sample_len = self._get_sample_len(audio)
                logger.debug(
                    f"Using a {sample_len}-token Whisper decoding budget per window "
                    f"for {len(audio) / 1000:.2f}s of audio"
                )
                model = self.model
                decode_is_instance_attribute = "decode" in vars(model)
                decode = model.decode
                exhausted_windows: list[Tensor] = []

                def decode_with_limit_tracking(
                    mel: Tensor, options: DecodingOptions, **kwargs: object
                ) -> DecodingResult | list[DecodingResult]:
                    """Decode a window and record whether it exhausts its budget."""
                    decode_result = decode(mel, options, **kwargs)
                    decode_results = (
                        cast("list[DecodingResult]", decode_result)
                        if isinstance(decode_result, list)
                        else [cast("DecodingResult", decode_result)]
                    )
                    if any(
                        len(result.tokens) >= sample_len for result in decode_results
                    ) and all(mel is not window for window in exhausted_windows):
                        exhausted_windows.append(mel)
                    return decode_result

                setattr(model, "decode", decode_with_limit_tracking)
                try:
                    try:
                        result = whisper_timestamped.transcribe(
                            model,
                            str(temp_audio_path),
                            language=self.language,
                            vad=settings.use_vad,
                            temperature=self.temperature,
                            condition_on_previous_text=self.condition_on_previous_text,
                            sample_len=sample_len,
                        )
                    finally:
                        if decode_is_instance_attribute:
                            setattr(model, "decode", decode)
                        else:
                            delattr(model, "decode")
                except AssertionError as exc:
                    if self.ctc_aligner is not None and str(exc).startswith(
                        "Inconsistent number of segments:"
                    ):
                        return self._transcribe_with_ctc_fallback(
                            audio, temp_audio_path, sample_len, exc
                        )
                    raise TranscriptionInferenceError(
                        f"Whisper inference failed with an assertion: {exc}"
                    ) from exc
        except TranscriptionInferenceError:
            raise
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            raise TranscriptionInferenceError(
                f"Unable to run Whisper inference: {exc}"
            ) from exc

        segments = [
            TranscribedSegment.model_validate(segment) for segment in result["segments"]
        ]
        limit_hit_count = len(exhausted_windows)
        if limit_hit_count:
            logger.info(
                f"Whisper reached its {sample_len}-token decoding limit "
                f"(affected windows: {limit_hit_count})"
            )
        return self._normalize_transcription_segments(
            segments, source="whisper", cache_path=None, use_vad=settings.use_vad
        )

    def _transcribe_with_ctc_fallback(
        self,
        audio: AudioSegment,
        audio_path: Path,
        sample_len: int,
        timestamp_error: AssertionError,
    ) -> list[TranscribedSegment]:
        """Decode text natively and align it after Whisper timestamping fails.

        Arguments:
            audio: audio being transcribed
            audio_path: temporary audio file passed to native Whisper
            sample_len: maximum number of tokens decoded per Whisper window
            timestamp_error: assertion raised by Whisper Timestamped
        Returns:
            CTC-aligned native Whisper transcript
        Raises:
            TranscriptionEmptyError: if native Whisper returns empty text
            TranscriptionInferenceError: if native Whisper fails or returns malformed
                output
        """
        assert self.ctc_aligner is not None
        logger.info(
            f"Retrying Whisper after timestamp alignment failed ({timestamp_error}) "
            f"using native decoding and CTC model {self.ctc_aligner.model_name}"
        )
        temperature: float | tuple[float, ...]
        if isinstance(self.temperature, int | float):
            temperature = float(self.temperature)
        else:
            temperature = tuple(self.temperature)
        try:
            result = self.model.transcribe(
                str(audio_path),
                language=self.language,
                temperature=temperature,
                condition_on_previous_text=self.condition_on_previous_text,
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
            raise TranscriptionInferenceError(
                f"Unable to run native Whisper fallback: {exc}"
            ) from exc
        if not isinstance(result, Mapping):
            raise TranscriptionInferenceError(
                "Native Whisper fallback returned malformed output."
            )
        text = result.get("text")
        if not isinstance(text, str):
            raise TranscriptionInferenceError(
                "Native Whisper fallback output is missing transcript text."
            )
        if not text.strip():
            raise TranscriptionEmptyError(
                "Native Whisper fallback returned empty transcript."
            )
        native_segment_data = result.get("segments")
        if (
            not isinstance(native_segment_data, Sequence)
            or isinstance(native_segment_data, str | bytes)
            or not native_segment_data
        ):
            raise TranscriptionInferenceError(
                "Native Whisper fallback output contains malformed segments."
            )
        try:
            native_segments = [
                TranscribedSegment.model_validate(segment)
                for segment in native_segment_data
            ]
        except (TypeError, ValueError) as exc:
            raise TranscriptionInferenceError(
                "Native Whisper fallback output contains malformed segments."
            ) from exc

        # Preserve the least favorable native quality signals across CTC timing
        quality_signals: dict[str, float] = {}
        avg_logprobs = [
            segment.avg_logprob
            for segment in native_segments
            if segment.avg_logprob is not None
        ]
        if avg_logprobs:
            quality_signals["avg_logprob"] = min(avg_logprobs)
        compression_ratios = [
            segment.compression_ratio
            for segment in native_segments
            if segment.compression_ratio is not None
        ]
        if compression_ratios:
            quality_signals["compression_ratio"] = max(compression_ratios)
        no_speech_probs = [
            segment.no_speech_prob
            for segment in native_segments
            if segment.no_speech_prob is not None
        ]
        if no_speech_probs:
            quality_signals["no_speech_prob"] = max(no_speech_probs)

        return [
            segment.model_copy(update=quality_signals)
            for segment in self.ctc_aligner(audio, text)
        ]
