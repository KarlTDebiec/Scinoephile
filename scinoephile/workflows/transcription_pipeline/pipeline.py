#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reference-free aligned multi-source transcription pipeline."""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import asdict
from enum import StrEnum
from hashlib import sha256
from logging import getLogger
from typing import cast

from pydub import AudioSegment

from scinoephile.analysis.transcription.artifact import (
    AlignmentArtifact,
    AlignmentBlock,
    AlignmentSource,
    TimingSettings,
)
from scinoephile.analysis.transcription.manifest import (
    ProcessorIdentity,
    RunBlock,
    RunManifest,
)
from scinoephile.analysis.transcription.timing import retime_alignment
from scinoephile.audio.classification import (
    AudioClassificationError,
    AudioEventDetectionResult,
    FireRedAudioEventDetector,
    FireRedLanguageIdentifier,
    LanguageIdentificationResult,
)
from scinoephile.audio.diarization import (
    PyannoteDiarizer,
    SpeakerDiarizationError,
    SpeakerDiarizationResult,
)
from scinoephile.audio.speaker_assignment import assign_speakers
from scinoephile.audio.subtitles import AudioSeries, get_series_from_segments
from scinoephile.audio.transcription import TranscribedSegment, TranscriptionEmptyError
from scinoephile.audio.vad import (
    SpeechBlock,
    SpeechBlockSplitter,
    VoiceActivityCache,
    VoiceActivityDetector,
    VoiceActivityTrace,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.workflows.multisource_transcription.transcriber import (
    MultiSourceTranscriber,
)
from scinoephile.workflows.transcription_alignment import (
    build_transcription_alignment_block,
)

__all__ = ["AudioAnalysisMode", "TranscriptionPipeline"]

logger = getLogger(__name__)


class AudioAnalysisMode(StrEnum):
    """Optional source-wide audio-analysis behavior."""

    AUTO = "auto"
    """Use analysis when available and continue without it after failure."""
    ON = "on"
    """Require successful analysis."""
    OFF = "off"
    """Do not run analysis."""


class TranscriptionPipeline:
    """Plan speech blocks, merge ASR evidence, and produce timed subtitles."""

    def __init__(
        self,
        *,
        language: Language,
        transcriber: MultiSourceTranscriber,
        alignment_sources: tuple[AlignmentSource, ...],
        block_splitter: SpeechBlockSplitter,
        block_vad_cache: VoiceActivityCache,
        block_vad_detector: VoiceActivityDetector,
        audio_event_mode: AudioAnalysisMode = AudioAnalysisMode.AUTO,
        audio_event_detector: FireRedAudioEventDetector | None = None,
        diarization_mode: AudioAnalysisMode = AudioAnalysisMode.AUTO,
        diarizer: PyannoteDiarizer | None = None,
        language_identification_mode: AudioAnalysisMode = AudioAnalysisMode.AUTO,
        language_identifier: FireRedLanguageIdentifier | None = None,
        timing_settings: TimingSettings | None = None,
    ):
        """Initialize.

        Arguments:
            language: transcription and output language
            transcriber: configured aligned multi-source transcriber
            alignment_sources: portable descriptors for every expected ASR source
            block_splitter: configured VAD-derived block splitter
            block_vad_cache: full-source VAD trace cache
            block_vad_detector: full-source block-planning VAD
            audio_event_mode: source-wide speech, singing, and music mode
            audio_event_detector: optional configured FireRed audio-event detector
            diarization_mode: source-wide speaker diarization mode
            diarizer: optional configured source-wide speaker diarizer
            language_identification_mode: source-wide spoken-language mode
            language_identifier: optional configured FireRed language identifier
            timing_settings: reference-free merged subtitle display timing
        Raises:
            ValueError: if sources are inconsistent or an enabled analysis mode lacks
              its dependency
        """
        alignment_source_names = tuple(source.name for source in alignment_sources)
        transcriber_source_names = tuple(transcriber.transcribers)
        if alignment_source_names != transcriber_source_names:
            raise ValueError(
                "Alignment sources must match transcription sources in stable order."
            )
        self.language = language
        """Transcription and output language."""
        self.transcriber = transcriber
        """Configured aligned multi-source transcriber."""
        self.alignment_sources = alignment_sources
        """Portable descriptors for every expected ASR source."""
        self.block_splitter = block_splitter
        """Full-source VAD trace block splitter."""
        self.block_vad_cache = block_vad_cache
        """Persistent full-source block-planning VAD trace cache."""
        self.block_vad_detector = block_vad_detector
        """Voice activity detector used only for block planning and pause evidence."""
        self.audio_event_mode = audio_event_mode
        """Source-wide speech, singing, and music detection mode."""
        self.audio_event_detector = audio_event_detector
        """Optional FireRed multi-label audio-event detector."""
        if self.audio_event_mode is not AudioAnalysisMode.OFF and (
            self.audio_event_detector is None
        ):
            raise ValueError("Audio-event mode requires an audio-event detector.")
        self.diarization_mode = diarization_mode
        """Source-wide speaker diarization mode."""
        self.diarizer = diarizer
        """Optional source-wide speaker diarizer."""
        if self.diarization_mode is not AudioAnalysisMode.OFF and self.diarizer is None:
            raise ValueError("Diarization mode requires a diarizer.")
        self.language_identification_mode = language_identification_mode
        """Source-wide spoken-language identification mode."""
        self.language_identifier = language_identifier
        """Optional FireRed spoken-language identifier."""
        if self.language_identification_mode is not AudioAnalysisMode.OFF and (
            self.language_identifier is None
        ):
            raise ValueError(
                "Language-identification mode requires a language identifier."
            )
        if timing_settings is None:
            timing_settings = TimingSettings()
        self.timing_settings = timing_settings
        """Reference-free merged subtitle display timing settings."""
        self.last_alignment_artifact: AlignmentArtifact | None = None
        """Portable evidence from the most recent run."""
        self.last_run_manifest: RunManifest | None = None
        """Reproducibility provenance from the most recent run."""
        self.last_blocks: list[SpeechBlock] = []
        """Most recent stable full-source block plan."""

    @property
    def block_vad_identity(self) -> CacheIdentity:
        """Get the block-planning configuration recorded in run manifests."""
        return cast(
            CacheIdentity,
            json.loads(
                json.dumps(
                    {
                        "detector": self.block_vad_detector.cache_identity,
                        "splitter": asdict(self.block_splitter.settings),
                    },
                    allow_nan=False,
                    ensure_ascii=False,
                )
            ),
        )

    @property
    def processor_identity(self) -> ProcessorIdentity:
        """Get the consensus processor configuration recorded in run manifests."""
        processor = self.transcriber.processor
        return ProcessorIdentity(
            operation=processor.test_case_cls.operation,
            prompt_name=processor.prompt.name,
            system_prompt_sha256=sha256(
                processor.queryer.system_prompt.encode("utf-8")
            ).hexdigest(),
            provider_identity=processor.queryer.provider.cache_identity,
            no_op=processor.queryer.no_op,
        )

    def plan_blocks(self, audio_series: AudioSeries) -> tuple[SpeechBlock, ...]:
        """Get the stable VAD block plan without running ASR or consensus.

        Arguments:
            audio_series: complete source audio
        Returns:
            VAD-derived blocks in source order
        """
        self.last_blocks = []
        trace = self._get_voice_activity_trace(audio_series.audio)
        self.last_blocks = self.block_splitter(trace)
        return tuple(self.last_blocks)

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

        Raises:
            ValueError: if a value is invalid
            RuntimeError: if the operation cannot be completed
        """
        self.last_alignment_artifact = None
        self.last_run_manifest = None
        self.last_blocks = []
        trace = self._get_voice_activity_trace(audio_series.audio)
        self.last_blocks = self.block_splitter(trace)
        selected_blocks = self._get_selected_blocks(start_at_idx, stop_at_idx)
        speech_intervals_ms = tuple(self.block_vad_detector.get_speech_intervals(trace))
        block_records: list[RunBlock] = []
        if (
            self.transcriber.processor.prune_test_cases
            and selected_blocks != self.last_blocks
        ):
            raise ValueError(
                "Cannot prune transcription test cases while processing only a "
                "subset of transcription blocks."
            )
        analysis_audio = audio_series.audio if selected_blocks else None
        audio_events = self._get_audio_events(analysis_audio)
        language_identification = self._get_language_identification(
            analysis_audio, speech_intervals_ms
        )
        diarization = self._get_diarization(audio_series.audio, bool(selected_blocks))

        output_segments = []
        alignment_blocks: list[AlignmentBlock] = []
        for block in selected_blocks:
            block_index = block.index + 1
            block_audio = audio_series.audio[
                block.buffered_start_ms : block.buffered_end_ms
            ]
            pause_intervals = self._get_block_pause_intervals(
                speech_intervals_ms, block
            )
            try:
                block_segments = self.transcriber.transcribe_block(
                    block_audio,
                    audio_events=audio_events,
                    language_identification=language_identification,
                    pause_intervals_seconds=pause_intervals,
                    source_offset_seconds=block.buffered_start_ms / 1000,
                    voice_activity_trace=trace,
                    diarization=diarization,
                )
            except TranscriptionEmptyError as exc:
                reason = str(exc).strip() or type(exc).__name__
                block_records.append(
                    RunBlock(
                        index=block_index,
                        status="empty",
                        reason=reason,
                        source_cache_key_sha256s=dict(
                            self.transcriber.last_source_cache_key_sha256s
                        ),
                        query_key_sha256s=self.transcriber.last_query_key_sha256s,
                    )
                )
                logger.info(
                    f"Transcription block {block_index} contains no transcribed "
                    f"speech: {reason}"
                )
                continue
            source_cache_key_sha256s = dict(
                self.transcriber.last_source_cache_key_sha256s
            )
            query_key_sha256s = self.transcriber.last_query_key_sha256s
            if diarization is not None:
                block_segments = assign_speakers(
                    diarization,
                    block_segments,
                    offset_seconds=block.buffered_start_ms / 1000,
                )
            block_segments = self._get_offset_core_segments(block_segments, block)
            block_segments = [
                segment for segment in block_segments if segment.text.strip()
            ]
            if not block_segments:
                block_records.append(
                    RunBlock(
                        index=block_index,
                        status="no-core-text",
                        reason="Merged text was outside the block core.",
                        source_cache_key_sha256s=source_cache_key_sha256s,
                        query_key_sha256s=query_key_sha256s,
                    )
                )
                logger.info(
                    f"Transcription block {block_index} contains no core-owned text."
                )
                continue
            block_segments = self._add_voice_activity_scores(block_segments, trace)
            if self.transcriber.last_lexical_alignment is None:
                raise RuntimeError(
                    "Multi-source transcription did not retain its lexical alignment."
                )
            alignment_blocks.append(
                build_transcription_alignment_block(
                    self.transcriber.last_lexical_alignment,
                    block_segments,
                    self.transcriber.aligner,
                    speech_block=block,
                    audio_events=audio_events,
                    diarization=diarization,
                    first_subtitle_index=len(output_segments) + 1,
                    language_identification=language_identification,
                    pause_intervals_seconds=pause_intervals,
                    source_errors=self.transcriber.last_source_errors,
                    timing_sources=self.transcriber.last_timing_sources,
                    traditionalize=self.language is Language.yue_hant,
                    voice_activity_trace=trace,
                )
            )
            block_records.append(
                RunBlock(
                    index=block_index,
                    status="transcribed",
                    source_cache_key_sha256s=source_cache_key_sha256s,
                    query_key_sha256s=query_key_sha256s,
                )
            )
            output_segments.extend(block_segments)

        self.last_alignment_artifact = retime_alignment(
            AlignmentArtifact(
                language=self.language,
                audio_duration_ms=len(audio_series.audio),
                sources=self.alignment_sources,
                timing=self.timing_settings,
                blocks=tuple(alignment_blocks),
            ),
            self.timing_settings,
        )
        alignment_subtitles = [
            subtitle
            for alignment_block in self.last_alignment_artifact.blocks
            for subtitle in alignment_block.subtitles
        ]
        if len(alignment_subtitles) != len(output_segments):
            raise RuntimeError(
                "Alignment subtitle count does not match merged segment count."
            )
        output_segments = [
            segment.model_copy(
                deep=True,
                update={
                    "id": segment_id,
                    "start": subtitle.start_ms / 1000,
                    "end": subtitle.end_ms / 1000,
                },
            )
            for segment_id, (segment, subtitle) in enumerate(
                zip(output_segments, alignment_subtitles, strict=True)
            )
        ]
        self.last_run_manifest = self._build_run_manifest(
            audio_series.audio, tuple(block_records)
        )
        return get_series_from_segments(output_segments, audio=audio_series.audio)

    def _add_voice_activity_scores(
        self, segments: list[TranscribedSegment], trace: VoiceActivityTrace
    ) -> list[TranscribedSegment]:
        """Attach full-source VAD summaries to source-timed words.

        Arguments:
            segments: source-timed transcription segments
            trace: full-source voice-activity score trace
        Returns:
            copied segments whose words include VAD summaries
        """
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

    def _build_run_manifest(
        self, audio: AudioSegment, blocks: tuple[RunBlock, ...]
    ) -> RunManifest:
        """Build the compact manifest for the finished run.

        Arguments:
            audio: complete decoded source audio
            blocks: selected VAD block outcomes and cache identities
        Returns:
            compact run manifest

        Raises:
            RuntimeError: if the operation cannot be completed
        """
        if self.last_alignment_artifact is None:
            raise RuntimeError("Cannot build run provenance without an artifact.")
        return RunManifest(
            language=self.language,
            audio_sha256=sha256(audio.raw_data).hexdigest(),
            audio_duration_ms=len(audio),
            audio_channels=audio.channels,
            audio_frame_rate=audio.frame_rate,
            audio_sample_width=audio.sample_width,
            block_vad_identity=self.block_vad_identity,
            planned_block_count=len(self.last_blocks),
            blocks=blocks,
            processor=self.processor_identity,
            alignment_sha256=self.last_alignment_artifact.sha256,
        )

    def _get_audio_events(
        self, audio: AudioSegment | None
    ) -> AudioEventDetectionResult | None:
        """Get optional FireRed audio events over the complete source.

        Arguments:
            audio: complete source audio, if the range contains blocks
        Returns:
            audio events, or None when disabled or unavailable in auto mode

        Raises:
            AudioClassificationError: if the operation fails
        """
        if self.audio_event_mode is AudioAnalysisMode.OFF or audio is None:
            return None
        assert self.audio_event_detector is not None
        try:
            return self.audio_event_detector(audio)
        except AudioClassificationError as exc:
            if self.audio_event_mode is AudioAnalysisMode.ON:
                raise
            logger.warning(
                f"Audio-event detection is unavailable; continuing without "
                f"singing or music evidence: {exc}"
            )
            return None

    def _get_diarization(
        self, audio: AudioSegment, has_selected_blocks: bool
    ) -> SpeakerDiarizationResult | None:
        """Get optional source-wide speaker diarization once per run.

        Arguments:
            audio: complete source audio
            has_selected_blocks: whether the requested range contains blocks
        Returns:
            speaker diarization, or None when disabled or unavailable in auto mode

        Raises:
            SpeakerDiarizationError: if the operation fails
        """
        if self.diarization_mode is AudioAnalysisMode.OFF or not has_selected_blocks:
            return None
        assert self.diarizer is not None
        try:
            return self.diarizer(audio)
        except SpeakerDiarizationError as exc:
            if self.diarization_mode is AudioAnalysisMode.ON:
                raise
            logger.warning(
                f"Speaker diarization is unavailable; continuing without speaker "
                f"evidence: {exc}"
            )
            return None

    def _get_language_identification(
        self, audio: AudioSegment | None, speech_intervals_ms: Sequence[tuple[int, int]]
    ) -> LanguageIdentificationResult | None:
        """Get optional FireRed LID over complete-source VAD speech intervals.

        Arguments:
            audio: complete source audio, if the range contains blocks
            speech_intervals_ms: source-timeline speech intervals
        Returns:
            language identification, or None when disabled or unavailable in auto mode

        Raises:
            AudioClassificationError: if the operation fails
        """
        if self.language_identification_mode is AudioAnalysisMode.OFF or audio is None:
            return None
        assert self.language_identifier is not None
        try:
            return self.language_identifier(audio, speech_intervals_ms)
        except AudioClassificationError as exc:
            if self.language_identification_mode is AudioAnalysisMode.ON:
                raise
            logger.warning(
                f"Language identification is unavailable; continuing without "
                f"language evidence: {exc}"
            )
            return None

    def _get_selected_blocks(
        self, start_at_idx: int, stop_at_idx: int | None
    ) -> list[SpeechBlock]:
        """Validate and select a half-open range from the stable block plan.

        Arguments:
            start_at_idx: inclusive zero-based block index
            stop_at_idx: exclusive zero-based block index, or None for the end
        Returns:
            selected stable speech blocks
        Raises:
            ScinoephileError: if the selected range is invalid
        """
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
        """Load or infer the full-source block-planning VAD trace.

        Arguments:
            audio: complete source audio
        Returns:
            cached or newly inferred frame-level VAD scores
        """
        metadata = self.block_vad_detector.trace_cache_identity
        trace = self.block_vad_cache.load(audio, metadata)
        if trace is not None:
            return trace
        logger.info("Running full-source voice activity detection.")
        trace = self.block_vad_detector.get_trace(audio)
        self.block_vad_cache.save(audio, metadata, trace)
        return trace

    @staticmethod
    def _get_block_pause_intervals(
        speech_intervals_ms: Sequence[tuple[int, int]], block: SpeechBlock
    ) -> tuple[tuple[float, float], ...]:
        """Get block-local complements of block-planning speech intervals.

        Arguments:
            speech_intervals_ms: source-timeline speech intervals
            block: block whose buffered range bounds the complements
        Returns:
            block-local pause intervals in seconds
        """
        pause_intervals = []
        pause_start_ms = block.buffered_start_ms
        for speech_start_ms, speech_end_ms in speech_intervals_ms:
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
        """Map block-local timings to the source and retain core-owned content.

        Arguments:
            segments: block-local transcription segments
            block: source-timeline buffered and core bounds
        Returns:
            source-timed segments whose midpoints belong to the block core
        """
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
