#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Partition aligned transcription queries at shared pauses."""

from __future__ import annotations

from collections.abc import Sequence

from .models import TranscriptionQuery

__all__ = ["partition_transcription_query"]

_REQUEST_PAUSE_CHARACTERS = 4
"""Shared pause columns required to start a separate LLM request."""
_REQUEST_PAUSE_SECONDS = 1.0
"""Continuous shared-pause duration required to start a separate request."""


def partition_transcription_query(
    query: TranscriptionQuery,
    pause_intervals_seconds: Sequence[tuple[float, float] | None] | None = None,
) -> tuple[tuple[TranscriptionQuery, tuple[int, int]], ...]:
    """Partition a validated alignment query at long continuous shared pauses.

    Arguments:
        query: validated complete-block alignment query
        pause_intervals_seconds: optional interval for each alignment column
    Returns:
        request queries and their complete-alignment column spans
    Raises:
        ValueError: if structured pause intervals do not match the query
    """
    rows = (query.speaker, *(source.text for source in query.sources))
    if pause_intervals_seconds is None:
        content_spans = _get_flat_content_spans(rows, len(query.speaker))
    else:
        content_spans = _get_timed_content_spans(
            rows, pause_intervals_seconds, len(query.speaker)
        )

    requests = []
    for content_start, content_end in content_spans:
        request = _get_query_slice(query, content_start, content_end)
        if any(_has_usable_content(source.text) for source in request.sources):
            requests.append((request, (content_start, content_end)))
    return tuple(requests)


def _get_flat_content_spans(
    rows: tuple[str, ...], width: int
) -> tuple[tuple[int, int], ...]:
    """Get content spans separated by long rendered pause runs.

    Arguments:
        rows: equal-width source and annotation rows
        width: alignment column count
    Returns:
        content spans between long shared pause runs
    """
    content_spans = []
    content_start = 0
    pause_start: int | None = None
    for column_idx in range(width + 1):
        is_shared_pause = column_idx < width and all(
            row[column_idx] == "・" for row in rows
        )
        if is_shared_pause:
            if pause_start is None:
                pause_start = column_idx
            continue
        if pause_start is not None:
            if column_idx - pause_start >= _REQUEST_PAUSE_CHARACTERS:
                if content_start < pause_start:
                    content_spans.append((content_start, pause_start))
                content_start = column_idx
            pause_start = None
    if content_start < width:
        content_spans.append((content_start, width))
    return tuple(content_spans)


def _get_query_slice(
    query: TranscriptionQuery, start: int, end: int
) -> TranscriptionQuery:
    """Get one alignment-column slice of a validated query.

    Arguments:
        query: validated complete-block alignment query
        start: inclusive alignment column index
        end: exclusive alignment column index
    Returns:
        sliced request query
    """
    update: dict[str, object] = {
        "sources": [
            source.model_copy(update={"text": source.text[start:end]})
            for source in query.sources
        ],
        "speaker": query.speaker[start:end],
    }
    return query.model_copy(update=update)


def _get_timed_content_spans(
    rows: tuple[str, ...],
    pause_intervals_seconds: Sequence[tuple[float, float] | None],
    width: int,
) -> tuple[tuple[int, int], ...]:
    """Get content spans separated by long continuous timed pauses.

    Arguments:
        rows: equal-width source and annotation rows
        pause_intervals_seconds: interval for each alignment column
        width: alignment column count
    Returns:
        content spans between long continuous shared pauses
    Raises:
        ValueError: if structured pause intervals do not match the rows
    """
    if len(pause_intervals_seconds) != width:
        raise ValueError(
            "Timed pause intervals must match the transcription alignment width."
        )

    content_spans = []
    content_start = 0
    pause_start: int | None = None
    pause_interval_start: float | None = None
    pause_interval_end: float | None = None
    for column_idx in range(width + 1):
        pause_interval = None
        if column_idx < width:
            pause_interval = pause_intervals_seconds[column_idx]
        if pause_interval is not None:
            if not all(row[column_idx] == "・" for row in rows):
                raise ValueError(
                    "Timed pause intervals require shared transcription pause columns."
                )
            if (
                pause_start is not None
                and pause_interval_end is not None
                and abs(pause_interval[0] - pause_interval_end) <= 1e-9
            ):
                pause_interval_end = pause_interval[1]
                continue
        if pause_start is not None:
            if (
                pause_interval_start is not None
                and pause_interval_end is not None
                and pause_interval_end - pause_interval_start >= _REQUEST_PAUSE_SECONDS
            ):
                if content_start < pause_start:
                    content_spans.append((content_start, pause_start))
                content_start = column_idx
            pause_start = None
            pause_interval_start = None
            pause_interval_end = None
        if pause_interval is not None:
            pause_start = column_idx
            pause_interval_start, pause_interval_end = pause_interval
    if content_start < width:
        content_spans.append((content_start, width))
    return tuple(content_spans)


def _has_usable_content(text: str) -> bool:
    """Check whether aligned text contains usable content.

    Arguments:
        text: aligned transcription text
    Returns:
        whether the text contains nonblank, non-pause content
    """
    return any(character != "・" and not character.isspace() for character in text)
