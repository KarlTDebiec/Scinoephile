#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Multi-source transcription orchestration."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from logging import getLogger

from pydub import AudioSegment

from scinoephile.analysis.alignment.timed_msa import MsaAligner, MsaAlignment, MsaColumn
from scinoephile.analysis.transcription.artifact import TimingSource
from scinoephile.audio.classification import (
    AudioEventDetectionResult,
    LanguageIdentificationResult,
)
from scinoephile.audio.diarization.models import SpeakerDiarizationResult
from scinoephile.audio.transcription import (
    TranscribedSegment,
    Transcriber,
    TranscriptionEmptyError,
    TranscriptionError,
)
from scinoephile.audio.transcription.alignment_sequence import (
    get_transcription_sequence,
)
from scinoephile.audio.transcription.ctc import CtcAligner
from scinoephile.audio.transcription.quality import (
    get_transcription_quality_issue,
    is_low_information_text,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.llms.transcription import TranscriptionProcessor, TranscriptionSource
from scinoephile.workflows.transcription_alignment import render_transcription_alignment

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
        aligner: MsaAligner,
        processor: TranscriptionProcessor,
        ctc_aligner: CtcAligner | None = None,
    ):
        """Initialize.

        Arguments:
            language: transcription and output language
            transcribers: named equal-status ASR sources
            aligner: multiple-sequence character aligner
            processor: aligned consensus and subtitle-boundary processor
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
        self.aligner = aligner
        """Multiple-sequence character aligner."""
        self.processor = processor
        """Aligned consensus and subtitle-boundary processor."""
        if ctc_aligner is None:
            ctc_aligner = CtcAligner(language)
        self.ctc_aligner = ctc_aligner
        """Aligner used to recover final consensus timings."""
        self.last_alignment: MsaAlignment | None = None
        """Latest aligned ASR evidence with timed pauses."""
        self.last_lexical_alignment: MsaAlignment | None = None
        """Latest multi-ASR alignment before timed pauses are inserted."""
        self.last_sources: dict[str, list[TranscribedSegment]] = {}
        """Latest successful raw ASR source outputs."""
        self.last_source_errors: dict[str, str] = {}
        """Latest tolerated source failures keyed by stable source name."""
        self.last_source_cache_key_sha256s: dict[str, str] = {}
        """Latest selected ASR cache-key digests keyed by source name."""
        self.last_query_key_sha256s: tuple[str, ...] = ()
        """Latest semantic processor query-key digests in request order."""
        self.last_timing_sources: dict[int, TimingSource] = {}
        """Final block-local segment IDs mapped to their timing origins."""

    def __call__(self, audio: AudioSegment) -> list[TranscribedSegment]:
        """Transcribe audio without optional analysis evidence.

        Arguments:
            audio: complete processing-block audio
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
        pause_intervals_seconds: Sequence[tuple[float, float]] | None = None,
        source_offset_seconds: float = 0.0,
    ) -> list[TranscribedSegment]:
        """Merge timestamped sources and recover consensus subtitle timings.

        Arguments:
            sources: named equal-status timestamped transcription sources
            audio: original block audio corresponding to local source timings
            audio_events: optional source-wide FireRed audio-event timeline
            diarization: optional source-wide exclusive speaker timeline
            language_identification: optional source-wide FireRed language timeline
            pause_intervals_seconds: optional explicit block-local pause intervals
            source_offset_seconds: source time corresponding to block-local zero
        Returns:
            final consensus subtitles with block-local CTC timings
        Raises:
            ScinoephileError: if fewer than two named sources are provided
            TranscriptionEmptyError: if source or consensus text is unusable
        """
        self.last_query_key_sha256s = ()
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
        self.last_query_key_sha256s = tuple(
            result.query_key_sha256 for result in request_results
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
        pause_intervals_seconds: Sequence[tuple[float, float]] | None = None,
        source_offset_seconds: float = 0.0,
    ) -> list[TranscribedSegment]:
        """Transcribe one processing block using optional audio-analysis evidence.

        Arguments:
            audio: complete processing-block audio
            audio_events: optional source-wide FireRed audio-event timeline
            diarization: optional source-wide exclusive speaker timeline
            language_identification: optional source-wide FireRed language timeline
            pause_intervals_seconds: optional explicit block-local pause intervals
            source_offset_seconds: source time corresponding to block-local zero
        Returns:
            final consensus subtitles with block-local CTC timings
        Raises:
            TranscriptionEmptyError: if no ASR source provides usable text
        """
        self.last_alignment = None
        self.last_lexical_alignment = None
        self.last_sources = {}
        self.last_source_errors = {}
        self.last_source_cache_key_sha256s = {}
        self.last_query_key_sha256s = ()
        self.last_timing_sources = {}
        successful_sources: dict[str, list[TranscribedSegment]] = {}
        source_errors = {}
        audio_duration_seconds = len(audio) / 1000
        for source_name, transcriber in self.transcribers.items():
            quality_issue: str | None = None

            def is_usable(candidate: list[TranscribedSegment]) -> bool:
                """Check whether one preprocessing attempt is usable.

                Arguments:
                    candidate: timestamped transcription candidate
                Returns:
                    whether the candidate is suitable for alignment
                """
                nonlocal quality_issue
                candidate = self._get_audio_bounded_segments(
                    candidate, audio_duration_seconds
                )
                quality_issue = get_transcription_quality_issue(
                    candidate, audio_duration_seconds=audio_duration_seconds
                )
                return quality_issue is None

            try:
                segments = transcriber(audio, is_usable=is_usable)
            except TranscriptionError as exc:
                error = str(exc).strip() or type(exc).__name__
                source_errors[source_name] = error
                logger.info(
                    f"Transcription source {source_name!r} failed and will be "
                    f"excluded from this block: {error}"
                )
                continue
            segments = self._get_audio_bounded_segments(
                segments, audio_duration_seconds
            )
            if segments:
                quality_issue = get_transcription_quality_issue(
                    segments, audio_duration_seconds=audio_duration_seconds
                )
            elif quality_issue is None:
                quality_issue = get_transcription_quality_issue(segments)
            if quality_issue is not None:
                source_errors[source_name] = quality_issue
                logger.info(
                    f"Transcription source {source_name!r} was rejected and will be "
                    f"excluded from this block: {quality_issue}"
                )
                continue
            successful_sources[source_name] = segments
            cache_key_sha256 = transcriber.last_cache_key_sha256
            if cache_key_sha256 is not None:
                self.last_source_cache_key_sha256s[source_name] = cache_key_sha256

        self.last_sources = successful_sources
        self.last_source_errors = source_errors
        if not successful_sources:
            raise TranscriptionEmptyError(
                "All transcription sources produced empty output."
            )
        if len(successful_sources) == 1:
            source_name, segments = next(iter(successful_sources.items()))
            text = "".join(segment.text for segment in segments)
            if is_low_information_text(text):
                raise TranscriptionEmptyError(
                    f"Only surviving transcription source {source_name!r} produced "
                    "low-information vocalizations."
                )
            sequence = get_transcription_sequence(source_name, segments)
            self.last_lexical_alignment = MsaAlignment(
                source_names=(source_name,),
                columns=tuple(MsaColumn((token,)) for token in sequence.tokens),
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
        )

    @staticmethod
    def _get_audio_bounded_segments(
        segments: list[TranscribedSegment], audio_duration_seconds: float
    ) -> list[TranscribedSegment]:
        """Clip timestamped source evidence to the supplied audio.

        Small backend timestamp overruns are accepted during source-quality
        validation, but impossible timing units must not reach the alignment.

        Arguments:
            segments: raw timestamped source transcription
            audio_duration_seconds: duration of the supplied audio
        Returns:
            transcription whose timed words lie within the supplied audio
        """
        if all(
            segment.start >= 0.0
            and segment.end <= audio_duration_seconds
            and all(
                word.start >= 0.0 and word.end <= audio_duration_seconds
                for word in (segment.words or [])
            )
            for segment in segments
        ):
            return segments

        output_segments = []
        for segment in segments:
            if not segment.words:
                output_segments.append(segment)
                continue
            words = []
            for word in segment.words:
                start_seconds = max(0.0, min(word.start, audio_duration_seconds))
                end_seconds = max(0.0, min(word.end, audio_duration_seconds))
                if round(end_seconds * 1000) <= round(start_seconds * 1000):
                    continue
                if start_seconds == word.start and end_seconds == word.end:
                    words.append(word)
                    continue
                words.append(
                    word.model_copy(update={"start": start_seconds, "end": end_seconds})
                )
            if not words:
                continue
            text = "".join(word.text for word in words)
            if (
                words == segment.words
                and segment.start == words[0].start
                and segment.end == words[-1].end
                and segment.text == text
            ):
                output_segments.append(segment)
                continue
            output_segments.append(
                segment.model_copy(
                    update={
                        "start": words[0].start,
                        "end": words[-1].end,
                        "text": text,
                        "words": words,
                    }
                )
            )
        return output_segments
