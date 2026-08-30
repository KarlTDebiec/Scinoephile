#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Orchestrates cached Whisper transcription and preprocessing fallbacks."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from logging import getLogger
from math import ceil
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.audio.separation import DemucsSeparator
from scinoephile.audio.transcription.chunking import get_offset_core_segments
from scinoephile.audio.transcription.ctc import CtcAligner
from scinoephile.audio.transcription.exceptions import (
    TranscriptionEmptyError,
    TranscriptionError,
    TranscriptionRecognitionError,
)
from scinoephile.audio.transcription.preprocessing_settings import (
    DemucsMode,
    TranscriptionPreprocessingSettings,
    VadMode,
)
from scinoephile.audio.transcription.quality import get_transcription_quality_issue
from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcription.transcriber import Transcriber
from scinoephile.audio.vad import VoiceActivityDetector, VoiceActivityTrace
from scinoephile.common.file import get_temp_file_path
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.core.cache.runtime import get_distribution_identity
from scinoephile.core.language import Language

from .ctc_fallback import get_ctc_fallback_segments
from .model import WhisperModel
from .normalization import normalize_segments

__all__ = ["WhisperTranscriber"]

_RECOVERY_TEMPERATURES = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)
"""Whisper temperature schedule used after standard decoding fails."""

_CHUNK_POSTPROCESSING_VERSION = 1
"""Version of overlapping Whisper fallback chunk recombination."""

_FALLBACK_MAX_WINDOW_DURATION_SECONDS = 30.0
"""Maximum Whisper inference-window duration during hallucination recovery."""

_FALLBACK_MINIMUM_WINDOW_DURATION_SECONDS = 1.0
"""Smallest Whisper window retried after suspicious decoding."""

_FALLBACK_OVERLAP_SECONDS = 1.0
"""Context overlap around each Whisper fallback core chunk."""

_TOKEN_LIMIT_GUARD_FRACTION = 0.95
"""Decode-budget fraction that triggers smaller-window recovery."""

if TYPE_CHECKING:
    from pydub import AudioSegment
    from torch import Tensor
    from whisper.decoding import DecodingOptions, DecodingResult

logger = getLogger(__name__)


class WhisperTranscriber(Transcriber):
    """Transcribes audio using Whisper."""

    cache_namespace = AudioCacheNamespace.TRANSCRIPTION_WHISPER
    """Registered namespace for cached Whisper output."""

    backend_name = "whisper"
    """Stable backend name stored in cache identities."""

    backend_label = "Whisper"
    """Human-readable backend name used in log messages."""

    def __init__(
        self,
        model: WhisperModel,
        language: Language,
        demucs_mode: DemucsMode = DemucsMode.OFF,
        vad_mode: VadMode = VadMode.OFF,
        cache_root_path: Path | None = None,
        overwrite_cache: bool = False,
        temperature: float | Sequence[float] = 0.0,
        condition_on_previous_text: bool = True,
        recover_decoding: bool = False,
        ctc_aligner: CtcAligner | None = None,
        demucs_separator: DemucsSeparator | None = None,
        vad_detector: VoiceActivityDetector | None = None,
    ):
        """Initialize.

        Arguments:
            model: configured executable Whisper model
            language: language to transcribe
            demucs_mode: Demucs preprocessing mode
            vad_mode: voice activity detection mode
            cache_root_path: root directory beneath which to cache
            overwrite_cache: whether to replace matching cache files
            temperature: decoding temperature or fallback schedule
            condition_on_previous_text: whether to condition each decoding window on
                the preceding window
            recover_decoding: whether to retry unusable deterministic output with a
                temperature fallback schedule
            ctc_aligner: optional CTC aligner used when Whisper timestamping fails
            demucs_separator: optional shared Demucs vocal separator
            vad_detector: optional shared voice activity detector
        Raises:
            ValueError: if the model does not match the language
        """
        try:
            language_code = model.spec.languages[language]
        except KeyError as exc:
            raise ValueError(
                f"{language} is not supported by Whisper model {model.spec.name}"
            ) from exc
        if model.language_code != language_code:
            raise ValueError(
                "Whisper model and transcriber languages must match "
                f"({model.language_code} != {language_code})."
            )
        self.model = model
        """Configured executable Whisper model."""

        self.language = language
        """Language to transcribe."""

        self.temperature: float | Sequence[float] = temperature
        """Decoding temperature or fallback schedule."""

        self.condition_on_previous_text = condition_on_previous_text
        """Whether each decode window is conditioned on the preceding window."""

        self.ctc_aligner = ctc_aligner
        """Optional CTC aligner used when Whisper timestamping fails."""

        super().__init__(
            cache_root_path,
            demucs_mode,
            vad_mode,
            overwrite_cache,
            demucs_separator,
            vad_detector,
        )
        self.recovery_transcriber: WhisperTranscriber | None = None
        """Defensive temperature-fallback transcriber, when enabled."""
        if recover_decoding:
            self.recovery_transcriber = WhisperTranscriber(
                model=self.model,
                language=self.language,
                demucs_mode=self.demucs_mode,
                vad_mode=self.vad_mode,
                cache_root_path=self._cache.cache_root_path,
                overwrite_cache=self._cache.overwrite,
                temperature=_RECOVERY_TEMPERATURES,
                condition_on_previous_text=False,
                ctc_aligner=self.ctc_aligner,
                demucs_separator=self.demucs_separator,
                vad_detector=self.vad_detector,
            )

    def remove_cached_transcriptions(self, audio: AudioSegment):
        """Remove standard and recovery transcriptions for the audio.

        Arguments:
            audio: audio used for cache-key generation
        """
        super().remove_cached_transcriptions(audio)
        if self.recovery_transcriber is not None:
            self.recovery_transcriber.remove_cached_transcriptions(audio)

    def transcribe(
        self,
        audio: AudioSegment,
        *,
        is_usable: Callable[[list[TranscribedSegment]], bool] | None = None,
    ) -> list[TranscribedSegment]:
        """Transcribe audio, retrying unusable output when configured.

        Arguments:
            audio: audio to transcribe
            is_usable: optional callback used to reject output and trigger retries
        Returns:
            first usable deterministic or recovered transcription
        Raises:
            TranscriptionError: if transcription fails
        """
        try:
            segments = super().transcribe(audio, is_usable=is_usable)
        except TranscriptionError:
            if self.recovery_transcriber is None:
                raise
            segments = []
        if segments or self.recovery_transcriber is None:
            return segments

        logger.info(
            "Retrying Whisper after standard decoding produced no usable transcript"
        )
        segments = self.recovery_transcriber(audio, is_usable=is_usable)
        self.last_cache_key_sha256 = self.recovery_transcriber.last_cache_key_sha256
        return segments

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
        return get_transcription_quality_issue(
            segments, audio_duration_seconds=audio_duration_seconds
        )

    def _get_transcriber_cache_identity(self, audio: AudioSegment) -> CacheIdentity:
        """Get the cache identity for configured Whisper output.

        Arguments:
            audio: audio whose properties may affect transcriber behavior
        Returns:
            transcriber configuration identifying the output
        """
        temperature: int | float | list[float]
        if isinstance(self.temperature, int | float):
            temperature = self.temperature
        else:
            temperature = list(self.temperature)
        cache_identity = {
            "chunk_postprocessing_version": _CHUNK_POSTPROCESSING_VERSION,
            "condition_on_previous_text": self.condition_on_previous_text,
            "device": self.model.device,
            "fallback_max_window_duration_seconds": (
                _FALLBACK_MAX_WINDOW_DURATION_SECONDS
            ),
            "fallback_minimum_window_duration_seconds": (
                _FALLBACK_MINIMUM_WINDOW_DURATION_SECONDS
            ),
            "fallback_overlap_seconds": _FALLBACK_OVERLAP_SECONDS,
            "language": self.model.language_code,
            "model_name": self.model.spec.name,
            "model_revision": self.model.spec.revision,
            "runtime": {
                "openai_whisper": get_distribution_identity("openai-whisper"),
                "whisper_timestamped": get_distribution_identity("whisper-timestamped"),
            },
            "temperature": temperature,
            "token_limit_guard_fraction": _TOKEN_LIMIT_GUARD_FRACTION,
        }
        if self.ctc_aligner is not None:
            cache_identity["timestamp_fallback"] = (
                self.ctc_aligner.cache_config_identity
            )
        return cache_identity

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

    def _prepare_cached_segments(
        self,
        audio: AudioSegment,
        segments: list[TranscribedSegment],
        cache_path: Path,
        settings: TranscriptionPreprocessingSettings,
    ) -> list[TranscribedSegment]:
        """Normalize cached Whisper segments.

        Arguments:
            audio: audio from which the cached segments were transcribed
            segments: cached transcription segments
            cache_path: path from which the segments were loaded
            settings: preprocessing settings that produced the segments
        Returns:
            normalized cached segments
        """
        return normalize_segments(
            segments,
            model_name=self.model.spec.name,
            source="cache",
            cache_path=cache_path,
            use_vad=settings.use_vad,
            audio_duration_seconds=len(audio) / 1000,
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
            TranscriptionError: if Whisper cannot produce usable output
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
            DependencyError: if Whisper dependencies are unavailable
            TranscriptionAlignmentError: if CTC fallback alignment fails
            TranscriptionEmptyError: if VAD or native fallback finds no speech
            TranscriptionRecognitionError: if Whisper inference fails
        """
        whisper_vad, voice_activity_trace = self._get_whisper_vad(audio, settings)
        with get_temp_file_path(suffix=".wav") as temp_audio_path:
            try:
                audio.export(temp_audio_path, format="wav")
                sample_len = self.model.get_sample_len(audio)
                guarded_limit = ceil(sample_len * _TOKEN_LIMIT_GUARD_FRACTION)
                logger.debug(
                    f"Using a {sample_len}-token Whisper decoding budget per window "
                    f"for {len(audio) / 1000:.2f}s of audio"
                )
                native_model = self.model.model
                decode_is_instance_attribute = "decode" in vars(native_model)
                decode = native_model.decode
                exhausted_windows: list[Tensor] = []

                def decode_with_limit_tracking(
                    mel: Tensor, options: DecodingOptions, **kwargs: Any
                ) -> DecodingResult | list[DecodingResult]:
                    """Decode a window and record whether it exhausts its budget.

                    Arguments:
                        mel: log-Mel spectrogram for the decoding window
                        options: native Whisper decoding options
                        **kwargs: additional native Whisper decoder arguments
                    Returns:
                        native Whisper decoding result or results
                    """
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

                setattr(native_model, "decode", decode_with_limit_tracking)
                try:
                    try:
                        segments = self.model(
                            temp_audio_path,
                            vad=whisper_vad,
                            temperature=self.temperature,
                            condition_on_previous_text=self.condition_on_previous_text,
                            sample_len=sample_len,
                        )
                    finally:
                        if decode_is_instance_attribute:
                            setattr(native_model, "decode", decode)
                        else:
                            delattr(native_model, "decode")
                except AssertionError as exc:
                    if self.ctc_aligner is not None and str(exc).startswith(
                        "Inconsistent number of segments:"
                    ):
                        segments = get_ctc_fallback_segments(
                            self.model,
                            self.ctc_aligner,
                            audio,
                            temp_audio_path,
                            sample_len,
                            exc,
                            temperature=self.temperature,
                            condition_on_previous_text=(
                                self.condition_on_previous_text
                            ),
                        )
                    else:
                        raise TranscriptionRecognitionError(
                            f"Whisper inference failed with an assertion: {exc}"
                        ) from exc
            except TranscriptionRecognitionError:
                raise
            except (ImportError, OSError, RuntimeError, TypeError, ValueError) as exc:
                raise TranscriptionRecognitionError(
                    f"Unable to run Whisper inference: {exc}"
                ) from exc

        limit_hit_count = len(exhausted_windows)
        if limit_hit_count:
            logger.info(
                f"Whisper used at least {guarded_limit} of its {sample_len}-token "
                f"decoding budget (affected windows: {limit_hit_count})"
            )
        normalized_segments = normalize_segments(
            segments,
            model_name=self.model.spec.name,
            source="whisper",
            cache_path=None,
            use_vad=settings.use_vad,
            audio_duration_seconds=len(audio) / 1000,
            discard_repetitive_windows=False,
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
