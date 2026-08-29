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
    TranscribedSegment,
    TranscriptionAlignmentError,
    TranscriptionEmptyError,
    get_segment_merged,
    get_segment_split_at_idx,
)
from scinoephile.audio.transcription.ctc import CtcAligner
from scinoephile.llms.transcription import (
    TranscriptionAnswer,
    TranscriptionRequestResult,
)

__all__ = ["get_request_interval", "get_timed_request_segments"]

logger = getLogger(__name__)

_REQUEST_FALLBACK_PADDING_SECONDS = 0.25
"""Audio padding around lexical timing when pause-derived bounds are invalid."""


def get_request_interval(
    alignment: Alignment, span: tuple[int, int], duration_seconds: float
) -> tuple[float, float] | None:
    """Get the audio interval bounded by adjacent long shared pauses.

    Arguments:
        alignment: complete aligned source and pause evidence
        span: inclusive and exclusive alignment-column indexes
        duration_seconds: complete block duration
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
            _get_offset_segment(segment, start_seconds) for segment in request_segments
        ]
        output_segments.extend(offset_segments)
        output_timing_sources.extend([timing_source] * len(offset_segments))
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


def _get_offset_segment(
    segment: TranscribedSegment, offset_seconds: float
) -> TranscribedSegment:
    """Add an audio-slice offset to one CTC-aligned segment.

    Arguments:
        segment: segment timed against an audio slice
        offset_seconds: slice start on the complete block timeline
    Returns:
        segment timed against the complete block
    """
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
