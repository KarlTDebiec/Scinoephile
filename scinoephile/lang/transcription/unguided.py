#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Unguided transcription and deterministic subtitle delineation."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from logging import getLogger
from pathlib import Path

from pydub import AudioSegment

from scinoephile.audio.diarization import (
    DiarizationMode,
    PyannoteDiarizer,
    SpeakerDiarizationError,
    SpeakerDiarizationResult,
)
from scinoephile.audio.subtitles import (
    AudioSeries,
    UnguidedDelineationResult,
    UnguidedDelineationSettings,
    UnguidedDelineator,
    get_series_from_segments,
)
from scinoephile.audio.transcription import (
    DemucsMode,
    MlxAudioTranscriber,
    SpeechBlock,
    SpeechBlockSettings,
    SpeechBlockSplitter,
    TranscribedSegment,
    TranscriptionEmptyError,
    VADImplementation,
    VADMode,
    VoiceActivityCache,
    VoiceActivityDetector,
    VoiceActivityTrace,
    WhisperTranscriber,
)
from scinoephile.audio.transcription.mlx_audio.backend import (
    MIMO_MODEL_NAME,
    QWEN3_ASR_MODEL_NAME,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider

from .guided import DEFAULT_SPECS
from .multisource import get_unguided_multi_source_transcriber
from .transcriber import TranscriptionBackend

__all__ = ["UnguidedTranscriber", "get_unguided_transcriber"]


logger = getLogger(__name__)

_MLX_AUDIO_CHUNK_DURATION_SECONDS = 30.0
"""Core MLX-Audio chunk duration used for source-length unguided input."""


class UnguidedTranscriber:
    """Transcribe VAD-derived source blocks and infer subtitle boundaries."""

    def __init__(
        self,
        *,
        language: Language,
        transcriber: Callable[[AudioSegment], list[TranscribedSegment]],
        diarization_mode: DiarizationMode = DiarizationMode.OFF,
        cache_root_path: Path | None = None,
        overwrite_cache: bool = False,
        block_settings: SpeechBlockSettings | None = None,
        block_splitter: SpeechBlockSplitter | None = None,
        block_vad_cache: VoiceActivityCache | None = None,
        block_vad_detector: VoiceActivityDetector | None = None,
        delineator: UnguidedDelineator | None = None,
        diarizer: Callable[[AudioSegment], SpeakerDiarizationResult] | None = None,
    ):
        """Initialize.

        Arguments:
            language: transcription language
            transcriber: configured timestamped audio transcriber
            diarization_mode: source-wide speaker diarization mode
            cache_root_path: cache root directory path
            overwrite_cache: whether to replace matching generated cache files
            block_settings: optional VAD-derived block configuration
            block_splitter: optional configured VAD-derived block splitter
            block_vad_cache: optional full-source VAD trace cache
            block_vad_detector: optional full-source block-planning VAD
            delineator: optional configured per-block subtitle delineator
            diarizer: optional configured source-wide speaker diarizer
        """
        self.language = language
        """Transcription language."""
        self.transcriber = transcriber
        """Configured timestamped audio transcriber."""
        self.diarization_mode = diarization_mode
        """Source-wide speaker diarization mode."""
        if block_splitter is None:
            block_splitter = SpeechBlockSplitter(block_settings)
        self.block_splitter = block_splitter
        """Full-source VAD trace block splitter."""
        if block_vad_detector is None:
            settings = self.block_splitter.settings
            block_vad_detector = VoiceActivityDetector(
                VADImplementation.PYANNOTE,
                threshold=settings.voice_activity_threshold,
                min_speech_duration_seconds=settings.min_speech_duration_seconds,
                min_silence_duration_seconds=0.0,
                padding_seconds=0.0,
            )
        self.block_vad_detector = block_vad_detector
        """Voice activity detector used to plan end-to-end source blocks."""
        if block_vad_cache is None:
            block_vad_cache = VoiceActivityCache(cache_root_path, overwrite_cache)
        self.block_vad_cache = block_vad_cache
        """Persistent full-source block-planning VAD trace cache."""
        if delineator is None:
            delineator = UnguidedDelineator()
        self.delineator = delineator
        """Per-block subtitle boundary selector."""
        self.diarizer = diarizer
        """Optional source-wide speaker diarizer."""
        if self.diarization_mode is not DiarizationMode.OFF and self.diarizer is None:
            self.diarizer = PyannoteDiarizer(
                cache_root_path, overwrite_cache=overwrite_cache
            )
        self.last_delineation_result: UnguidedDelineationResult | None = None
        """Most recent boundary decisions and evidence, when processing has run."""
        self.last_delineation_results: list[UnguidedDelineationResult] = []
        """Most recent per-block boundary decisions and evidence."""
        self.last_blocks: list[SpeechBlock] = []
        """Most recent stable full-source block plan."""

    def process(
        self,
        audio_series: AudioSeries,
        *,
        start_at_idx: int = 0,
        stop_at_idx: int | None = None,
    ) -> AudioSeries:
        """Transcribe and delineate selected VAD-derived source blocks.

        Arguments:
            audio_series: complete source audio without required subtitle events
            start_at_idx: inclusive zero-based block index at which to start
            stop_at_idx: exclusive zero-based block index at which to stop
        Returns:
            automatically delineated audio subtitle series
        """
        trace = self._get_voice_activity_trace(audio_series.audio)
        self.last_blocks = self.block_splitter(trace)
        selected_blocks = self._get_selected_blocks(start_at_idx, stop_at_idx)
        diarization = self._get_diarization(audio_series.audio, bool(selected_blocks))

        results = []
        output_segments = []
        for block in selected_blocks:
            block_audio = audio_series.audio[
                block.buffered_start_ms : block.buffered_end_ms
            ]
            try:
                block_segments = self.transcriber(block_audio)
            except TranscriptionEmptyError as exc:
                logger.info(
                    f"Unguided block {block.index + 1} contains no transcribed "
                    f"speech: {exc}"
                )
                continue
            if diarization is not None:
                block_segments = diarization.assign_speakers(
                    block_segments, offset_seconds=block.buffered_start_ms / 1000
                )
            block_segments = self._get_offset_core_segments(block_segments, block)
            block_segments = [
                segment for segment in block_segments if segment.text.strip()
            ]
            if not block_segments:
                logger.info(
                    f"Unguided block {block.index + 1} contains no nonblank "
                    "transcription segments."
                )
                continue
            block_segments = self._add_voice_activity_scores(block_segments, trace)

            try:
                result = self.delineator(block_segments)
            except ValueError as exc:
                raise ScinoephileError(
                    f"Unable to delineate unguided transcription block "
                    f"{block.index + 1}: {exc}"
                ) from exc
            results.append(result)
            output_segments.extend(
                segment for segment in result.segments if segment.text.strip()
            )

        output_segments = [
            segment.model_copy(update={"id": segment_id})
            for segment_id, segment in enumerate(output_segments)
        ]
        self.last_delineation_results = results
        self.last_delineation_result = self._combine_results(results, output_segments)
        return get_series_from_segments(output_segments, audio=audio_series.audio)

    def _add_voice_activity_scores(
        self, segments: list[TranscribedSegment], trace: VoiceActivityTrace
    ) -> list[TranscribedSegment]:
        """Attach full-source VAD summaries to source-timed words."""
        output_segments = [segment.model_copy(deep=True) for segment in segments]
        words = [
            word
            for segment in output_segments
            for word in (segment.words if segment.words is not None else [])
        ]
        threshold = self.block_splitter.settings.voice_activity_threshold
        for word_idx, word in enumerate(words):
            word.voice_activity_score = trace.get_mean_score(word.start, word.end)
            word.voice_activity_peak = trace.get_peak_score(word.start, word.end)
            word.voice_activity_coverage = trace.get_coverage(
                word.start, word.end, threshold
            )
            if word_idx + 1 < len(words):
                next_word = words[word_idx + 1]
                word.following_voice_activity_score = trace.get_mean_score(
                    word.end, next_word.start
                )
        return output_segments

    @staticmethod
    def _combine_results(
        results: list[UnguidedDelineationResult], segments: list[TranscribedSegment]
    ) -> UnguidedDelineationResult:
        """Combine per-block diagnostics for backward-compatible inspection."""
        boundaries = []
        unit_offset = 0
        for result in results:
            boundaries.extend(
                replace(boundary, index=boundary.index + unit_offset)
                for boundary in result.boundaries
            )
            if result.segments:
                unit_offset += len(result.boundaries) + 1
        return UnguidedDelineationResult(
            segments=segments,
            boundaries=boundaries,
            total_cost=sum(result.total_cost for result in results),
            used_relaxed_constraints=any(
                result.used_relaxed_constraints for result in results
            ),
        )

    def _get_diarization(
        self, audio: AudioSegment, has_selected_blocks: bool
    ) -> SpeakerDiarizationResult | None:
        """Get optional source-wide speaker diarization once per run."""
        if self.diarization_mode is DiarizationMode.OFF or not has_selected_blocks:
            return None
        assert self.diarizer is not None
        try:
            return self.diarizer(audio)
        except SpeakerDiarizationError as exc:
            if self.diarization_mode is DiarizationMode.ON:
                raise
            logger.warning(
                f"Speaker diarization is unavailable; continuing without speaker "
                f"evidence: {exc}"
            )
            return None

    @staticmethod
    def _get_offset_core_segments(
        segments: list[TranscribedSegment], block: SpeechBlock
    ) -> list[TranscribedSegment]:
        """Map block-local timings to the source and retain core-owned content."""
        offset_seconds = block.buffered_start_ms / 1000
        core_start_seconds = block.start_ms / 1000
        core_end_seconds = block.end_ms / 1000
        output_segments = []
        for segment in segments:
            if segment.words:
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
                output_segments.append(
                    segment.model_copy(
                        update={
                            "start": words[0].start,
                            "end": words[-1].end,
                            "text": "".join(word.text for word in words),
                            "words": words,
                        }
                    )
                )
                continue

            global_start = segment.start + offset_seconds
            global_end = segment.end + offset_seconds
            midpoint = (global_start + global_end) / 2
            if midpoint < core_start_seconds or midpoint >= core_end_seconds:
                continue
            output_segments.append(
                segment.model_copy(
                    update={
                        "start": max(global_start, core_start_seconds),
                        "end": min(global_end, core_end_seconds),
                    }
                )
            )
        return output_segments

    def _get_selected_blocks(
        self, start_at_idx: int, stop_at_idx: int | None
    ) -> list[SpeechBlock]:
        """Validate and select a half-open range from the stable block plan."""
        block_count = len(self.last_blocks)
        if stop_at_idx is None:
            stop_at_idx = block_count
        if (
            start_at_idx < 0
            or start_at_idx > block_count
            or stop_at_idx < start_at_idx
            or stop_at_idx > block_count
        ):
            raise ScinoephileError(
                f"Invalid unguided block range [{start_at_idx}, {stop_at_idx}) for "
                f"{block_count} available blocks."
            )
        return self.last_blocks[start_at_idx:stop_at_idx]

    def _get_voice_activity_trace(self, audio: AudioSegment) -> VoiceActivityTrace:
        """Load or infer the full-source block-planning VAD trace."""
        metadata = self.block_vad_detector.trace_cache_identity
        trace = self.block_vad_cache.load(audio, metadata)
        if trace is not None:
            return trace
        trace = self.block_vad_detector.get_trace(audio)
        self.block_vad_cache.save(audio, metadata, trace)
        return trace


def get_unguided_transcriber(
    language: Language,
    *,
    multi_source: bool = False,
    model_name: str | None = None,
    backend: TranscriptionBackend = TranscriptionBackend.WHISPER,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    vad_mode: VADMode = VADMode.OFF,
    diarization_mode: DiarizationMode = DiarizationMode.OFF,
    vad_implementation: VADImplementation = VADImplementation.SILERO,
    block_vad_implementation: VADImplementation = VADImplementation.PYANNOTE,
    mlx_audio_token_limit_guard: bool = False,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
    delineation_settings: UnguidedDelineationSettings | None = None,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    no_op: bool = False,
) -> UnguidedTranscriber:
    """Get an unguided transcriber for a supported language.

    Arguments:
        language: transcription language
        multi_source: merge Whisper, MiMo, and Qwen before delineation
        model_name: backend-specific model override
        backend: audio transcription backend
        demucs_mode: Demucs preprocessing mode
        vad_mode: voice activity detection mode
        diarization_mode: source-wide speaker diarization mode
        vad_implementation: voice activity detection implementation
        block_vad_implementation: VAD used to plan end-to-end source blocks
        mlx_audio_token_limit_guard: whether to guard constrained MLX-Audio models
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching generated cache files
        delineation_settings: optional subtitle boundary configuration
        provider: provider to use for multi-source consensus queries
        additional_context: additional context for the consensus prompt
        no_op: select the first available source instead of querying an LLM
    Returns:
        configured unguided transcriber
    Raises:
        ScinoephileError: if unguided transcription does not support the language
    """
    language_specs = [
        spec.language_spec
        for (candidate_language, _), spec in DEFAULT_SPECS.items()
        if candidate_language is language
    ]
    if not language_specs:
        raise ScinoephileError(
            f"Unguided transcription does not support language {language.code}."
        )
    language_spec = language_specs[0]
    if any(spec is not language_spec for spec in language_specs[1:]):
        raise RuntimeError(
            f"Transcription language {language.code} has conflicting configurations."
        )
    block_settings = SpeechBlockSettings()
    block_vad_detector = VoiceActivityDetector(
        block_vad_implementation,
        threshold=block_settings.voice_activity_threshold,
        min_speech_duration_seconds=block_settings.min_speech_duration_seconds,
        min_silence_duration_seconds=0.0,
        padding_seconds=0.0,
    )

    transcriber: Callable[[AudioSegment], list[TranscribedSegment]]
    if multi_source:
        if model_name is not None:
            raise ScinoephileError(
                "A single transcription model cannot be used with multi-source "
                "unguided transcription."
            )
        source_transcribers = {
            "whisper": WhisperTranscriber(
                model_name=language_spec.get_model_name(TranscriptionBackend.WHISPER),
                language=language_spec.whisper_language,
                demucs_mode=demucs_mode,
                vad_mode=VADMode.ON,
                vad_implementation=block_vad_implementation,
                cache_root_path=cache_root_path,
                overwrite_cache=overwrite_cache,
            ),
            "mimo": MlxAudioTranscriber(
                model_name=MIMO_MODEL_NAME,
                language=language,
                chunk_duration_seconds=_MLX_AUDIO_CHUNK_DURATION_SECONDS,
                token_limit_guard=mlx_audio_token_limit_guard,
                demucs_mode=demucs_mode,
                vad_mode=vad_mode,
                vad_implementation=vad_implementation,
                cache_root_path=cache_root_path,
                overwrite_cache=overwrite_cache,
            ),
            "qwen": MlxAudioTranscriber(
                model_name=QWEN3_ASR_MODEL_NAME,
                language=language,
                chunk_duration_seconds=_MLX_AUDIO_CHUNK_DURATION_SECONDS,
                token_limit_guard=False,
                demucs_mode=demucs_mode,
                vad_mode=vad_mode,
                vad_implementation=vad_implementation,
                cache_root_path=cache_root_path,
                overwrite_cache=overwrite_cache,
            ),
        }
        transcriber = get_unguided_multi_source_transcriber(
            language,
            source_transcribers,
            provider=provider,
            cache_root_path=cache_root_path,
            overwrite_cache=overwrite_cache,
            additional_context=additional_context,
            no_op=no_op,
        )
    else:
        if model_name is None:
            model_name = language_spec.get_model_name(backend)
        if backend is TranscriptionBackend.MLX_AUDIO:
            transcriber = MlxAudioTranscriber(
                model_name=model_name,
                language=language,
                chunk_duration_seconds=_MLX_AUDIO_CHUNK_DURATION_SECONDS,
                token_limit_guard=mlx_audio_token_limit_guard,
                demucs_mode=demucs_mode,
                vad_mode=vad_mode,
                vad_implementation=vad_implementation,
                cache_root_path=cache_root_path,
                overwrite_cache=overwrite_cache,
            )
        else:
            transcriber = WhisperTranscriber(
                model_name=model_name,
                language=language_spec.whisper_language,
                demucs_mode=demucs_mode,
                vad_mode=vad_mode,
                vad_implementation=vad_implementation,
                cache_root_path=cache_root_path,
                overwrite_cache=overwrite_cache,
            )
    return UnguidedTranscriber(
        language=language,
        transcriber=transcriber,
        diarization_mode=diarization_mode,
        cache_root_path=cache_root_path,
        overwrite_cache=overwrite_cache,
        block_settings=block_settings,
        block_vad_detector=block_vad_detector,
        delineator=UnguidedDelineator(delineation_settings),
    )
