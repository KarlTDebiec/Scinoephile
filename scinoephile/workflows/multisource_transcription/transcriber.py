#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Multi-source transcription orchestration."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from logging import getLogger

from pydub import AudioSegment

from scinoephile.analysis.alignment.timed_msa.aligner import Aligner
from scinoephile.analysis.alignment.timed_msa.alignment import Alignment
from scinoephile.analysis.alignment.timed_msa.models import Column
from scinoephile.analysis.transcription.artifact import TimingSource
from scinoephile.audio.classification import (
    AudioEventDetectionResult,
    LanguageIdentificationResult,
)
from scinoephile.audio.diarization.models import SpeakerDiarizationResult
from scinoephile.audio.transcription import (
    CtcAligner,
    TranscribedSegment,
    Transcriber,
    TranscriptionEmptyError,
    TranscriptionError,
)
from scinoephile.audio.transcription.alignment_sequence import (
    get_transcription_sequence,
)
from scinoephile.audio.vad.trace import VoiceActivityTrace
from scinoephile.core import Language, ScinoephileError
from scinoephile.lang.yue.transcription.token_similarity import YueTokenSimilarity
from scinoephile.llms.transcription import TranscriptionProcessor, TranscriptionSource
from scinoephile.workflows.transcription_alignment import render_transcription_alignment

from .quality import get_source_quality_issue
from .timing import get_timed_request_segments

__all__ = ["MultiSourceTranscriber"]

logger = getLogger(__name__)


class MultiSourceTranscriber:
    """Align ASR evidence, derive consensus, and recover subtitle timings."""

    def __init__(
        self,
        *,
        language: Language,
        transcribers: Mapping[str, Transcriber],
        processor: TranscriptionProcessor,
        aligner: Aligner | None = None,
        ctc_aligner: CtcAligner | None = None,
    ):
        """Initialize.

        Arguments:
            language: transcription and output language
            transcribers: named equal-status ASR sources
            processor: aligned consensus and subtitle-boundary processor
            aligner: multiple-sequence character aligner
            ctc_aligner: aligner used to recover final consensus timings
        Raises:
            ValueError: if there are too few named transcription sources
        """
        if len(transcribers) < 2:
            raise ValueError(
                "Multi-source transcription requires at least two sources."
            )
        if any(not name.strip() for name in transcribers):
            raise ValueError("Transcription source names must be nonblank.")
        self.language = language
        """Transcription and output language."""
        self.transcribers = dict(transcribers)
        """Named equal-status ASR sources in stable query order."""
        self.processor = processor
        """Aligned consensus and subtitle-boundary processor."""
        if aligner is None:
            aligner = Aligner(YueTokenSimilarity())
        self.aligner = aligner
        """Multiple-sequence character aligner."""
        if ctc_aligner is None:
            ctc_aligner = CtcAligner(language)
        self.ctc_aligner = ctc_aligner
        """Aligner used to recover final consensus timings."""
        self.last_alignment: Alignment | None = None
        """Latest aligned ASR evidence with timed pauses."""
        self.last_lexical_alignment: Alignment | None = None
        """Latest multi-ASR alignment before timed pauses are inserted."""
        self.last_sources: dict[str, list[TranscribedSegment]] = {}
        """Latest successful raw ASR source outputs."""
        self.last_source_errors: dict[str, str] = {}
        """Latest tolerated source failures keyed by stable source name."""
        self.last_timing_sources: dict[int, TimingSource] = {}
        """Final block-local segment IDs mapped to their timing origins."""

    def __call__(self, audio: AudioSegment) -> list[TranscribedSegment]:
        """Transcribe audio without optional analysis evidence.

        Arguments:
            audio: complete padded block audio
        Returns:
            final consensus subtitles with block-local timings
        """
        return self.transcribe_block(audio)

    def merge(
        self,
        sources: Mapping[str, Sequence[TranscribedSegment]],
        audio: AudioSegment,
        *,
        audio_events: AudioEventDetectionResult | None = None,
        diarization: SpeakerDiarizationResult | None = None,
        language_identification: LanguageIdentificationResult | None = None,
        pause_intervals_seconds: Sequence[tuple[float, float]] = (),
        source_offset_seconds: float = 0.0,
        voice_activity_trace: VoiceActivityTrace | None = None,
    ) -> list[TranscribedSegment]:
        """Merge timestamped sources and recover consensus subtitle timings.

        Arguments:
            sources: named equal-status timestamped transcription sources
            audio: original block audio corresponding to local source timings
            audio_events: optional source-wide FireRed audio-event timeline
            diarization: optional source-wide exclusive speaker timeline
            language_identification: optional source-wide FireRed language timeline
            pause_intervals_seconds: block-local VAD silence intervals
            source_offset_seconds: source time corresponding to block-local zero
            voice_activity_trace: optional source-wide VAD score trace
        Returns:
            final consensus subtitles with block-local CTC timings
        Raises:
            ScinoephileError: if fewer than two named sources are provided
            TranscriptionEmptyError: if source or consensus text is unusable
        """
        self.last_timing_sources = {}
        if len(sources) < 2:
            raise ScinoephileError(
                "Multi-source transcription requires at least two sources."
            )
        if len(audio) <= 0:
            raise TranscriptionEmptyError(
                "Cannot merge transcription evidence for empty audio."
            )

        sequences = tuple(
            get_transcription_sequence(name, segments)
            for name, segments in sources.items()
        )
        if any(not sequence.tokens for sequence in sequences):
            raise TranscriptionEmptyError(
                "Timed transcription sources contain no usable aligned text."
            )
        alignment = self.aligner(sequences)
        self.last_lexical_alignment = alignment
        alignment = alignment.with_pauses(
            pause_intervals_seconds=pause_intervals_seconds,
            source_names=alignment.source_names,
        )
        self.last_alignment = alignment
        rendered = render_transcription_alignment(
            alignment,
            audio_events=audio_events,
            diarization=diarization,
            language_identification=language_identification,
            source_offset_seconds=source_offset_seconds,
            traditionalize=self.language is Language.yue_hant,
            voice_activity_trace=voice_activity_trace,
        )
        request_results = self.processor.process_requests(
            [
                TranscriptionSource(name=row.name, text=row.text)
                for row in rendered.rows
            ],
            rendered.speaker,
            language=rendered.language,
            music=rendered.music,
            singing=rendered.singing,
        )
        if not any(result.answer.transcript.strip() for result in request_results):
            raise TranscriptionEmptyError(
                "Aligned multi-source transcription produced no usable text."
            )
        segments, self.last_timing_sources = get_timed_request_segments(
            audio, alignment, request_results, self.ctc_aligner
        )
        return segments

    def transcribe_block(
        self,
        audio: AudioSegment,
        *,
        audio_events: AudioEventDetectionResult | None = None,
        diarization: SpeakerDiarizationResult | None = None,
        language_identification: LanguageIdentificationResult | None = None,
        pause_intervals_seconds: Sequence[tuple[float, float]] = (),
        source_offset_seconds: float = 0.0,
        voice_activity_trace: VoiceActivityTrace | None = None,
    ) -> list[TranscribedSegment]:
        """Transcribe one padded block using optional audio-analysis evidence.

        Arguments:
            audio: complete padded block audio
            audio_events: optional source-wide FireRed audio-event timeline
            diarization: optional source-wide exclusive speaker timeline
            language_identification: optional source-wide FireRed language timeline
            pause_intervals_seconds: block-local VAD silence intervals
            source_offset_seconds: source time corresponding to block-local zero
            voice_activity_trace: optional source-wide VAD score trace
        Returns:
            final consensus subtitles with block-local CTC timings
        Raises:
            TranscriptionEmptyError: if no ASR source provides usable text
        """
        self.last_alignment = None
        self.last_lexical_alignment = None
        self.last_sources = {}
        self.last_source_errors = {}
        self.last_timing_sources = {}
        successful_sources: dict[str, list[TranscribedSegment]] = {}
        source_errors = {}
        for source_name, transcriber in self.transcribers.items():
            try:
                segments = transcriber(audio)
            except TranscriptionError as exc:
                error = str(exc).strip() or type(exc).__name__
                source_errors[source_name] = error
                logger.info(
                    f"Transcription source {source_name!r} failed and will be "
                    f"excluded from this block: {error}"
                )
                continue
            quality_issue = get_source_quality_issue(
                segments, audio_duration_seconds=len(audio) / 1000
            )
            if quality_issue is not None:
                source_errors[source_name] = quality_issue
                logger.info(
                    f"Transcription source {source_name!r} was rejected and will be "
                    f"excluded from this block: {quality_issue}"
                )
                continue
            successful_sources[source_name] = segments

        self.last_sources = successful_sources
        self.last_source_errors = source_errors
        if not successful_sources:
            raise TranscriptionEmptyError(
                "All transcription sources produced empty output."
            )
        if len(successful_sources) == 1:
            source_name, segments = next(iter(successful_sources.items()))
            sequence = get_transcription_sequence(source_name, segments)
            self.last_lexical_alignment = Alignment(
                source_names=(source_name,),
                columns=tuple(Column((token,)) for token in sequence.tokens),
            )
            self.last_alignment = self.last_lexical_alignment
            logger.warning(
                f"Only transcription source {source_name!r} produced output; "
                "skipping multi-source consensus."
            )
            return segments
        return self.merge(
            successful_sources,
            audio,
            audio_events=audio_events,
            diarization=diarization,
            language_identification=language_identification,
            pause_intervals_seconds=pause_intervals_seconds,
            source_offset_seconds=source_offset_seconds,
            voice_activity_trace=voice_activity_trace,
        )
