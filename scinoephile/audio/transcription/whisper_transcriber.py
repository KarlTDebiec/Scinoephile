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

from .chunking import get_offset_core_segments
from .ctc_aligner import CtcAligner
from .demucs import DemucsSeparator
from .exceptions import TranscriptionEmptyError, TranscriptionInferenceError
from .preprocessing_settings import (
    DemucsMode,
    TranscriptionPreprocessingSettings,
    VADMode,
)
from .source_quality import (
    SUBTITLE_CREDIT_HALLUCINATION_MARKERS,
    get_transcription_source_quality_issue,
)
from .transcribed_segment import TranscribedSegment
from .transcriber import Transcriber
from .vad import VADImplementation, VoiceActivityDetector
from .voice_activity_trace import VoiceActivityTrace

__all__ = ["SUBTITLE_CREDIT_HALLUCINATION_MARKERS", "WhisperTranscriber"]

_CHUNK_POSTPROCESSING_VERSION = "1"
"""Version of overlapping Whisper fallback chunk recombination."""

_FALLBACK_MAX_WINDOW_DURATION_SECONDS = 30.0
"""Maximum Whisper inference-window duration during hallucination recovery."""

_FALLBACK_MINIMUM_WINDOW_DURATION_SECONDS = 1.0
"""Smallest Whisper window retried after suspicious decoding."""

_FALLBACK_OVERLAP_SECONDS = 1.0
"""Context overlap around each Whisper fallback core chunk."""

_LOCAL_MODEL_PATH_PREFIXES = {"checkpoint", "checkpoints", "model", "models"}
_MAX_SAMPLE_LEN = 224
"""Maximum token budget supported by the configured Whisper models."""

_MAX_TOKENS_PER_SECOND = 16
"""Generous decode budget per second of source audio."""

_MIN_SAMPLE_LEN = 32
"""Minimum token budget for very short source audio."""

_SUBTITLE_CREDIT_MAX_NO_SPEECH_PROBABILITY = 0.6
"""Minimum no-speech probability for discarding a terminal subtitle credit."""

_TOKEN_LIMIT_GUARD_FRACTION = 0.95
"""Decode-budget fraction that triggers smaller-window recovery."""

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
        vad_implementation: VADImplementation = VADImplementation.SILERO,
        vad_detector: VoiceActivityDetector | None = None,
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
            vad_implementation: voice activity detection implementation
            vad_detector: optional shared voice activity detector
        """
        self.model_name = model_name
        self._model: WhisperModel | None = None
        self.language = language
        self.temperature: float | Sequence[float] = temperature
        self.condition_on_previous_text = condition_on_previous_text
        self.ctc_aligner = ctc_aligner
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
    def _get_retry_chunking(audio: AudioSegment) -> tuple[int, int]:
        """Get smaller core and overlap durations for a suspicious window.

        The initial fallback keeps complete inference windows at or below Whisper's
        native 30-second receptive field. Later recursive retries bisect the failing
        audio while retaining bounded context on each side.

        Arguments:
            audio: suspicious audio window
        Returns:
            core chunk duration and overlap in milliseconds
        """
        maximum_window_ms = round(_FALLBACK_MAX_WINDOW_DURATION_SECONDS * 1000)
        configured_overlap_ms = round(_FALLBACK_OVERLAP_SECONDS * 1000)
        if len(audio) > maximum_window_ms:
            chunk_duration_ms = maximum_window_ms - (2 * configured_overlap_ms)
        else:
            chunk_duration_ms = max(1, len(audio) // 2)
        maximum_overlap_ms = max(0, (chunk_duration_ms - 1) // 2)
        chunk_overlap_ms = min(configured_overlap_ms, maximum_overlap_ms)
        return chunk_duration_ms, chunk_overlap_ms

    @staticmethod
    def _get_retry_reason(
        segments: Sequence[TranscribedSegment],
        *,
        audio_duration_seconds: float,
        guarded_window_count: int,
    ) -> str | None:
        """Get the reason suspicious Whisper output needs smaller-window recovery.

        Arguments:
            segments: normalized Whisper segments
            audio_duration_seconds: duration of the attempted audio window
            guarded_window_count: decoder windows using at least 95% of their budget
        Returns:
            retry reason, if recovery is required
        """
        if guarded_window_count:
            return (
                f"{guarded_window_count} decoder window(s) used at least "
                f"{_TOKEN_LIMIT_GUARD_FRACTION:.0%} of their token budget."
            )
        if not any(segment.text.strip() for segment in segments):
            return None
        return get_transcription_source_quality_issue(
            segments, audio_duration_seconds=audio_duration_seconds
        )

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
        metadata: dict[str, object] = {
            "chunk_postprocessing_version": _CHUNK_POSTPROCESSING_VERSION,
            "condition_on_previous_text": self.condition_on_previous_text,
            "fallback_max_window_duration_seconds": (
                _FALLBACK_MAX_WINDOW_DURATION_SECONDS
            ),
            "fallback_minimum_window_duration_seconds": (
                _FALLBACK_MINIMUM_WINDOW_DURATION_SECONDS
            ),
            "fallback_overlap_seconds": _FALLBACK_OVERLAP_SECONDS,
            "language": self.language,
            "model_name": self.model_name,
            "temperature": temperature,
            "token_limit_guard_fraction": _TOKEN_LIMIT_GUARD_FRACTION,
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

    def _get_whisper_vad(
        self, audio: AudioSegment, settings: TranscriptionPreprocessingSettings
    ) -> tuple[bool | list[tuple[float, float]], VoiceActivityTrace | None]:
        """Get Whisper-compatible VAD intervals and their probability trace.

        Arguments:
            audio: audio whose speech intervals should be detected
            settings: active preprocessing settings
        Returns:
            Whisper VAD configuration and its probability trace, if enabled
        Raises:
            TranscriptionEmptyError: if enabled VAD finds no speech
        """
        if not settings.use_vad:
            return False, None

        trace = self._get_voice_activity_trace(audio)
        speech_intervals = self.vad_detector.get_speech_intervals(trace)
        if not speech_intervals:
            implementation_label = self.vad_detector.implementation.value.upper()
            raise TranscriptionEmptyError(
                f"{implementation_label} VAD found no speech."
            )
        return (
            [(start_ms / 1000, end_ms / 1000) for start_ms, end_ms in speech_intervals],
            trace,
        )

    def _transcribe_attempt(
        self, audio: AudioSegment, settings: TranscriptionPreprocessingSettings
    ) -> list[TranscribedSegment]:
        """Run Whisper, recovering suspicious output with smaller windows.

        Arguments:
            audio: original or Demucs-separated audio to transcribe
            settings: preprocessing settings
        Returns:
            normalized transcription segments
        Raises:
            TranscriptionInferenceError: if Whisper fails with an assertion
        """
        segments, guarded_window_count = self._transcribe_audio_window(audio, settings)
        retry_reason = self._get_retry_reason(
            segments,
            audio_duration_seconds=len(audio) / 1000,
            guarded_window_count=guarded_window_count,
        )
        if retry_reason is None:
            return segments

        chunk_duration_ms, chunk_overlap_ms = self._get_retry_chunking(audio)
        logger.warning(
            f"Retrying suspicious Whisper output with "
            f"{chunk_duration_ms / 1000:.3f}s core chunks: {retry_reason}"
        )
        return self._transcribe_chunked_audio(
            audio, settings, chunk_duration_ms, chunk_overlap_ms
        )

    def _transcribe_audio_window(
        self, audio: AudioSegment, settings: TranscriptionPreprocessingSettings
    ) -> tuple[list[TranscribedSegment], int]:
        """Transcribe one audio window and count near-exhausted decoder windows.

        Arguments:
            audio: audio window to transcribe
            settings: preprocessing settings
        Returns:
            normalized segments and number of guarded decoder windows
        Raises:
            TranscriptionInferenceError: if Whisper inference fails
        """
        whisper_timestamped = import_whisper_timestamped()
        whisper_vad, voice_activity_trace = self._get_whisper_vad(audio, settings)
        with get_temp_file_path(suffix=".wav") as temp_audio_path:
            try:
                audio.export(temp_audio_path, format="wav")
                sample_len = self._get_sample_len(audio)
                guarded_limit = ceil(sample_len * _TOKEN_LIMIT_GUARD_FRACTION)
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
                        len(result.tokens) >= guarded_limit for result in decode_results
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
                            vad=whisper_vad,
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
                        fallback_segments = self._transcribe_with_ctc_fallback(
                            audio, temp_audio_path, sample_len, exc
                        )
                        if voice_activity_trace is not None:
                            fallback_segments = self._add_voice_activity_scores(
                                fallback_segments, voice_activity_trace
                            )
                        return fallback_segments, len(exhausted_windows)
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
                f"Whisper used at least {guarded_limit} of its {sample_len}-token "
                f"decoding budget "
                f"(affected windows: {limit_hit_count})"
            )
        normalized_segments = self._normalize_transcription_segments(
            segments, source="whisper", cache_path=None, use_vad=settings.use_vad
        )
        if voice_activity_trace is not None:
            normalized_segments = self._add_voice_activity_scores(
                normalized_segments, voice_activity_trace
            )
        return normalized_segments, limit_hit_count

    def _transcribe_audio_window_with_retry(
        self, audio: AudioSegment, settings: TranscriptionPreprocessingSettings
    ) -> list[TranscribedSegment]:
        """Transcribe a window, recursively splitting suspicious output.

        Arguments:
            audio: audio window to transcribe
            settings: preprocessing settings
        Returns:
            usable timestamped segments, possibly empty for an irrecoverable window
        """
        segments, guarded_window_count = self._transcribe_audio_window(audio, settings)
        retry_reason = self._get_retry_reason(
            segments,
            audio_duration_seconds=len(audio) / 1000,
            guarded_window_count=guarded_window_count,
        )
        if retry_reason is None:
            return segments

        minimum_window_ms = round(_FALLBACK_MINIMUM_WINDOW_DURATION_SECONDS * 1000)
        if len(audio) <= minimum_window_ms:
            logger.warning(
                f"Omitting irrecoverable {len(audio) / 1000:.3f}s Whisper window: "
                f"{retry_reason}"
            )
            return []

        chunk_duration_ms, chunk_overlap_ms = self._get_retry_chunking(audio)
        logger.info(
            f"Retrying suspicious {len(audio) / 1000:.3f}s Whisper window with "
            f"{chunk_duration_ms / 1000:.3f}s core chunks: {retry_reason}"
        )
        return self._transcribe_chunked_audio(
            audio, settings, chunk_duration_ms, chunk_overlap_ms
        )

    def _transcribe_chunked_audio(
        self,
        audio: AudioSegment,
        settings: TranscriptionPreprocessingSettings,
        chunk_duration_ms: int,
        chunk_overlap_ms: int,
    ) -> list[TranscribedSegment]:
        """Transcribe overlapping chunks and retain words owned by each core.

        Arguments:
            audio: audio to transcribe
            settings: preprocessing settings
            chunk_duration_ms: core chunk duration in milliseconds
            chunk_overlap_ms: context overlap around each core chunk
        Returns:
            combined timestamped segments
        Raises:
            TranscriptionEmptyError: if every chunk is empty or irrecoverable
        """
        segments: list[TranscribedSegment] = []
        for core_start_ms in range(0, len(audio), chunk_duration_ms):
            core_end_ms = min(len(audio), core_start_ms + chunk_duration_ms)
            window_start_ms = max(0, core_start_ms - chunk_overlap_ms)
            window_end_ms = min(len(audio), core_end_ms + chunk_overlap_ms)
            window_audio = audio[window_start_ms:window_end_ms]
            try:
                window_segments = self._transcribe_audio_window_with_retry(
                    window_audio, settings
                )
            except TranscriptionEmptyError:
                logger.info(
                    f"Skipping empty Whisper audio window "
                    f"{window_start_ms / 1000:.2f}s-"
                    f"{window_end_ms / 1000:.2f}s"
                )
                continue
            segments.extend(
                get_offset_core_segments(
                    window_segments,
                    window_start_ms / 1000,
                    core_start_ms / 1000,
                    core_end_ms / 1000,
                    len(segments),
                )
            )
        if not segments:
            raise TranscriptionEmptyError(
                "Whisper returned no usable transcript across fallback chunks."
            )
        return segments

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
