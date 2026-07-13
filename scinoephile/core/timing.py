#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core code related to timing."""

from __future__ import annotations

from copy import deepcopy

from scinoephile.core.subtitles import Series

from .exceptions import ScinoephileError

__all__ = ["format_time_ms", "get_series_timewarped"]


def format_time_ms(time_ms: int) -> str:
    """Format a millisecond timestamp as HH:MM:SS.

    Arguments:
        time_ms: time in milliseconds
    Returns:
        timestamp formatted as HH:MM:SS
    """
    total_seconds = time_ms // 1000
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_series_timewarped(
    source_one: Series,
    source_two: Series,
    one_start_idx: int | None = None,
    one_end_idx: int | None = None,
    two_start_idx: int | None = None,
    two_end_idx: int | None = None,
) -> Series:
    """Timewarp a series to match anchors in another series.

    Indexes are 1-based and inclusive, matching subtitle numbering in SRT files.

    Arguments:
        source_one: anchor series
        source_two: series to timewarp
        one_start_idx: 1-based index of anchor subtitle in source one
        one_end_idx: 1-based index of anchor subtitle in source one
        two_start_idx: 1-based index of anchor subtitle in source two
        two_end_idx: 1-based index of anchor subtitle in source two
    Returns:
        timewarped series
    Raises:
        ScinoephileError: If series are empty or indexes are invalid
    """
    if not source_one.events:
        raise ScinoephileError("Source one has no subtitle events to timewarp against")
    if not source_two.events:
        raise ScinoephileError("Source two has no subtitle events to timewarp")

    if one_start_idx is None:
        one_start_idx = 1
    if one_end_idx is None:
        one_end_idx = len(source_one)
    if two_start_idx is None:
        two_start_idx = 1
    if two_end_idx is None:
        two_end_idx = len(source_two)

    _validate_idx(one_start_idx, source_one, "source one start")
    _validate_idx(one_end_idx, source_one, "source one end")
    _validate_idx(two_start_idx, source_two, "source two start")
    _validate_idx(two_end_idx, source_two, "source two end")
    _validate_range(one_start_idx, one_end_idx, "source one")
    _validate_range(two_start_idx, two_end_idx, "source two")

    one_start_event = source_one.events[one_start_idx - 1]
    one_end_event = source_one.events[one_end_idx - 1]
    two_start_event = source_two.events[two_start_idx - 1]
    two_end_event = source_two.events[two_end_idx - 1]

    two_duration = two_end_event.end - two_start_event.start
    if two_duration == 0:
        raise ScinoephileError("Source two anchor duration is zero; cannot timewarp")

    one_duration = one_end_event.end - one_start_event.start
    if one_duration == 0:
        raise ScinoephileError("Source one anchor duration is zero; cannot timewarp")

    scale = one_duration / two_duration
    if scale <= 0:
        raise ScinoephileError(
            "Timewarp scale must be positive to preserve subtitle ordering"
        )

    offset = one_start_event.start - scale * two_start_event.start
    timewarped = deepcopy(source_two)

    for event in timewarped:
        event.start = int(round(scale * event.start + offset))
        event.end = int(round(scale * event.end + offset))

    return timewarped


def _validate_idx(idx: int, source: Series, label: str):
    """Validate a 1-based index for timewarping.

    Arguments:
        idx: 1-based index to validate
        source: series containing the subtitle events
        label: label for error messages
    Raises:
        ScinoephileError: If the index is invalid
    """
    if idx < 1:
        raise ScinoephileError(
            f"Invalid {label} index {idx}; indexes are 1-based and must be positive"
        )
    if idx > len(source):
        raise ScinoephileError(
            f"Invalid {label} index {idx}; series has {len(source)} subtitles"
        )


def _validate_range(start_idx: int, end_idx: int, label: str):
    """Validate the ordering of a 1-based timewarp index range.

    Arguments:
        start_idx: 1-based start index
        end_idx: 1-based end index
        label: label for error messages
    Raises:
        ScinoephileError: If the range is reversed
    """
    if start_idx > end_idx:
        raise ScinoephileError(
            f"Invalid {label} range {start_idx}-{end_idx}; "
            "start index must not exceed end index"
        )
