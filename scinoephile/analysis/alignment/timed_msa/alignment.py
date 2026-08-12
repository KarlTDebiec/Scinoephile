#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Timestamped multiple-sequence alignment and pause annotation."""

from __future__ import annotations

from collections.abc import Sequence as AbcSequence
from dataclasses import dataclass
from math import floor
from statistics import median

from .models import Column

__all__ = ["Alignment"]


@dataclass(frozen=True, slots=True)
class Alignment:
    """Multiple alignment of named timestamped character sequences."""

    source_names: tuple[str, ...]
    """Source names in row order."""
    columns: tuple[Column, ...]
    """Alignment columns in reading order."""

    def __post_init__(self):
        """Validate row names and column widths.

        Raises:
            ValueError: if sources are absent or duplicated, or widths differ
        """
        if not self.source_names:
            raise ValueError("Timed alignment requires at least one source.")
        if len(set(self.source_names)) != len(self.source_names):
            raise ValueError("Multiple alignment source names must be unique.")
        if any(len(column.tokens) != len(self.source_names) for column in self.columns):
            raise ValueError(
                "Multiple alignment column width does not match its sources."
            )

    def get_sequence_text(self, source_name: str) -> str:
        """Reconstruct one ungapped source sequence.

        Arguments:
            source_name: source row to reconstruct
        Returns:
            original source characters without alignment gaps
        Raises:
            ValueError: if the source name is not present in the alignment
        """
        source_idx = self.source_names.index(source_name)
        return "".join(
            token.text
            for column in self.columns
            if (token := column.tokens[source_idx]) is not None
        )

    def with_pauses(
        self,
        *,
        pause_intervals_seconds: AbcSequence[tuple[float, float]] | None = None,
        source_names: AbcSequence[str] | None = None,
        start_seconds: float | None = None,
        end_seconds: float | None = None,
        minimum_pause_seconds: float = 0.25,
        pause_unit_seconds: float = 0.25,
    ) -> Alignment:
        """Insert shared timed gaps from explicit intervals or source timing.

        The first pause column represents the interval beginning at
        `minimum_pause_seconds`. Each additional `pause_unit_seconds` adds another
        column so approximate duration remains visible in the character alignment.

        Arguments:
            pause_intervals_seconds: explicit local pause intervals, when available
            source_names: rows whose shared timing gaps define pauses, or all rows
            start_seconds: optional local interval start for a leading pause
            end_seconds: optional local interval end for a trailing pause
            minimum_pause_seconds: shortest shared gap represented as a pause
            pause_unit_seconds: duration increment represented by each additional column
        Returns:
            alignment with shared timed-pause columns
        Raises:
            ValueError: if names, bounds, settings, or input columns are invalid
        """
        _validate_timed_pause_arguments(
            self,
            pause_intervals_seconds,
            start_seconds,
            end_seconds,
            minimum_pause_seconds,
            pause_unit_seconds,
        )
        source_indexes = _get_pause_source_indexes(self, source_names)
        if pause_intervals_seconds is not None:
            return _get_alignment_with_explicit_pauses(
                self,
                pause_intervals_seconds,
                source_indexes,
                minimum_pause_seconds,
                pause_unit_seconds,
            )
        future_starts = _get_future_source_starts(self, source_indexes, end_seconds)

        output_columns = []
        inserted_pause_intervals = set()
        latest_end = start_seconds
        for column_idx in range(len(self.columns) + 1):
            next_start = future_starts[column_idx]
            if latest_end is not None and next_start is not None:
                pause_interval = (latest_end, next_start)
                pause_columns = _get_pause_columns(
                    len(self.source_names),
                    pause_interval,
                    minimum_pause_seconds,
                    pause_unit_seconds,
                )
                if pause_columns and pause_interval not in inserted_pause_intervals:
                    inserted_pause_intervals.add(pause_interval)
                    output_columns.extend(pause_columns)
            if column_idx == len(self.columns):
                continue

            column = self.columns[column_idx]
            output_columns.append(column)
            ends = [
                token.end_seconds
                for source_idx in source_indexes
                if (token := column.tokens[source_idx]) is not None
            ]
            if column.marker_time_seconds is not None:
                ends.append(column.marker_time_seconds)
            if ends:
                column_end = max(ends)
                if latest_end is None or column_end > latest_end:
                    latest_end = column_end

        return Alignment(source_names=self.source_names, columns=tuple(output_columns))


def _get_alignment_with_explicit_pauses(
    alignment: Alignment,
    pause_intervals_seconds: AbcSequence[tuple[float, float]],
    source_indexes: tuple[int, ...],
    minimum_pause_seconds: float,
    pause_unit_seconds: float,
) -> Alignment:
    """Insert externally detected pauses at approximate temporal positions.

    Arguments:
        alignment: lexical alignment without existing pause columns
        pause_intervals_seconds: explicit local pause intervals
        source_indexes: row indexes used to position pauses
        minimum_pause_seconds: shortest interval represented as a pause
        pause_unit_seconds: duration increment represented by each additional column
    Returns:
        alignment with explicit timed-pause columns
    Raises:
        ValueError: if pause intervals are not ordered and disjoint
    """
    pauses_by_boundary: dict[int, list[Column]] = {}
    previous_end = 0.0
    previous_boundary = 0
    for pause_interval in pause_intervals_seconds:
        pause_start, pause_end = pause_interval
        if pause_start < previous_end:
            raise ValueError("Explicit timed pauses must be ordered and disjoint.")
        previous_end = pause_end
        pause_columns = _get_pause_columns(
            len(alignment.source_names),
            pause_interval,
            minimum_pause_seconds,
            pause_unit_seconds,
        )
        if not pause_columns:
            continue
        boundary = max(
            previous_boundary,
            _get_explicit_pause_insertion_boundary(
                alignment, source_indexes, pause_interval
            ),
        )
        previous_boundary = boundary
        pauses_by_boundary.setdefault(boundary, []).extend(pause_columns)

    output_columns = []
    for boundary in range(len(alignment.columns) + 1):
        output_columns.extend(pauses_by_boundary.get(boundary, ()))
        if boundary < len(alignment.columns):
            output_columns.append(alignment.columns[boundary])
    return Alignment(source_names=alignment.source_names, columns=tuple(output_columns))


def _get_explicit_pause_insertion_boundary(
    alignment: Alignment,
    source_indexes: tuple[int, ...],
    pause_interval: tuple[float, float],
) -> int:
    """Locate an explicit pause using source gaps before token midpoints.

    A source whose inter-token gap overlaps most of the detected pause provides
    direct boundary evidence. This is stronger than voting on character
    midpoints, particularly when several sources share the same forced aligner
    and therefore repeat one timing error. The robust median-midpoint placement
    remains the fallback when no source exposes a sufficiently matching gap.

    Arguments:
        alignment: lexical alignment in which to locate the pause
        source_indexes: row indexes used as timing evidence
        pause_interval: explicit local pause interval
    Returns:
        insertion boundary between alignment columns
    """
    pause_start, pause_end = pause_interval
    pause_midpoint = (pause_start + pause_end) / 2
    fallback_boundary = _get_timed_insertion_boundary(
        alignment, source_indexes, pause_midpoint
    )
    future_starts = _get_future_starts_by_source(alignment, source_indexes)
    previous_ends: list[float | None] = [None] * len(source_indexes)
    best_boundary = fallback_boundary
    best_score = (0.0, 0.0, -len(alignment.columns))

    for boundary in range(len(alignment.columns) + 1):
        overlaps = []
        for source_position, previous_end in enumerate(previous_ends):
            next_start = future_starts[source_position][boundary]
            if previous_end is None or next_start is None:
                overlaps.append(0.0)
                continue
            overlaps.append(
                max(0.0, min(next_start, pause_end) - max(previous_end, pause_start))
            )
        score = (
            max(overlaps, default=0.0),
            sum(overlaps),
            -abs(boundary - fallback_boundary),
        )
        if score > best_score:
            best_boundary = boundary
            best_score = score

        if boundary == len(alignment.columns):
            continue
        column = alignment.columns[boundary]
        for source_position, source_idx in enumerate(source_indexes):
            token = column.tokens[source_idx]
            if token is not None:
                previous_ends[source_position] = token.end_seconds

    pause_duration = pause_end - pause_start
    if best_score[0] < pause_duration / 2:
        return fallback_boundary
    return best_boundary


def _get_future_source_starts(
    alignment: Alignment, source_indexes: tuple[int, ...], end_seconds: float | None
) -> tuple[float | None, ...]:
    """Get the earliest selected-source token start after each boundary.

    Arguments:
        alignment: lexical alignment to inspect
        source_indexes: row indexes used as timing evidence
        end_seconds: optional trailing interval boundary
    Returns:
        earliest future token start at each column boundary
    """
    future_starts: list[float | None] = [None] * (len(alignment.columns) + 1)
    next_start = end_seconds
    future_starts[-1] = next_start
    for column_idx in range(len(alignment.columns) - 1, -1, -1):
        starts = [
            token.start_seconds
            for source_idx in source_indexes
            if (token := alignment.columns[column_idx].tokens[source_idx]) is not None
        ]
        marker_time_seconds = alignment.columns[column_idx].marker_time_seconds
        if marker_time_seconds is not None:
            starts.append(marker_time_seconds)
        if starts:
            column_start = min(starts)
            if next_start is None or column_start < next_start:
                next_start = column_start
        future_starts[column_idx] = next_start
    return tuple(future_starts)


def _get_future_starts_by_source(
    alignment: Alignment, source_indexes: tuple[int, ...]
) -> tuple[tuple[float | None, ...], ...]:
    """Get each selected source's next token start after every boundary.

    Arguments:
        alignment: lexical alignment to inspect
        source_indexes: row indexes used as timing evidence
    Returns:
        future token starts by source and column boundary
    """
    starts_by_source = []
    for source_idx in source_indexes:
        future_starts: list[float | None] = [None] * (len(alignment.columns) + 1)
        next_start = None
        for column_idx in range(len(alignment.columns) - 1, -1, -1):
            token = alignment.columns[column_idx].tokens[source_idx]
            if token is not None:
                next_start = token.start_seconds
            future_starts[column_idx] = next_start
        starts_by_source.append(tuple(future_starts))
    return tuple(starts_by_source)


def _get_pause_columns(
    source_count: int,
    interval_seconds: tuple[float, float],
    minimum_pause_seconds: float,
    pause_unit_seconds: float,
) -> tuple[Column, ...]:
    """Encode one shared timing gap as duration-bucketed pause columns.

    Arguments:
        source_count: number of source rows in each output column
        interval_seconds: local pause interval
        minimum_pause_seconds: shortest interval represented as a pause
        pause_unit_seconds: duration increment represented by each additional column
    Returns:
        shared timed-pause columns representing the interval
    """
    start_seconds, end_seconds = interval_seconds
    duration_seconds = end_seconds - start_seconds
    if duration_seconds < minimum_pause_seconds or duration_seconds <= 0.0:
        return ()
    pause_count = 1 + floor(
        (duration_seconds - minimum_pause_seconds + 1e-9) / pause_unit_seconds
    )
    columns = []
    for pause_idx in range(pause_count):
        pause_end_seconds = start_seconds + (pause_idx + 1) * pause_unit_seconds
        if pause_idx == pause_count - 1:
            pause_end_seconds = end_seconds
        columns.append(
            Column(
                (None,) * source_count,
                pause_interval_seconds=(
                    start_seconds + pause_idx * pause_unit_seconds,
                    pause_end_seconds,
                ),
            )
        )
    return tuple(columns)


def _get_pause_source_indexes(
    alignment: Alignment, source_names: AbcSequence[str] | None
) -> tuple[int, ...]:
    """Resolve and validate rows whose shared gaps define pauses.

    Arguments:
        alignment: alignment containing the available source rows
        source_names: rows whose timing defines pauses, or all rows
    Returns:
        indexes of source rows used as timing evidence
    Raises:
        ValueError: if no source rows are selected or names are duplicated
    """
    if source_names is None:
        source_names = alignment.source_names
    source_indexes = tuple(
        alignment.source_names.index(source_name) for source_name in source_names
    )
    if not source_indexes:
        raise ValueError("Timed pauses require at least one source row.")
    if len(set(source_indexes)) != len(source_indexes):
        raise ValueError("Timed pause source names must be unique.")
    return source_indexes


def _get_timed_insertion_boundary(
    alignment: Alignment, source_indexes: tuple[int, ...], target_time: float
) -> int:
    """Locate the profile boundary following a local target time.

    Arguments:
        alignment: lexical alignment in which to locate the time
        source_indexes: row indexes used as timing evidence
        target_time: local time after which to insert
    Returns:
        insertion boundary between alignment columns
    """
    boundary = 0
    for column_idx, column in enumerate(alignment.columns):
        if column.is_marker:
            column_time = column.marker_time_seconds
        else:
            token_midpoints = [
                (token.start_seconds + token.end_seconds) / 2
                for source_idx in source_indexes
                if (token := column.tokens[source_idx]) is not None
            ]
            column_time = None
            if token_midpoints:
                column_time = median(token_midpoints)
        if column_time is not None and column_time <= target_time:
            boundary = column_idx + 1
    return boundary


def _validate_timed_pause_arguments(
    alignment: Alignment,
    pause_intervals_seconds: AbcSequence[tuple[float, float]] | None,
    start_seconds: float | None,
    end_seconds: float | None,
    minimum_pause_seconds: float,
    pause_unit_seconds: float,
):
    """Validate timed-pause insertion settings and input alignment.

    Arguments:
        alignment: lexical alignment to annotate
        pause_intervals_seconds: explicit local pause intervals, when available
        start_seconds: optional local interval start for a leading pause
        end_seconds: optional local interval end for a trailing pause
        minimum_pause_seconds: shortest interval represented as a pause
        pause_unit_seconds: duration increment represented by each additional column
    Raises:
        ValueError: if bounds, settings, intervals, or input columns are invalid
    """
    if minimum_pause_seconds < 0.0:
        raise ValueError("Minimum timed alignment pause must be non-negative.")
    if pause_unit_seconds <= 0.0:
        raise ValueError("Timed alignment pause unit must be positive.")
    if start_seconds is not None and start_seconds < 0.0:
        raise ValueError("Timed alignment start must be non-negative.")
    if end_seconds is not None and end_seconds < 0.0:
        raise ValueError("Timed alignment end must be non-negative.")
    if (
        start_seconds is not None
        and end_seconds is not None
        and end_seconds < start_seconds
    ):
        raise ValueError("Timed alignment end must not precede its start.")
    if any(column.is_pause for column in alignment.columns):
        raise ValueError("Timed alignment already contains pause columns.")
    if pause_intervals_seconds is not None and (
        start_seconds is not None or end_seconds is not None
    ):
        raise ValueError(
            "Explicit timed pauses cannot be combined with inferred time bounds."
        )
    if pause_intervals_seconds is not None:
        for pause_start, pause_end in pause_intervals_seconds:
            if pause_start < 0.0 or pause_end <= pause_start:
                raise ValueError("Explicit timed pause intervals must be positive.")
