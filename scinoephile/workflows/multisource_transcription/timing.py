#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CTC timing recovery for multi-source consensus requests."""

from __future__ import annotations

from collections.abc import Sequence
from logging import getLogger

from pydub import AudioSegment

from scinoephile.analysis.alignment.timed_msa.alignment import Alignment
from scinoephile.analysis.transcription.artifact import TimingSource
from scinoephile.audio.transcription import (
    CtcAligner,
    TranscribedSegment,
    TranscriptionAlignmentError,
    TranscriptionEmptyError,
    get_segment_merged,
    get_segment_split_at_idx,
    get_segment_with_offset,
)
from scinoephile.core.text import is_lexical_character
from scinoephile.llms.transcription import (
    TranscriptionAnswer,
    TranscriptionRequestResult,
)

__all__ = ["get_request_interval", "get_timed_request_segments"]

logger = getLogger(__name__)

_REQUEST_FALLBACK_PADDING_SECONDS = 0.25
"""Audio padding around lexical timing when pause-derived bounds are invalid."""
_MINIMUM_STRETCHED_CTC_SECONDS = 4.0
"""Shortest CTC span considered for evidence-local realignment."""
_MAXIMUM_CTC_SECONDS_PER_CHARACTER = 1.0
"""Largest plausible CTC span per lexical subtitle character."""
_MINIMUM_EVIDENCE_DEVIATION_SECONDS = 2.0
"""Smallest timing deviation that warrants subtitle-local CTC alignment."""


def get_request_interval(
    alignment: Alignment,
    span: tuple[int, int],
    duration_seconds: float,
    *,
    answer_evidence_column_indexes: Sequence[int] = (),
) -> tuple[float, float] | None:
    """Get the audio interval around answer evidence within shared-pause bounds.

    Arguments:
        alignment: complete aligned source and pause evidence
        span: inclusive and exclusive alignment-column indexes
        duration_seconds: complete block duration
        answer_evidence_column_indexes: columns corroborating answer characters
    Returns:
        bounded audio interval, or None when evidence is outside the audio
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
    pause_interval = None
    if end_seconds > start_seconds:
        pause_interval = (start_seconds, end_seconds)

    evidence_columns = tuple(
        alignment.columns[column_idx]
        for column_idx in answer_evidence_column_indexes
        if start_column <= column_idx < end_column
    )
    if evidence_columns:
        evidence_start_seconds = max(
            0.0,
            min(column.start_seconds for column in evidence_columns)
            - _REQUEST_FALLBACK_PADDING_SECONDS,
        )
        evidence_end_seconds = min(
            duration_seconds,
            max(column.end_seconds for column in evidence_columns)
            + _REQUEST_FALLBACK_PADDING_SECONDS,
        )
        if pause_interval is not None:
            evidence_start_seconds = max(evidence_start_seconds, pause_interval[0])
            evidence_end_seconds = min(evidence_end_seconds, pause_interval[1])
        if evidence_end_seconds > evidence_start_seconds:
            return evidence_start_seconds, evidence_end_seconds
        logger.warning(
            "Answer-evidence timing does not overlap its shared-pause request "
            "bounds; using the shared-pause interval instead."
        )

    if pause_interval is not None:
        return pause_interval

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


def get_timed_request_segments(  # noqa: PLR0912, PLR0915
    audio: AudioSegment,
    alignment: Alignment,
    request_results: Sequence[TranscriptionRequestResult],
    ctc_aligner: CtcAligner,
) -> tuple[list[TranscribedSegment], dict[int, TimingSource]]:
    """CTC-align request transcripts and retain their subtitle splits.

    Arguments:
        audio: complete block audio
        alignment: complete aligned source and pause evidence
        request_results: LLM request answers and alignment spans
        ctc_aligner: aligner used to recover consensus timings
    Returns:
        final block-local segments and their timing sources
    Raises:
        TranscriptionEmptyError: if no request has a usable audio interval
    """
    output_segments = []
    output_timing_sources: list[TimingSource] = []
    duration_seconds = len(audio) / 1000
    for request_idx, request_result in enumerate(request_results, start=1):
        answer = request_result.answer
        if not answer.transcript:
            logger.info(
                f"Skipping transcription request {request_idx} because the "
                "processor found no sufficiently supported speech."
            )
            continue
        request_interval = get_request_interval(
            alignment,
            (request_result.start_column, request_result.end_column),
            duration_seconds,
            answer_evidence_column_indexes=(
                request_result.answer_evidence_column_indexes
            ),
        )
        if request_interval is None:
            logger.warning(
                f"Skipping transcription request {request_idx} because its "
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
                f"Skipping transcription request {request_idx} because no "
                "chronologically usable block audio remains."
            )
            continue
        span_audio = audio[round(start_seconds * 1000) : round(end_seconds * 1000)]
        timing_source: TimingSource = "ctc-request"
        try:
            aligned = ctc_aligner(span_audio, answer.transcript)
        except TranscriptionAlignmentError as exc:
            retry_start_seconds = output_segments[-1].end if output_segments else 0.0
            if retry_start_seconds >= duration_seconds:
                logger.warning(
                    f"Skipping transcription request {request_idx} because CTC "
                    f"timing failed and no unconsumed block audio remains: {exc}"
                )
                continue
            logger.warning(
                f"CTC timing failed within transcription request {request_idx}'s "
                f"evidence interval; retrying against the unconsumed block audio: "
                f"{exc}"
            )
            retry_audio = audio[round(retry_start_seconds * 1000) :]
            try:
                aligned = ctc_aligner(retry_audio, answer.transcript)
            except TranscriptionAlignmentError as retry_exc:
                logger.warning(
                    f"Skipping transcription request {request_idx} because CTC "
                    f"timing also failed across the unconsumed block audio: "
                    f"{retry_exc}"
                )
                continue
            start_seconds = retry_start_seconds
            timing_source = "ctc-unconsumed-block"
        if not aligned:
            logger.warning(
                f"Skipping transcription request {request_idx} because CTC "
                "alignment produced no timed consensus text."
            )
            continue
        aligned_segment = get_segment_merged(aligned)
        request_segments = _split_aligned_segment(aligned_segment, answer)
        offset_segments = [
            get_segment_with_offset(segment, start_seconds)
            for segment in request_segments
        ]
        previous_end_seconds = 0.0
        if output_segments:
            previous_end_seconds = output_segments[-1].end
        offset_segments, segment_timing_sources = _repair_stretched_segments(
            audio,
            alignment,
            request_result,
            offset_segments,
            ctc_aligner,
            duration_seconds,
            previous_end_seconds=previous_end_seconds,
            request_end_seconds=end_seconds,
            timing_source=timing_source,
        )
        output_segments.extend(offset_segments)
        output_timing_sources.extend(segment_timing_sources)
    if not output_segments:
        raise TranscriptionEmptyError(
            "No transcription request has a usable audio interval."
        )

    numbered_segments = [
        segment.model_copy(update={"id": segment_idx})
        for segment_idx, segment in enumerate(output_segments)
    ]
    timing_sources = {
        segment.id: timing_source
        for segment, timing_source in zip(
            numbered_segments, output_timing_sources, strict=True
        )
    }
    return numbered_segments, timing_sources


def _get_subtitle_evidence_column_indexes(
    request_result: TranscriptionRequestResult,
) -> tuple[tuple[int, ...], ...]:
    """Partition per-character evidence columns at subtitle boundaries.

    Arguments:
        request_result: answer and its per-character evidence columns
    Returns:
        corroborating complete-alignment columns for each answer subtitle
    Raises:
        RuntimeError: if evidence and lexical answer lengths differ
    """
    character_evidence = request_result.answer_character_evidence_column_indexes
    if not character_evidence:
        return tuple(() for _ in request_result.answer.subtitles)
    expected_character_count = sum(
        is_lexical_character(character)
        for character in request_result.answer.transcript
    )
    if len(character_evidence) != expected_character_count:
        raise RuntimeError(
            "Answer character evidence does not match the consensus transcript."
        )

    evidence_by_subtitle = []
    character_start = 0
    for subtitle in request_result.answer.subtitles:
        character_end = character_start + sum(
            is_lexical_character(character) for character in subtitle.text
        )
        evidence_by_subtitle.append(
            tuple(
                column_idx
                for column_idx in character_evidence[character_start:character_end]
                if column_idx is not None
            )
        )
        character_start = character_end
    return tuple(evidence_by_subtitle)


def _is_stretched(segment: TranscribedSegment) -> bool:
    """Check whether a CTC interval is implausibly long for its lexical text.

    Arguments:
        segment: CTC-aligned subtitle candidate
    Returns:
        whether the interval is disproportionately long
    """
    lexical_character_count = sum(
        is_lexical_character(character) for character in segment.text
    )
    maximum_seconds = max(
        _MINIMUM_STRETCHED_CTC_SECONDS,
        lexical_character_count * _MAXIMUM_CTC_SECONDS_PER_CHARACTER,
    )
    return segment.end - segment.start > maximum_seconds


def _is_stretched_beyond_evidence(
    segment: TranscribedSegment, evidence_interval: tuple[float, float]
) -> bool:
    """Check whether stretched CTC timing substantially exceeds ASR evidence.

    Arguments:
        segment: CTC-aligned subtitle candidate
        evidence_interval: corroborating ASR timing envelope
    Returns:
        whether CTC timing is long and materially outside its evidence
    """
    if not _is_stretched(segment):
        return False
    evidence_start_seconds, evidence_end_seconds = evidence_interval
    evidence_duration_seconds = evidence_end_seconds - evidence_start_seconds
    tolerance_seconds = max(
        _MINIMUM_EVIDENCE_DEVIATION_SECONDS, evidence_duration_seconds / 2
    )
    return (
        evidence_start_seconds - segment.start > tolerance_seconds
        or segment.end - evidence_end_seconds > tolerance_seconds
    )


def _repair_stretched_segments(  # noqa: PLR0913
    audio: AudioSegment,
    alignment: Alignment,
    request_result: TranscriptionRequestResult,
    segments: Sequence[TranscribedSegment],
    ctc_aligner: CtcAligner,
    duration_seconds: float,
    *,
    previous_end_seconds: float,
    request_end_seconds: float,
    timing_source: TimingSource,
) -> tuple[list[TranscribedSegment], list[TimingSource]]:
    """Realign suspiciously stretched subtitles inside their own evidence windows.

    A request-level forced alignment may bridge answer text omitted between two
    retained subtitles. That can make a character near the end of the first
    subtitle match speech many seconds later. Only suspicious subtitles are
    rerun, avoiding a separate CTC inference for every ordinary subtitle.

    Arguments:
        audio: complete block audio
        alignment: complete aligned source and pause evidence
        request_result: answer, span, and per-character evidence columns
        segments: request-level CTC segments using block-local timing
        ctc_aligner: aligner used to recover consensus timings
        duration_seconds: complete block duration
        previous_end_seconds: end of the preceding output request
        request_end_seconds: exclusive end of this request's usable audio
        timing_source: origin of the request-level CTC timing
    Returns:
        repaired segments and their timing sources
    """
    evidence_by_subtitle = _get_subtitle_evidence_column_indexes(request_result)
    repaired_segments = list(segments)
    timing_sources = [timing_source] * len(segments)
    for segment_idx, (segment, evidence_column_indexes) in enumerate(
        zip(segments, evidence_by_subtitle, strict=True)
    ):
        if not evidence_column_indexes:
            continue
        evidence_interval = get_request_interval(
            alignment,
            (request_result.start_column, request_result.end_column),
            duration_seconds,
            answer_evidence_column_indexes=evidence_column_indexes,
        )
        if evidence_interval is None or not _is_stretched_beyond_evidence(
            segment, evidence_interval
        ):
            continue
        start_seconds, end_seconds = evidence_interval
        if segment_idx:
            start_seconds = max(start_seconds, repaired_segments[segment_idx - 1].end)
        else:
            start_seconds = max(start_seconds, previous_end_seconds)
        if segment_idx + 1 < len(segments):
            end_seconds = min(end_seconds, segments[segment_idx + 1].start)
        else:
            end_seconds = min(end_seconds, request_end_seconds)
        if end_seconds <= start_seconds:
            logger.warning(
                "Unable to repair stretched CTC timing for subtitle "
                f"{segment.text!r}: its corroborating evidence interval is empty."
            )
            continue

        span_audio = audio[round(start_seconds * 1000) : round(end_seconds * 1000)]
        try:
            aligned = ctc_aligner(span_audio, segment.text)
        except TranscriptionAlignmentError as exc:
            logger.warning(
                "Unable to repair stretched CTC timing for subtitle "
                f"{segment.text!r}: {exc}"
            )
            continue
        if not aligned:
            logger.warning(
                "Unable to repair stretched CTC timing for subtitle "
                f"{segment.text!r}: CTC alignment produced no timed text."
            )
            continue
        repaired = get_segment_with_offset(get_segment_merged(aligned), start_seconds)
        if repaired.text != segment.text:
            raise RuntimeError(
                "Subtitle-local CTC text does not match the requested consensus."
            )
        repaired_segments[segment_idx] = repaired
        timing_sources[segment_idx] = "ctc-subtitle"
        logger.info(
            "Repaired stretched CTC timing for subtitle "
            f"{segment.text!r}: {segment.start:.3f}-{segment.end:.3f}s -> "
            f"{repaired.start:.3f}-{repaired.end:.3f}s."
        )
    return repaired_segments, timing_sources


def _split_aligned_segment(
    segment: TranscribedSegment, answer: TranscriptionAnswer
) -> list[TranscribedSegment]:
    """Split one CTC-aligned transcript at consensus subtitle boundaries.

    Arguments:
        segment: complete CTC-aligned request transcript
        answer: consensus answer whose boundaries must be preserved
    Returns:
        CTC-aligned segments divided at consensus boundaries
    Raises:
        RuntimeError: if aligned text or retained boundaries are inconsistent
    """
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
        raise RuntimeError("Unable to retain consensus subtitle boundaries.")
    return output_segments
