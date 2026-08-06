#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Reference-free fusion of aligned timestamped transcription sources."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from logging import getLogger
from pathlib import Path
from typing import cast

from pydub import AudioSegment

from scinoephile.analysis.multisequence_alignment import (
    TimedAlignmentColumn,
    TimedMultiSequenceAligner,
    TimedMultiSequenceAlignment,
    get_timed_alignment_with_pauses,
)
from scinoephile.audio.classification import (
    AudioEventDetectionResult,
    LanguageIdentificationResult,
)
from scinoephile.audio.diarization import SpeakerDiarizationResult
from scinoephile.audio.transcription import (
    CtcAligner,
    TranscribedSegment,
    Transcriber,
    TranscriptionAlignmentError,
    TranscriptionEmptyError,
    TranscriptionError,
    VoiceActivityTrace,
    get_segment_merged,
    get_segment_split_at_idx,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.llms.aligned_transcription_merge import (
    AlignedTranscriptionMergeAnswer,
    AlignedTranscriptionMergeProcessor,
    AlignedTranscriptionMergeSource,
)
from scinoephile.llms.providers.registry import get_provider

from .aligned_merge import get_aligned_transcription_merger
from .multisource_alignment import (
    CantoneseTimedTokenSimilarity,
    get_timed_alignment_sequence,
    get_timed_multisource_alignment_chunks,
)

__all__ = ["MultiSourceTranscriber", "get_multi_source_transcriber"]


logger = getLogger(__name__)

_MINIMUM_PAUSE_SECONDS = 0.25
"""Shortest VAD pause represented in an aligned merge request."""
_PAUSE_UNIT_SECONDS = 0.25
"""Duration represented by each shared pause character."""
_REQUEST_PAUSE_CHARACTERS = 4
"""Shared pause characters required to start a separate LLM request."""
_REQUEST_FALLBACK_PADDING_SECONDS = 0.25
"""Audio padding around lexical timing when pause-derived bounds are invalid."""


class MultiSourceTranscriber:
    """Align ASR evidence, merge it into subtitles, and recover their timings."""

    def __init__(
        self,
        *,
        language: Language,
        transcribers: Mapping[str, Transcriber],
        merger: AlignedTranscriptionMergeProcessor,
        ctc_aligner: CtcAligner | None = None,
        alignment_aligner: TimedMultiSequenceAligner | None = None,
    ):
        """Initialize.

        Arguments:
            language: transcription and output language
            transcribers: named equal-status ASR sources
            merger: aligned consensus and subtitle-boundary processor
            ctc_aligner: aligner used to recover final consensus timings
            alignment_aligner: multiple-sequence character aligner
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
        self.merger = merger
        """Aligned consensus and subtitle-boundary processor."""
        if ctc_aligner is None:
            ctc_aligner = CtcAligner(language)
        self.ctc_aligner = ctc_aligner
        """Aligner used to recover final consensus timings."""
        if alignment_aligner is None:
            alignment_aligner = TimedMultiSequenceAligner(
                CantoneseTimedTokenSimilarity()
            )
        self.alignment_aligner = alignment_aligner
        """Cantonese-aware multiple-sequence character aligner."""
        self.last_alignment: TimedMultiSequenceAlignment | None = None
        """Latest aligned ASR and pause evidence."""
        self.last_lexical_alignment: TimedMultiSequenceAlignment | None = None
        """Latest multi-ASR alignment before timed pauses are inserted."""
        self.last_sources: dict[str, list[TranscribedSegment]] = {}
        """Latest successful raw ASR source outputs."""
        self.last_source_errors: dict[str, str] = {}
        """Latest tolerated source failures keyed by stable source name."""

    def __call__(self, audio: AudioSegment) -> list[TranscribedSegment]:
        """Transcribe audio without optional VAD or diarization evidence."""
        return self.transcribe_block(audio)

    def transcribe_block(
        self,
        audio: AudioSegment,
        *,
        audio_events: AudioEventDetectionResult | None = None,
        classification_offset_seconds: float = 0.0,
        language_identification: LanguageIdentificationResult | None = None,
        pause_intervals_seconds: Sequence[tuple[float, float]] = (),
        voice_activity_trace: VoiceActivityTrace | None = None,
        voice_activity_offset_seconds: float = 0.0,
        diarization: SpeakerDiarizationResult | None = None,
        diarization_offset_seconds: float = 0.0,
    ) -> list[TranscribedSegment]:
        """Transcribe one padded block using aligned audio-analysis evidence.

        Arguments:
            audio: complete padded block audio
            audio_events: optional source-wide FireRed audio-event timeline
            classification_offset_seconds: source time at block-local zero
            language_identification: optional source-wide FireRed language timeline
            pause_intervals_seconds: block-local VAD silence intervals
            voice_activity_trace: optional source-wide VAD score trace
            voice_activity_offset_seconds: source time at block-local zero
            diarization: optional source-wide exclusive speaker timeline
            diarization_offset_seconds: source time at block-local zero
        Returns:
            final LLM-split subtitles with block-local CTC timings
        Raises:
            TranscriptionEmptyError: if no ASR source provides usable text
        """
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
            if any(segment.text.strip() for segment in segments):
                successful_sources[source_name] = segments
            else:
                source_errors[source_name] = "Source produced no nonblank text."

        self.last_sources = successful_sources
        self.last_source_errors = source_errors
        if not successful_sources:
            raise TranscriptionEmptyError(
                "All transcription sources produced empty output."
            )
        if len(successful_sources) == 1:
            source_name, segments = next(iter(successful_sources.items()))
            sequence = get_timed_alignment_sequence(source_name, segments)
            self.last_lexical_alignment = TimedMultiSequenceAlignment(
                source_names=(source_name,),
                columns=tuple(
                    TimedAlignmentColumn((token,)) for token in sequence.tokens
                ),
            )
            self.last_alignment = self.last_lexical_alignment
            logger.warning(
                f"Only transcription source {source_name!r} produced "
                "output; skipping multi-source merge."
            )
            return segments
        if audio_events is None and language_identification is None:
            return self.merge(
                successful_sources,
                audio,
                pause_intervals_seconds=pause_intervals_seconds,
                voice_activity_trace=voice_activity_trace,
                voice_activity_offset_seconds=voice_activity_offset_seconds,
                diarization=diarization,
                diarization_offset_seconds=diarization_offset_seconds,
            )
        return self.merge(
            successful_sources,
            audio,
            audio_events=audio_events,
            classification_offset_seconds=classification_offset_seconds,
            language_identification=language_identification,
            pause_intervals_seconds=pause_intervals_seconds,
            voice_activity_trace=voice_activity_trace,
            voice_activity_offset_seconds=voice_activity_offset_seconds,
            diarization=diarization,
            diarization_offset_seconds=diarization_offset_seconds,
        )

    def merge(
        self,
        sources: Mapping[str, Sequence[TranscribedSegment]],
        audio: AudioSegment,
        *,
        audio_events: AudioEventDetectionResult | None = None,
        classification_offset_seconds: float = 0.0,
        language_identification: LanguageIdentificationResult | None = None,
        pause_intervals_seconds: Sequence[tuple[float, float]] = (),
        voice_activity_trace: VoiceActivityTrace | None = None,
        voice_activity_offset_seconds: float = 0.0,
        diarization: SpeakerDiarizationResult | None = None,
        diarization_offset_seconds: float = 0.0,
    ) -> list[TranscribedSegment]:
        """Merge timestamped sources and recover timings for LLM subtitle splits.

        Arguments:
            sources: named equal-status timestamped transcription sources
            audio: original block audio corresponding to local source timings
            audio_events: optional source-wide FireRed audio-event timeline
            classification_offset_seconds: source time at block-local zero
            language_identification: optional source-wide FireRed language timeline
            pause_intervals_seconds: block-local VAD silence intervals
            voice_activity_trace: optional source-wide VAD score trace
            voice_activity_offset_seconds: source time at block-local zero
            diarization: optional source-wide exclusive speaker timeline
            diarization_offset_seconds: source time at block-local zero
        Returns:
            final LLM-split subtitles with block-local CTC timings
        Raises:
            ScinoephileError: if fewer than two named sources are provided
            TranscriptionEmptyError: if source or merged text is unusable
        """
        if len(sources) < 2:
            raise ScinoephileError(
                "Multi-source transcription requires at least two sources."
            )
        if len(audio) <= 0:
            raise TranscriptionEmptyError(
                "Cannot merge transcription evidence for empty audio."
            )

        sequences = tuple(
            get_timed_alignment_sequence(name, segments)
            for name, segments in sources.items()
        )
        if any(not sequence.tokens for sequence in sequences):
            raise TranscriptionEmptyError(
                "Timed transcription sources contain no usable aligned text."
            )
        alignment = self.alignment_aligner(sequences)
        self.last_lexical_alignment = alignment
        alignment = get_timed_alignment_with_pauses(
            alignment,
            minimum_pause_seconds=_MINIMUM_PAUSE_SECONDS,
            pause_intervals_seconds=pause_intervals_seconds,
            pause_unit_seconds=_PAUSE_UNIT_SECONDS,
            source_names=alignment.source_names,
        )
        self.last_alignment = alignment
        chunks = get_timed_multisource_alignment_chunks(
            alignment,
            audio_events=audio_events,
            classification_offset_seconds=classification_offset_seconds,
            diarization=diarization,
            diarization_offset_seconds=diarization_offset_seconds,
            language_identification=language_identification,
            traditionalize=self.language is Language.yue_hant,
            voice_activity_trace=voice_activity_trace,
            voice_activity_offset_seconds=voice_activity_offset_seconds,
        )
        merge_sources, speaker, language_trace, singing_trace, music_trace = (
            self._join_chunks(chunks)
        )
        answer = self.merger.process(
            merge_sources,
            speaker,
            language_trace=language_trace,
            music_trace=music_trace,
            request_pause_characters=_REQUEST_PAUSE_CHARACTERS,
            singing_trace=singing_trace,
        )
        if not answer.transcript.strip():
            raise TranscriptionEmptyError(
                "Aligned multi-source merge produced no usable text."
            )
        return self._get_timed_answer_segments(audio, alignment, answer)

    def _get_timed_answer_segments(
        self,
        audio: AudioSegment,
        alignment: TimedMultiSequenceAlignment,
        answer: AlignedTranscriptionMergeAnswer,
    ) -> list[TranscribedSegment]:
        """CTC-align each request transcript and retain its LLM subtitle splits."""
        if len(self.merger.last_request_spans) != len(self.merger.last_request_answers):
            raise RuntimeError(
                "Aligned merge request spans and answers are inconsistent."
            )
        if answer.transcript != "".join(
            request_answer.transcript
            for request_answer in self.merger.last_request_answers
        ):
            raise RuntimeError("Combined aligned merge answer is inconsistent.")

        output_segments = []
        duration_seconds = len(audio) / 1000
        for request_idx, (request_span, request_answer) in enumerate(
            zip(
                self.merger.last_request_spans,
                self.merger.last_request_answers,
                strict=True,
            ),
            start=1,
        ):
            request_interval = self._get_request_interval(
                alignment, request_span, duration_seconds
            )
            if request_interval is None:
                logger.warning(
                    f"Skipping aligned merge request {request_idx} because its "
                    "evidence lies outside the usable block audio."
                )
                continue
            start_seconds, end_seconds = request_interval
            if output_segments:
                start_seconds = max(start_seconds, output_segments[-1].end)
                if end_seconds <= start_seconds:
                    end_seconds = duration_seconds
            if end_seconds <= start_seconds:
                logger.warning(
                    f"Skipping aligned merge request {request_idx} because no "
                    "chronologically usable block audio remains."
                )
                continue
            span_audio = audio[round(start_seconds * 1000) : round(end_seconds * 1000)]
            try:
                aligned = self.ctc_aligner(span_audio, request_answer.transcript)
            except TranscriptionAlignmentError as exc:
                retry_start_seconds = (
                    output_segments[-1].end if output_segments else 0.0
                )
                if retry_start_seconds >= duration_seconds:
                    logger.warning(
                        f"Skipping aligned merge request {request_idx} because "
                        f"CTC timing failed and no unconsumed block audio remains: "
                        f"{exc}"
                    )
                    continue
                logger.warning(
                    f"CTC timing failed within aligned merge request "
                    f"{request_idx}'s evidence interval; retrying against the "
                    f"unconsumed block audio: {exc}"
                )
                retry_audio = audio[round(retry_start_seconds * 1000) :]
                try:
                    aligned = self.ctc_aligner(retry_audio, request_answer.transcript)
                except TranscriptionAlignmentError as retry_exc:
                    logger.warning(
                        f"Skipping aligned merge request {request_idx} because "
                        f"CTC timing also failed across the unconsumed block audio: "
                        f"{retry_exc}"
                    )
                    continue
                start_seconds = retry_start_seconds
            if not aligned:
                logger.warning(
                    f"Skipping aligned merge request {request_idx} because CTC "
                    "alignment produced no timed consensus text."
                )
                continue
            aligned_segment = get_segment_merged(aligned)
            request_segments = self._split_aligned_segment(
                aligned_segment, request_answer
            )
            output_segments.extend(
                self._get_offset_segment(segment, start_seconds)
                for segment in request_segments
            )

        if not output_segments:
            raise TranscriptionEmptyError(
                "No aligned merge request has a usable audio interval."
            )

        return [
            segment.model_copy(update={"id": segment_idx})
            for segment_idx, segment in enumerate(output_segments)
        ]

    @staticmethod
    def _get_request_interval(
        alignment: TimedMultiSequenceAlignment,
        span: tuple[int, int],
        duration_seconds: float,
    ) -> tuple[float, float] | None:
        """Get the audio interval bounded by adjacent long shared pauses.

        Returns:
            bounded audio interval, or None when ASR evidence is outside the audio
        """
        start_column, end_column = span
        if start_column == 0:
            start_seconds = 0.0
        else:
            start_seconds = alignment.columns[start_column - 1].end_seconds
        if end_column == len(alignment.columns):
            end_seconds = duration_seconds
        else:
            end_seconds = alignment.columns[end_column].start_seconds
        start_seconds = max(0.0, min(start_seconds, duration_seconds))
        end_seconds = max(start_seconds, min(end_seconds, duration_seconds))
        if end_seconds > start_seconds:
            return start_seconds, end_seconds

        content_columns = alignment.columns[start_column:end_column]
        if not content_columns:
            return None
        lexical_start_seconds = max(
            0.0,
            min(column.start_seconds for column in content_columns)
            - _REQUEST_FALLBACK_PADDING_SECONDS,
        )
        lexical_end_seconds = min(
            duration_seconds,
            max(column.end_seconds for column in content_columns)
            + _REQUEST_FALLBACK_PADDING_SECONDS,
        )
        if lexical_end_seconds <= lexical_start_seconds:
            return None
        logger.warning(
            "Long-pause request bounds are invalid; using the request's lexical "
            "evidence interval instead."
        )
        return lexical_start_seconds, lexical_end_seconds

    @staticmethod
    def _get_offset_segment(
        segment: TranscribedSegment, offset_seconds: float
    ) -> TranscribedSegment:
        """Add an audio-slice offset to one CTC-aligned segment."""
        words = None
        if segment.words is not None:
            words = [
                word.model_copy(
                    update={
                        "start": word.start + offset_seconds,
                        "end": word.end + offset_seconds,
                    }
                )
                for word in segment.words
            ]
        return segment.model_copy(
            update={
                "start": segment.start + offset_seconds,
                "end": segment.end + offset_seconds,
                "words": words,
            }
        )

    @staticmethod
    def _join_chunks(
        chunks,
    ) -> tuple[
        list[AlignedTranscriptionMergeSource], str, str | None, str | None, str | None
    ]:
        """Join display-sized alignment chunks into complete request rows."""
        if not chunks:
            raise TranscriptionEmptyError("Multiple-sequence alignment is empty.")
        source_names = tuple(source.name for source in chunks[0].sources)
        if any(
            tuple(source.name for source in chunk.sources) != source_names
            for chunk in chunks[1:]
        ):
            raise RuntimeError("Aligned source order changed between display chunks.")
        sources = [
            AlignedTranscriptionMergeSource(
                name=name,
                text="".join(chunk.sources[source_idx].text for chunk in chunks),
            )
            for source_idx, name in enumerate(source_names)
        ]
        return (
            sources,
            "".join(chunk.speaker for chunk in chunks),
            _join_optional_chunk_row(chunks, "language_trace"),
            _join_optional_chunk_row(chunks, "singing_trace"),
            _join_optional_chunk_row(chunks, "music_trace"),
        )

    @staticmethod
    def _split_aligned_segment(
        segment: TranscribedSegment, answer: AlignedTranscriptionMergeAnswer
    ) -> list[TranscribedSegment]:
        """Split one CTC-aligned transcript at the LLM's subtitle boundaries."""
        if segment.text != answer.transcript:
            raise RuntimeError(
                "CTC-aligned text does not match the requested consensus transcript."
            )
        output_segments = []
        remaining = segment
        for subtitle in answer.subtitles[:-1]:
            first, remaining = get_segment_split_at_idx(remaining, len(subtitle.text))
            output_segments.append(first)
        output_segments.append(remaining)
        if [item.text for item in output_segments] != [
            subtitle.text for subtitle in answer.subtitles
        ]:
            raise RuntimeError("Unable to retain aligned merge subtitle boundaries.")
        return output_segments


def get_multi_source_transcriber(
    language: Language,
    transcribers: Mapping[str, Transcriber],
    *,
    provider: LLMProvider | None = None,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
    additional_context: str | None = None,
    no_op: bool = False,
    current_test_cases_path: Path | None = None,
    prune_test_cases: bool = False,
    shared_test_cases: list[TestCase] | None = None,
) -> MultiSourceTranscriber:
    """Get a reference-free aligned multi-source transcriber.

    Arguments:
        language: transcription and output language
        transcribers: named equal-status ASR sources
        provider: provider to use for the consensus query
        cache_root_path: cache root directory path
        overwrite_cache: whether to replace matching generated cache files
        additional_context: additional context to include in the merge prompt
        no_op: select the first available source instead of querying an LLM
        current_test_cases_path: aligned-merge test-case JSON path
        prune_test_cases: whether to remove unencountered persisted test cases
        shared_test_cases: preloaded aligned-merge test cases
    Returns:
        configured aligned multi-source transcriber
    """
    if provider is None:
        provider = get_provider()
    merger = get_aligned_transcription_merger(
        language,
        shared_test_cases=shared_test_cases,
        provider=provider,
        cache_root_path=cache_root_path,
        overwrite_cache=overwrite_cache,
        additional_context=additional_context,
        no_op=no_op,
        current_test_cases_path=current_test_cases_path,
        prune_test_cases=prune_test_cases,
    )
    return MultiSourceTranscriber(
        language=language, transcribers=transcribers, merger=merger
    )


def _join_optional_chunk_row(chunks, attribute: str) -> str | None:
    """Join an optional annotation row while enforcing chunk consistency."""
    values = tuple(getattr(chunk, attribute) for chunk in chunks)
    if all(value is None for value in values):
        return None
    if any(value is None for value in values):
        raise RuntimeError(f"Aligned {attribute} availability changed between chunks.")
    return "".join(cast(str, value) for value in values)
