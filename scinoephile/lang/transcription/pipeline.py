#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reference-free aligned multi-source transcription pipeline."""

from __future__ import annotations

from collections.abc import Callable
from logging import getLogger
from pathlib import Path

from pydub import AudioSegment

from scinoephile.analysis.transcription_alignment import (
    SubtitleTimingSettings,
    TranscriptionAlignmentArtifact,
    TranscriptionAlignmentBlock,
    TranscriptionAlignmentSource,
)
from scinoephile.audio.classification import (
    AudioClassificationError,
    AudioClassificationMode,
    AudioEvent,
    AudioEventDetectionResult,
    FireRedAudioEventDetector,
    FireRedLanguageIdentifier,
    LanguageIdentificationResult,
)
from scinoephile.audio.diarization import (
    DiarizationMode,
    PyannoteDiarizer,
    SpeakerDiarizationError,
    SpeakerDiarizationResult,
)
from scinoephile.audio.subtitles import AudioSeries, get_series_from_segments
from scinoephile.audio.transcription import (
    DemucsMode,
    SpeechBlock,
    SpeechBlockSettings,
    SpeechBlockSplitter,
    TranscribedSegment,
    TranscriptionEmptyError,
    VADImplementation,
    VoiceActivityCache,
    VoiceActivityDetector,
    VoiceActivityTrace,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, TestCase

from .multisource import MultiSourceTranscriber, get_multi_source_transcriber
from .multisource_alignment import get_transcription_alignment_block
from .sources import TranscriptionSourceSpec, get_transcription_sources
from .timing import get_segments_with_display_timing

__all__ = ["TranscriptionPipeline", "get_transcription_pipeline"]

logger = getLogger(__name__)

_CONFIDENT_LANGUAGE_MINIMUM_CONFIDENCE = 0.9
"""Minimum LID confidence used to reject a transcription block."""

_CONFIDENT_LANGUAGE_MINIMUM_DURATION_SECONDS = 5.0
"""Minimum high-confidence non-target speech used to reject a block."""

_CONFIDENT_NON_TARGET_LANGUAGE_COVERAGE = 0.8
"""Minimum classified-speech coverage used to reject a non-target block."""

_CONFIDENT_SINGING_COVERAGE = 0.8
"""Minimum corroborating singing and music coverage used to reject a block."""

_FIRERED_TARGET_LANGUAGE_CODES = {
    Language.eng: frozenset({"en"}),
    Language.yue_hans: frozenset({"zh-yue"}),
    Language.yue_hant: frozenset({"zh-yue"}),
    Language.zho_hans: frozenset({"zh-mandarin"}),
    Language.zho_hant: frozenset({"zh-mandarin"}),
}
"""FireRed LID codes accepted for each transcription language."""


class TranscriptionPipeline:
    """Plan speech blocks, merge ASR evidence, and produce timed subtitles."""

    def __init__(
        self,
        *,
        language: Language,
        transcriber: MultiSourceTranscriber,
        alignment_sources: tuple[TranscriptionAlignmentSource, ...],
        audio_event_mode: AudioClassificationMode = AudioClassificationMode.AUTO,
        audio_event_detector: FireRedAudioEventDetector | None = None,
        skip_singing_blocks: bool = False,
        diarization_mode: DiarizationMode = DiarizationMode.AUTO,
        cache_root_path: Path | None = None,
        overwrite_cache: bool = False,
        block_settings: SpeechBlockSettings | None = None,
        block_splitter: SpeechBlockSplitter | None = None,
        block_vad_cache: VoiceActivityCache | None = None,
        block_vad_detector: VoiceActivityDetector | None = None,
        diarizer: Callable[[AudioSegment], SpeakerDiarizationResult] | None = None,
        language_identification_mode: AudioClassificationMode = (
            AudioClassificationMode.AUTO
        ),
        language_identifier: FireRedLanguageIdentifier | None = None,
        skip_non_target_language_blocks: bool = False,
        timing_settings: SubtitleTimingSettings | None = None,
    ):
        """Initialize.

        Arguments:
            language: transcription and output language
            transcriber: configured aligned multi-source transcriber
            alignment_sources: portable descriptors for every expected ASR source
            audio_event_mode: source-wide speech, singing, and music mode
            audio_event_detector: optional configured FireRed audio-event detector
            skip_singing_blocks: whether to omit confidently singing blocks
            diarization_mode: source-wide speaker diarization mode
            cache_root_path: cache root directory path
            overwrite_cache: whether to replace matching generated cache files
            block_settings: optional VAD-derived block configuration
            block_splitter: optional configured VAD-derived block splitter
            block_vad_cache: optional full-source VAD trace cache
            block_vad_detector: optional full-source block-planning VAD
            diarizer: optional configured source-wide speaker diarizer
            language_identification_mode: source-wide spoken-language mode
            language_identifier: optional configured FireRed language identifier
            skip_non_target_language_blocks: whether to omit confidently non-target
                language blocks
            timing_settings: reference-free merged subtitle display timing
        """
        self.language = language
        """Transcription and output language."""
        self.transcriber = transcriber
        """Configured aligned multi-source transcriber."""
        self.alignment_sources = alignment_sources
        """Portable descriptors for every expected ASR source."""
        self.audio_event_mode = audio_event_mode
        """Source-wide speech, singing, and music detection mode."""
        self.audio_event_detector = audio_event_detector
        """Optional FireRed multi-label audio-event detector."""
        self.skip_singing_blocks = skip_singing_blocks
        """Whether to omit blocks whose cores are at least 80% singing and music."""
        if self.audio_event_mode is not AudioClassificationMode.OFF and (
            self.audio_event_detector is None
        ):
            self.audio_event_detector = FireRedAudioEventDetector(
                cache_root_path, overwrite_cache=overwrite_cache
            )
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
        """Voice activity detector used only for block planning and pause evidence."""
        if block_vad_cache is None:
            block_vad_cache = VoiceActivityCache(cache_root_path, overwrite_cache)
        self.block_vad_cache = block_vad_cache
        """Persistent full-source block-planning VAD trace cache."""
        self.diarizer = diarizer
        """Optional source-wide speaker diarizer."""
        if self.diarization_mode is not DiarizationMode.OFF and self.diarizer is None:
            self.diarizer = PyannoteDiarizer(
                cache_root_path, overwrite_cache=overwrite_cache
            )
        self.language_identification_mode = language_identification_mode
        """Source-wide spoken-language identification mode."""
        self.language_identifier = language_identifier
        """Optional FireRed spoken-language identifier."""
        self.skip_non_target_language_blocks = skip_non_target_language_blocks
        """Whether to omit blocks with sustained confident non-target speech."""
        if self.language_identification_mode is not AudioClassificationMode.OFF and (
            self.language_identifier is None
        ):
            self.language_identifier = FireRedLanguageIdentifier(
                cache_root_path, overwrite_cache=overwrite_cache
            )
        if timing_settings is None:
            timing_settings = SubtitleTimingSettings()
        self.timing_settings = timing_settings
        """Reference-free merged subtitle display timing settings."""
        self.last_alignment_artifact: TranscriptionAlignmentArtifact | None = None
        """Portable evidence from the most recent run."""
        self.last_blocks: list[SpeechBlock] = []
        """Most recent stable full-source block plan."""

    def process(
        self,
        audio_series: AudioSeries,
        *,
        start_at_idx: int = 0,
        stop_at_idx: int | None = None,
    ) -> AudioSeries:
        """Transcribe selected VAD-derived source blocks.

        Arguments:
            audio_series: complete source audio without required subtitle events
            start_at_idx: inclusive zero-based block index at which to start
            stop_at_idx: exclusive zero-based block index at which to stop
        Returns:
            merged and timed audio subtitle series
        """
        trace = self._get_voice_activity_trace(audio_series.audio)
        self.last_blocks = self.block_splitter(trace)
        selected_blocks = self._get_selected_blocks(start_at_idx, stop_at_idx)
        if (
            self.transcriber.merger.prune_test_cases
            and selected_blocks != self.last_blocks
        ):
            raise ValueError(
                "Cannot prune aligned merge test cases while processing only a "
                "subset of transcription blocks."
            )
        classification_audio, classification_offset_ms = self._get_classification_audio(
            audio_series.audio, selected_blocks
        )
        audio_events = self._get_audio_events(
            classification_audio, classification_offset_ms
        )
        language_identification = self._get_language_identification(
            classification_audio, classification_offset_ms, trace, selected_blocks
        )
        selected_blocks = self._get_filtered_blocks(
            selected_blocks, audio_events, language_identification
        )
        diarization = self._get_diarization(audio_series.audio, bool(selected_blocks))

        output_segments = []
        alignment_blocks: list[TranscriptionAlignmentBlock] = []
        for block in selected_blocks:
            block_audio = audio_series.audio[
                block.buffered_start_ms : block.buffered_end_ms
            ]
            pause_intervals = self._get_block_pause_intervals(trace, block)
            try:
                block_segments = self.transcriber.transcribe_block(
                    block_audio,
                    audio_events=audio_events,
                    classification_offset_seconds=block.buffered_start_ms / 1000,
                    language_identification=language_identification,
                    pause_intervals_seconds=pause_intervals,
                    voice_activity_trace=trace,
                    voice_activity_offset_seconds=block.buffered_start_ms / 1000,
                    diarization=diarization,
                    diarization_offset_seconds=block.buffered_start_ms / 1000,
                )
            except TranscriptionEmptyError as exc:
                logger.info(
                    f"Transcription block {block.index + 1} contains no transcribed "
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
                    f"Transcription block {block.index + 1} contains no core-owned "
                    "text."
                )
                continue
            block_segments = self._add_voice_activity_scores(block_segments, trace)
            if self.transcriber.last_lexical_alignment is None:
                raise RuntimeError(
                    "Multi-source transcription did not retain its lexical alignment."
                )
            alignment_blocks.append(
                get_transcription_alignment_block(
                    self.transcriber.last_lexical_alignment,
                    block_segments,
                    self.transcriber.alignment_aligner,
                    block_index=block.index + 1,
                    audio_events=audio_events,
                    buffered_end_ms=block.buffered_end_ms,
                    buffered_start_ms=block.buffered_start_ms,
                    core_end_ms=block.end_ms,
                    core_start_ms=block.start_ms,
                    diarization=diarization,
                    first_subtitle_index=len(output_segments) + 1,
                    language_identification=language_identification,
                    pause_intervals_seconds=pause_intervals,
                    source_errors=self.transcriber.last_source_errors,
                    traditionalize=self.language is Language.yue_hant,
                    voice_activity_trace=trace,
                )
            )
            output_segments.extend(block_segments)

        output_segments = get_segments_with_display_timing(
            output_segments, len(audio_series.audio) / 1000, self.timing_settings
        )
        output_segments = [
            segment.model_copy(update={"id": segment_id})
            for segment_id, segment in enumerate(output_segments)
        ]
        alignment_blocks = self._get_blocks_with_display_timing(
            alignment_blocks, output_segments
        )
        self.last_alignment_artifact = TranscriptionAlignmentArtifact(
            language=self.language,
            audio_duration_ms=len(audio_series.audio),
            sources=self.alignment_sources,
            timing=self.timing_settings,
            blocks=tuple(alignment_blocks),
        )
        return get_series_from_segments(output_segments, audio=audio_series.audio)

    @staticmethod
    def _get_blocks_with_display_timing(
        blocks: list[TranscriptionAlignmentBlock], segments: list[TranscribedSegment]
    ) -> list[TranscriptionAlignmentBlock]:
        """Apply globally calculated display bounds to artifact subtitles."""
        subtitles = [subtitle for block in blocks for subtitle in block.subtitles]
        if len(subtitles) != len(segments):
            raise RuntimeError(
                "Alignment subtitle count does not match merged segment count."
            )
        display_bounds = {
            subtitle.index: (round(segment.start * 1000), round(segment.end * 1000))
            for subtitle, segment in zip(subtitles, segments, strict=True)
        }
        return [
            block.model_copy(
                update={
                    "subtitles": tuple(
                        subtitle.model_copy(
                            update={
                                "start_ms": display_bounds[subtitle.index][0],
                                "end_ms": display_bounds[subtitle.index][1],
                            }
                        )
                        for subtitle in block.subtitles
                    )
                }
            )
            for block in blocks
        ]

    def plan_blocks(self, audio_series: AudioSeries) -> tuple[SpeechBlock, ...]:
        """Get the stable VAD block plan without running ASR or the merger.

        Arguments:
            audio_series: complete source audio
        Returns:
            VAD-derived blocks in source order
        """
        trace = self._get_voice_activity_trace(audio_series.audio)
        self.last_blocks = self.block_splitter(trace)
        return tuple(self.last_blocks)

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

    def _get_filtered_blocks(
        self,
        blocks: list[SpeechBlock],
        audio_events: AudioEventDetectionResult | None,
        language_identification: LanguageIdentificationResult | None,
    ) -> list[SpeechBlock]:
        """Remove blocks confidently classified outside transcription scope."""
        output_blocks = []
        target_language_codes = _FIRERED_TARGET_LANGUAGE_CODES[self.language]
        non_target_language_codes = set()
        if language_identification is not None:
            non_target_language_codes = {
                span.language
                for span in language_identification.spans
                if span.language not in target_language_codes
            }
        for block in blocks:
            start = block.start_ms / 1000
            end = block.end_ms / 1000
            reasons = []
            if self.skip_singing_blocks and audio_events is not None:
                singing_coverage = audio_events.get_coverage(
                    AudioEvent.SINGING, start, end
                )
                music_coverage = audio_events.get_coverage(AudioEvent.MUSIC, start, end)
                if (
                    singing_coverage >= _CONFIDENT_SINGING_COVERAGE
                    and music_coverage >= _CONFIDENT_SINGING_COVERAGE
                ):
                    reasons.append(
                        f"{singing_coverage:.1%} singing and "
                        f"{music_coverage:.1%} music coverage"
                    )
            if (
                self.skip_non_target_language_blocks
                and language_identification is not None
            ):
                non_target_coverage = language_identification.get_coverage(
                    start,
                    end,
                    languages=non_target_language_codes,
                    minimum_confidence=_CONFIDENT_LANGUAGE_MINIMUM_CONFIDENCE,
                )
                non_target_duration = language_identification.get_duration(
                    start,
                    end,
                    languages=non_target_language_codes,
                    minimum_confidence=_CONFIDENT_LANGUAGE_MINIMUM_CONFIDENCE,
                )
                if (
                    non_target_coverage >= _CONFIDENT_NON_TARGET_LANGUAGE_COVERAGE
                    and non_target_duration
                    >= _CONFIDENT_LANGUAGE_MINIMUM_DURATION_SECONDS
                ):
                    reasons.append(
                        f"{non_target_coverage:.1%} confidently non-target "
                        f"classified speech over {non_target_duration:.1f}s"
                    )
            if reasons:
                logger.info(
                    f"Skipping transcription block {block.index + 1} "
                    f"({block.start_ms / 1000:.3f}-{block.end_ms / 1000:.3f}s): "
                    f"{', '.join(reasons)}."
                )
                continue
            output_blocks.append(block)
        return output_blocks

    def _get_audio_events(
        self, audio: AudioSegment | None, offset_ms: int
    ) -> AudioEventDetectionResult | None:
        """Get optional FireRed audio events over the selected block span."""
        if self.audio_event_mode is AudioClassificationMode.OFF or audio is None:
            return None
        assert self.audio_event_detector is not None
        try:
            return self.audio_event_detector(audio, offset_seconds=offset_ms / 1000)
        except AudioClassificationError as exc:
            if self.audio_event_mode is AudioClassificationMode.ON:
                raise
            logger.warning(
                f"Audio-event detection is unavailable; continuing without "
                f"singing or music evidence: {exc}"
            )
            return None

    def _get_language_identification(
        self,
        audio: AudioSegment | None,
        offset_ms: int,
        trace: VoiceActivityTrace,
        selected_blocks: list[SpeechBlock],
    ) -> LanguageIdentificationResult | None:
        """Get optional FireRed LID over selected VAD speech intervals."""
        if (
            self.language_identification_mode is AudioClassificationMode.OFF
            or audio is None
        ):
            return None
        assert self.language_identifier is not None
        speech_intervals = self._get_classification_speech_intervals(
            trace, selected_blocks, offset_ms, len(audio)
        )
        try:
            return self.language_identifier(
                audio, speech_intervals, offset_seconds=offset_ms / 1000
            )
        except AudioClassificationError as exc:
            if self.language_identification_mode is AudioClassificationMode.ON:
                raise
            logger.warning(
                f"Language identification is unavailable; continuing without "
                f"language evidence: {exc}"
            )
            return None

    @staticmethod
    def _get_classification_audio(
        audio: AudioSegment, selected_blocks: list[SpeechBlock]
    ) -> tuple[AudioSegment | None, int]:
        """Get the smallest contiguous source slice covering selected buffers."""
        if not selected_blocks:
            return None, 0
        start_ms = min(block.buffered_start_ms for block in selected_blocks)
        end_ms = max(block.buffered_end_ms for block in selected_blocks)
        return audio[start_ms:end_ms], start_ms

    def _get_classification_speech_intervals(
        self,
        trace: VoiceActivityTrace,
        selected_blocks: list[SpeechBlock],
        offset_ms: int,
        duration_ms: int,
    ) -> tuple[tuple[int, int], ...]:
        """Clip block-planning speech intervals to the classification slice."""
        if not selected_blocks:
            return ()
        source_end_ms = offset_ms + duration_ms
        intervals = []
        for start_ms, end_ms in self.block_vad_detector.get_speech_intervals(trace):
            if end_ms <= offset_ms:
                continue
            if start_ms >= source_end_ms:
                break
            intervals.append(
                (
                    max(offset_ms, start_ms) - offset_ms,
                    min(source_end_ms, end_ms) - offset_ms,
                )
            )
        return tuple(intervals)

    def _get_block_pause_intervals(
        self, trace: VoiceActivityTrace, block: SpeechBlock
    ) -> tuple[tuple[float, float], ...]:
        """Get block-local complements of block-planning speech intervals."""
        pause_intervals = []
        pause_start_ms = block.buffered_start_ms
        for (
            speech_start_ms,
            speech_end_ms,
        ) in self.block_vad_detector.get_speech_intervals(trace):
            if speech_end_ms <= block.buffered_start_ms:
                continue
            if speech_start_ms >= block.buffered_end_ms:
                break
            clipped_start_ms = max(block.buffered_start_ms, speech_start_ms)
            clipped_end_ms = min(block.buffered_end_ms, speech_end_ms)
            if clipped_start_ms > pause_start_ms:
                pause_intervals.append(
                    (
                        (pause_start_ms - block.buffered_start_ms) / 1000,
                        (clipped_start_ms - block.buffered_start_ms) / 1000,
                    )
                )
            pause_start_ms = max(pause_start_ms, clipped_end_ms)
        if pause_start_ms < block.buffered_end_ms:
            pause_intervals.append(
                (
                    (pause_start_ms - block.buffered_start_ms) / 1000,
                    (block.buffered_end_ms - block.buffered_start_ms) / 1000,
                )
            )
        return tuple(pause_intervals)

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
                f"Invalid transcription block range [{start_at_idx}, {stop_at_idx}) "
                f"for {block_count} available blocks."
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


def get_transcription_pipeline(
    language: Language,
    *,
    audio_event_mode: AudioClassificationMode = AudioClassificationMode.AUTO,
    skip_singing_blocks: bool = False,
    source_specs: tuple[TranscriptionSourceSpec, ...] | None = None,
    demucs_mode: DemucsMode = DemucsMode.OFF,
    diarization_mode: DiarizationMode = DiarizationMode.AUTO,
    language_identification_mode: AudioClassificationMode = (
        AudioClassificationMode.AUTO
    ),
    skip_non_target_language_blocks: bool = False,
    vad_implementation: VADImplementation = VADImplementation.SILERO,
    block_vad_implementation: VADImplementation = VADImplementation.PYANNOTE,
    mlx_audio_token_limit_guard: bool = True,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    no_op: bool = False,
    aligned_merge_json_path: Path | None = None,
    prune_test_cases: bool = False,
    aligned_merge_test_cases: list[TestCase] | None = None,
    timing_settings: SubtitleTimingSettings | None = None,
) -> TranscriptionPipeline:
    """Get a production aligned multi-source transcription pipeline.

    Arguments:
        language: transcription and output language
        audio_event_mode: source-wide speech, singing, and music mode
        skip_singing_blocks: whether to omit confidently singing blocks
        source_specs: optional future-extensible ASR source registry override
        demucs_mode: source-level vocal-separation mode
        diarization_mode: source-wide speaker diarization mode
        language_identification_mode: source-wide spoken-language mode
        skip_non_target_language_blocks: whether to omit confidently non-target
            language blocks
        vad_implementation: backend VAD implementation retained for cache identity
        block_vad_implementation: VAD used for block planning and pause evidence
        mlx_audio_token_limit_guard: whether to guard MiMo generation length
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching generated cache files
        provider: provider to use for consensus queries
        additional_context: additional context for the consensus prompt
        no_op: select the first source instead of querying an LLM
        aligned_merge_json_path: aligned-merge test-case JSON path
        prune_test_cases: whether to remove unencountered merge test cases
        aligned_merge_test_cases: preloaded aligned-merge test cases
        timing_settings: reference-free merged subtitle display timing
    Returns:
        configured production transcription pipeline
    """
    source_transcribers, alignment_sources = get_transcription_sources(
        language,
        source_specs=source_specs,
        demucs_mode=demucs_mode,
        mlx_audio_token_limit_guard=mlx_audio_token_limit_guard,
        vad_implementation=vad_implementation,
        cache_root_path=cache_root_path,
        overwrite_cache=overwrite_cache,
    )
    transcriber = get_multi_source_transcriber(
        language,
        source_transcribers,
        provider=provider,
        cache_root_path=cache_root_path,
        overwrite_cache=overwrite_cache,
        additional_context=additional_context,
        no_op=no_op,
        current_test_cases_path=aligned_merge_json_path,
        prune_test_cases=prune_test_cases,
        shared_test_cases=aligned_merge_test_cases,
    )
    block_settings = SpeechBlockSettings()
    block_vad_detector = VoiceActivityDetector(
        block_vad_implementation,
        threshold=block_settings.voice_activity_threshold,
        min_speech_duration_seconds=block_settings.min_speech_duration_seconds,
        min_silence_duration_seconds=0.0,
        padding_seconds=0.0,
    )
    return TranscriptionPipeline(
        language=language,
        transcriber=transcriber,
        alignment_sources=alignment_sources,
        audio_event_mode=audio_event_mode,
        skip_singing_blocks=skip_singing_blocks,
        diarization_mode=diarization_mode,
        language_identification_mode=language_identification_mode,
        skip_non_target_language_blocks=skip_non_target_language_blocks,
        cache_root_path=cache_root_path,
        overwrite_cache=overwrite_cache,
        block_settings=block_settings,
        block_vad_detector=block_vad_detector,
        timing_settings=timing_settings,
    )
