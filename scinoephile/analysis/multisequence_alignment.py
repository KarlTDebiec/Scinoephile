#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Progressive multiple-sequence alignment of timestamped characters."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from itertools import permutations
from math import floor

import numpy as np

__all__ = [
    "TimedAlignmentColumn",
    "TimedAlignmentSequence",
    "TimedAlignmentSettings",
    "TimedAlignmentToken",
    "TimedMultiSequenceAligner",
    "TimedMultiSequenceAlignment",
    "get_timed_alignment_with_markers",
    "get_timed_alignment_with_pauses",
]

type _TimedTokenSimilarity = Callable[
    ["TimedAlignmentToken", "TimedAlignmentToken"], float
]
"""Callable returning a substitution score for two timestamped tokens."""

_STATE_MATCH = 0
_STATE_GAP_IN_SEQUENCE = 1
_STATE_GAP_IN_PROFILE = 2
_STATE_NONE = 255


@dataclass(frozen=True, slots=True)
class TimedAlignmentToken:
    """One display token with a source-local time interval."""

    text: str
    """Original source text represented by this token."""
    start_seconds: float
    """Inclusive token start relative to the aligned audio."""
    end_seconds: float
    """Exclusive token end relative to the aligned audio."""

    def __post_init__(self):
        """Validate token text and timing."""
        if len(self.text) != 1:
            raise ValueError("Timed alignment tokens must contain one character.")
        if self.start_seconds < 0.0:
            raise ValueError("Timed alignment token start must be non-negative.")
        if self.end_seconds < self.start_seconds:
            raise ValueError("Timed alignment token end must not precede its start.")


@dataclass(frozen=True, slots=True)
class TimedAlignmentSequence:
    """Named ordered sequence of timestamped characters."""

    name: str
    """Stable source name."""
    tokens: tuple[TimedAlignmentToken, ...]
    """Timestamped source characters in transcription order."""

    def __post_init__(self):
        """Validate the source name and chronological token order."""
        if not self.name.strip():
            raise ValueError("Timed alignment sequence name must be nonblank.")
        previous_start = -1.0
        for token in self.tokens:
            if token.start_seconds < previous_start:
                raise ValueError(
                    "Timed alignment tokens must be chronologically ordered."
                )
            previous_start = token.start_seconds


@dataclass(frozen=True, slots=True)
class TimedAlignmentColumn:
    """One multiple-alignment column containing source tokens or gaps."""

    tokens: tuple[TimedAlignmentToken | None, ...]
    """Source-ordered token cells; None represents an alignment gap."""
    pause_interval_seconds: tuple[float, float] | None = None
    """Explicit local interval for a shared timed-pause column."""
    marker: str | None = None
    """Character displayed across every row for a timed annotation column."""
    marker_time_seconds: float | None = None
    """Local source time of a shared annotation marker."""

    def __post_init__(self):
        """Validate token cells and optional shared-pause timing."""
        if not self.tokens:
            raise ValueError("Timed alignment columns must contain source cells.")
        contains_token = any(token is not None for token in self.tokens)
        if contains_token and (
            self.pause_interval_seconds is not None or self.marker is not None
        ):
            raise ValueError("Lexical alignment columns cannot be annotations.")
        if self.pause_interval_seconds is not None and self.marker is not None:
            raise ValueError("Alignment columns cannot be both pauses and markers.")
        if (
            not contains_token
            and self.pause_interval_seconds is None
            and self.marker is None
        ):
            raise ValueError("Shared alignment gaps require a timed annotation.")
        if self.pause_interval_seconds is not None:
            start_seconds, end_seconds = self.pause_interval_seconds
            if start_seconds < 0.0:
                raise ValueError("Timed alignment pause start must be non-negative.")
            if end_seconds <= start_seconds:
                raise ValueError("Timed alignment pause duration must be positive.")
        if self.marker is None and self.marker_time_seconds is not None:
            raise ValueError("Alignment marker timing requires a marker character.")
        if self.marker is not None:
            if len(self.marker) != 1:
                raise ValueError("Alignment markers must contain one character.")
            if self.marker_time_seconds is None or self.marker_time_seconds < 0.0:
                raise ValueError("Alignment markers require non-negative timing.")

    @property
    def end_seconds(self) -> float:
        """Get the robust column end time."""
        if self.pause_interval_seconds is not None:
            return self.pause_interval_seconds[1]
        if self.marker_time_seconds is not None:
            return self.marker_time_seconds
        ends = [token.end_seconds for token in self.tokens if token is not None]
        if not ends:
            raise ValueError("Timed alignment columns cannot contain only gaps.")
        return float(np.median(ends))

    @property
    def start_seconds(self) -> float:
        """Get the robust column start time."""
        if self.pause_interval_seconds is not None:
            return self.pause_interval_seconds[0]
        if self.marker_time_seconds is not None:
            return self.marker_time_seconds
        starts = [token.start_seconds for token in self.tokens if token is not None]
        if not starts:
            raise ValueError("Timed alignment columns cannot contain only gaps.")
        return float(np.median(starts))

    @property
    def is_pause(self) -> bool:
        """Whether this is a shared timed-pause column."""
        return self.pause_interval_seconds is not None

    @property
    def is_marker(self) -> bool:
        """Whether this is a shared timed-marker column."""
        return self.marker is not None


@dataclass(frozen=True, slots=True)
class TimedMultiSequenceAlignment:
    """Multiple alignment of named timestamped character sequences."""

    source_names: tuple[str, ...]
    """Source names in row order."""
    columns: tuple[TimedAlignmentColumn, ...]
    """Alignment columns in reading order."""

    def __post_init__(self):
        """Validate row names and column widths."""
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
        """
        source_idx = self.source_names.index(source_name)
        return "".join(
            token.text
            for column in self.columns
            if (token := column.tokens[source_idx]) is not None
        )


@dataclass(frozen=True, slots=True, kw_only=True)
class TimedAlignmentSettings:
    """Affine-gap settings for progressive multiple alignment."""

    exhaustive_order_source_limit: int = 4
    """Largest source count for which every progressive order is evaluated."""
    gap_extend_score: float = -1.0
    """Score for extending an existing gap by one column."""
    gap_open_score: float = -4.0
    """Score for opening a new gap."""

    def __post_init__(self):
        """Validate alignment search and scoring settings."""
        if self.exhaustive_order_source_limit < 2:
            raise ValueError(
                "Exhaustive alignment order source limit must be at least two."
            )
        if self.gap_open_score > 0.0 or self.gap_extend_score > 0.0:
            raise ValueError("Timed alignment gap scores must be non-positive.")


class TimedMultiSequenceAligner:
    """Align timestamped sequences using progressive affine-gap alignment."""

    def __init__(
        self,
        similarity: _TimedTokenSimilarity,
        settings: TimedAlignmentSettings | None = None,
    ):
        """Initialize.

        Arguments:
            similarity: timestamp-aware token substitution scoring function
            settings: optional affine-gap scoring configuration
        """
        self.similarity = similarity
        """Timestamp-aware token substitution scoring function."""
        if settings is None:
            settings = TimedAlignmentSettings()
        self.settings = settings
        """Affine-gap scoring configuration."""

    def __call__(
        self, sequences: Sequence[TimedAlignmentSequence]
    ) -> TimedMultiSequenceAlignment:
        """Align two or more named timestamped sequences.

        For small source sets, all progressive source orders are considered and
        the alignment with the greatest source-pair score is retained. Larger
        source sets use pairwise affinity guide orders, avoiding factorial growth
        while continuing to consider every source as an initial anchor.

        Arguments:
            sequences: named timestamped character sequences
        Returns:
            source-neutral multiple alignment in the input row order
        Raises:
            ValueError: if there are too few sequences or names are duplicated
        """
        if len(sequences) < 2:
            raise ValueError("Multiple alignment requires at least two sequences.")
        source_names = tuple(sequence.name for sequence in sequences)
        if len(set(source_names)) != len(source_names):
            raise ValueError("Multiple alignment sequence names must be unique.")

        best_alignment = None
        best_score = float("-inf")
        if len(sequences) <= self.settings.exhaustive_order_source_limit:
            ordered_sequence_candidates = permutations(sequences)
        else:
            ordered_sequence_candidates = self._get_guide_orders(sequences)
        for ordered_sequences in ordered_sequence_candidates:
            candidate = self._align_in_order(ordered_sequences)
            candidate = self._get_reordered(candidate, source_names)
            candidate_score = self._get_sum_of_pairs_score(candidate)
            if candidate_score > best_score:
                best_alignment = candidate
                best_score = candidate_score
        assert best_alignment is not None
        return best_alignment

    def add_sequence(
        self, alignment: TimedMultiSequenceAlignment, sequence: TimedAlignmentSequence
    ) -> TimedMultiSequenceAlignment:
        """Align one non-authoritative sequence onto a fixed existing profile.

        Existing rows retain their mutual alignment. The added sequence may place
        new columns between them but cannot realign them against one another.

        Arguments:
            alignment: fixed multiple-sequence alignment profile
            sequence: additional sequence to project onto the profile
        Returns:
            alignment with the additional sequence appended as its final row
        Raises:
            ValueError: if the name is duplicated or pauses were already inserted
        """
        if sequence.name in alignment.source_names:
            raise ValueError("Added alignment sequence name must be unique.")
        if any(not any(column.tokens) for column in alignment.columns):
            raise ValueError("Additional sequences must be aligned before annotations.")
        return self._align_profile_to_sequence(alignment, sequence)

    def _align_in_order(
        self, sequences: Sequence[TimedAlignmentSequence]
    ) -> TimedMultiSequenceAlignment:
        """Progressively align sequences in one specified order."""
        first = sequences[0]
        alignment = TimedMultiSequenceAlignment(
            source_names=(first.name,),
            columns=tuple(TimedAlignmentColumn((token,)) for token in first.tokens),
        )
        for sequence in sequences[1:]:
            alignment = self._align_profile_to_sequence(alignment, sequence)
        return alignment

    def _align_profile_to_sequence(  # noqa: PLR0912, PLR0915
        self, profile: TimedMultiSequenceAlignment, sequence: TimedAlignmentSequence
    ) -> TimedMultiSequenceAlignment:
        """Align one existing profile to one additional sequence."""
        profile_length = len(profile.columns)
        sequence_length = len(sequence.tokens)
        shape = (profile_length + 1, sequence_length + 1)
        match_scores = np.full(shape, float("-inf"), dtype=np.float64)
        gap_in_sequence_scores = np.full(shape, float("-inf"), dtype=np.float64)
        gap_in_profile_scores = np.full(shape, float("-inf"), dtype=np.float64)
        match_backpointers = np.full(shape, _STATE_NONE, dtype=np.uint8)
        gap_in_sequence_backpointers = np.full(shape, _STATE_NONE, dtype=np.uint8)
        gap_in_profile_backpointers = np.full(shape, _STATE_NONE, dtype=np.uint8)
        match_scores[0, 0] = 0.0

        for profile_idx in range(1, profile_length + 1):
            gap_in_sequence_scores[profile_idx, 0] = (
                self.settings.gap_open_score
                + (profile_idx - 1) * self.settings.gap_extend_score
            )
            if profile_idx == 1:
                gap_in_sequence_backpointers[profile_idx, 0] = _STATE_MATCH
            else:
                gap_in_sequence_backpointers[profile_idx, 0] = _STATE_GAP_IN_SEQUENCE
        for sequence_idx in range(1, sequence_length + 1):
            gap_in_profile_scores[0, sequence_idx] = (
                self.settings.gap_open_score
                + (sequence_idx - 1) * self.settings.gap_extend_score
            )
            if sequence_idx == 1:
                gap_in_profile_backpointers[0, sequence_idx] = _STATE_MATCH
            else:
                gap_in_profile_backpointers[0, sequence_idx] = _STATE_GAP_IN_PROFILE

        for profile_idx, column in enumerate(profile.columns, 1):
            for sequence_idx, token in enumerate(sequence.tokens, 1):
                previous_match_scores = (
                    match_scores[profile_idx - 1, sequence_idx - 1],
                    gap_in_sequence_scores[profile_idx - 1, sequence_idx - 1],
                    gap_in_profile_scores[profile_idx - 1, sequence_idx - 1],
                )
                previous_match_state = int(np.argmax(previous_match_scores))
                match_scores[profile_idx, sequence_idx] = previous_match_scores[
                    previous_match_state
                ] + self._get_profile_similarity(column, token)
                match_backpointers[profile_idx, sequence_idx] = previous_match_state

                previous_gap_in_sequence_scores = (
                    match_scores[profile_idx - 1, sequence_idx]
                    + self.settings.gap_open_score,
                    gap_in_sequence_scores[profile_idx - 1, sequence_idx]
                    + self.settings.gap_extend_score,
                    gap_in_profile_scores[profile_idx - 1, sequence_idx]
                    + self.settings.gap_open_score,
                )
                previous_gap_in_sequence_state = int(
                    np.argmax(previous_gap_in_sequence_scores)
                )
                gap_in_sequence_scores[profile_idx, sequence_idx] = (
                    previous_gap_in_sequence_scores[previous_gap_in_sequence_state]
                )
                gap_in_sequence_backpointers[profile_idx, sequence_idx] = (
                    previous_gap_in_sequence_state
                )

                previous_gap_in_profile_scores = (
                    match_scores[profile_idx, sequence_idx - 1]
                    + self.settings.gap_open_score,
                    gap_in_sequence_scores[profile_idx, sequence_idx - 1]
                    + self.settings.gap_open_score,
                    gap_in_profile_scores[profile_idx, sequence_idx - 1]
                    + self.settings.gap_extend_score,
                )
                previous_gap_in_profile_state = int(
                    np.argmax(previous_gap_in_profile_scores)
                )
                gap_in_profile_scores[profile_idx, sequence_idx] = (
                    previous_gap_in_profile_scores[previous_gap_in_profile_state]
                )
                gap_in_profile_backpointers[profile_idx, sequence_idx] = (
                    previous_gap_in_profile_state
                )

        final_scores = (
            match_scores[profile_length, sequence_length],
            gap_in_sequence_scores[profile_length, sequence_length],
            gap_in_profile_scores[profile_length, sequence_length],
        )
        state = int(np.argmax(final_scores))
        profile_idx = profile_length
        sequence_idx = sequence_length
        columns = []
        while profile_idx > 0 or sequence_idx > 0:
            if state == _STATE_MATCH:
                columns.append(
                    TimedAlignmentColumn(
                        (
                            *profile.columns[profile_idx - 1].tokens,
                            sequence.tokens[sequence_idx - 1],
                        )
                    )
                )
                state = int(match_backpointers[profile_idx, sequence_idx])
                profile_idx -= 1
                sequence_idx -= 1
            elif state == _STATE_GAP_IN_SEQUENCE:
                columns.append(
                    TimedAlignmentColumn(
                        (*profile.columns[profile_idx - 1].tokens, None)
                    )
                )
                state = int(gap_in_sequence_backpointers[profile_idx, sequence_idx])
                profile_idx -= 1
            elif state == _STATE_GAP_IN_PROFILE:
                columns.append(
                    TimedAlignmentColumn(
                        (
                            *(None for _ in profile.source_names),
                            sequence.tokens[sequence_idx - 1],
                        )
                    )
                )
                state = int(gap_in_profile_backpointers[profile_idx, sequence_idx])
                sequence_idx -= 1
            else:
                raise RuntimeError("Timed multiple alignment backtrace is incomplete.")
        columns.reverse()
        return TimedMultiSequenceAlignment(
            source_names=(*profile.source_names, sequence.name), columns=tuple(columns)
        )

    def _get_guide_orders(
        self, sequences: Sequence[TimedAlignmentSequence]
    ) -> tuple[tuple[TimedAlignmentSequence, ...], ...]:
        """Get pairwise-affinity progressive orders for a large source set."""
        pairwise_scores: dict[tuple[int, int], float] = {}
        for one_idx in range(len(sequences) - 1):
            for two_idx in range(one_idx + 1, len(sequences)):
                pairwise_alignment = self._align_in_order(
                    (sequences[one_idx], sequences[two_idx])
                )
                column_count = max(len(pairwise_alignment.columns), 1)
                pairwise_scores[(one_idx, two_idx)] = (
                    self._get_sum_of_pairs_score(pairwise_alignment) / column_count
                )

        orders = []
        seen_orders = set()
        for first_idx in range(len(sequences)):
            order = [first_idx]
            remaining = list(range(len(sequences)))
            remaining.remove(first_idx)
            while remaining:
                best_idx = remaining[0]
                best_score = float("-inf")
                for candidate_idx in remaining:
                    candidate_score = 0.0
                    for profile_idx in order:
                        pair = (
                            min(profile_idx, candidate_idx),
                            max(profile_idx, candidate_idx),
                        )
                        candidate_score += pairwise_scores[pair]
                    candidate_score /= len(order)
                    if candidate_score > best_score:
                        best_idx = candidate_idx
                        best_score = candidate_score
                order.append(best_idx)
                remaining.remove(best_idx)
            order_tuple = tuple(order)
            if order_tuple in seen_orders:
                continue
            seen_orders.add(order_tuple)
            orders.append(tuple(sequences[idx] for idx in order_tuple))
        return tuple(orders)

    def _get_profile_similarity(
        self, column: TimedAlignmentColumn, token: TimedAlignmentToken
    ) -> float:
        """Get mean similarity between a profile column and one token."""
        similarities = [
            self.similarity(profile_token, token)
            for profile_token in column.tokens
            if profile_token is not None
        ]
        return sum(similarities) / len(similarities)

    def _get_reordered(
        self, alignment: TimedMultiSequenceAlignment, source_names: tuple[str, ...]
    ) -> TimedMultiSequenceAlignment:
        """Reorder alignment rows to a requested stable source order."""
        indexes = tuple(alignment.source_names.index(name) for name in source_names)
        return TimedMultiSequenceAlignment(
            source_names=source_names,
            columns=tuple(
                TimedAlignmentColumn(tuple(column.tokens[idx] for idx in indexes))
                for column in alignment.columns
            ),
        )

    def _get_sum_of_pairs_score(self, alignment: TimedMultiSequenceAlignment) -> float:
        """Score a completed alignment across every projected source pair."""
        score = 0.0
        for one_idx in range(len(alignment.source_names) - 1):
            for two_idx in range(one_idx + 1, len(alignment.source_names)):
                gap_state = None
                for column in alignment.columns:
                    one = column.tokens[one_idx]
                    two = column.tokens[two_idx]
                    if one is None and two is None:
                        continue
                    if one is not None and two is not None:
                        score += self.similarity(one, two)
                        gap_state = None
                        continue
                    current_gap_state = one is None
                    if current_gap_state == gap_state:
                        score += self.settings.gap_extend_score
                    else:
                        score += self.settings.gap_open_score
                    gap_state = current_gap_state
        return score


def get_timed_alignment_with_markers(
    alignment: TimedMultiSequenceAlignment,
    markers: Sequence[tuple[float, str]],
    *,
    source_names: Sequence[str] | None = None,
) -> TimedMultiSequenceAlignment:
    """Insert timed marker columns across every row of a lexical alignment.

    Arguments:
        alignment: lexical alignment without existing annotations
        markers: ordered local marker times and single-character labels
        source_names: rows whose token timing positions the markers, or all rows
    Returns:
        alignment with shared timed-marker columns
    Raises:
        ValueError: if markers, names, or the input alignment are invalid
    """
    if any(column.is_pause or column.is_marker for column in alignment.columns):
        raise ValueError("Markers must be inserted before other annotations.")
    source_indexes = _get_marker_source_indexes(alignment, source_names)
    markers_by_boundary: dict[int, list[TimedAlignmentColumn]] = {}
    previous_time = 0.0
    previous_boundary = 0
    for marker_time, marker in markers:
        if marker_time < previous_time:
            raise ValueError("Timed alignment markers must be chronologically ordered.")
        previous_time = marker_time
        boundary = max(
            previous_boundary,
            _get_timed_insertion_boundary(alignment, source_indexes, marker_time),
        )
        previous_boundary = boundary
        markers_by_boundary.setdefault(boundary, []).append(
            TimedAlignmentColumn(
                (None,) * len(alignment.source_names),
                marker=marker,
                marker_time_seconds=marker_time,
            )
        )

    output_columns = []
    for boundary in range(len(alignment.columns) + 1):
        output_columns.extend(markers_by_boundary.get(boundary, ()))
        if boundary < len(alignment.columns):
            output_columns.append(alignment.columns[boundary])
    return TimedMultiSequenceAlignment(
        source_names=alignment.source_names, columns=tuple(output_columns)
    )


def get_timed_alignment_with_pauses(
    alignment: TimedMultiSequenceAlignment,
    *,
    pause_intervals_seconds: Sequence[tuple[float, float]] | None = None,
    source_names: Sequence[str] | None = None,
    start_seconds: float | None = None,
    end_seconds: float | None = None,
    minimum_pause_seconds: float = 0.25,
    pause_unit_seconds: float = 0.25,
) -> TimedMultiSequenceAlignment:
    """Insert shared timed gaps from explicit intervals or source timing.

    The first pause column represents the interval beginning at
    ``minimum_pause_seconds``. Each additional ``pause_unit_seconds`` adds another
    column so approximate duration remains visible in the character alignment.

    Arguments:
        alignment: lexical alignment without existing pause columns
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
        alignment,
        pause_intervals_seconds,
        start_seconds,
        end_seconds,
        minimum_pause_seconds,
        pause_unit_seconds,
    )
    source_indexes = _get_pause_source_indexes(alignment, source_names)
    if pause_intervals_seconds is not None:
        return _get_alignment_with_explicit_pauses(
            alignment,
            pause_intervals_seconds,
            source_indexes,
            minimum_pause_seconds,
            pause_unit_seconds,
        )
    future_starts = _get_future_source_starts(alignment, source_indexes, end_seconds)

    output_columns = []
    inserted_pause_intervals = set()
    latest_end = start_seconds
    for column_idx in range(len(alignment.columns) + 1):
        next_start = future_starts[column_idx]
        if latest_end is not None and next_start is not None:
            pause_interval = (latest_end, next_start)
            pause_columns = _get_pause_columns(
                len(alignment.source_names),
                pause_interval,
                minimum_pause_seconds,
                pause_unit_seconds,
            )
            if pause_columns and pause_interval not in inserted_pause_intervals:
                inserted_pause_intervals.add(pause_interval)
                output_columns.extend(pause_columns)
        if column_idx == len(alignment.columns):
            continue

        column = alignment.columns[column_idx]
        output_columns.append(column)
        ends = [
            token.end_seconds
            for source_idx in source_indexes
            if (token := column.tokens[source_idx]) is not None
        ]
        if ends:
            column_end = max(ends)
            if latest_end is None or column_end > latest_end:
                latest_end = column_end

    return TimedMultiSequenceAlignment(
        source_names=alignment.source_names, columns=tuple(output_columns)
    )


def _get_alignment_with_explicit_pauses(
    alignment: TimedMultiSequenceAlignment,
    pause_intervals_seconds: Sequence[tuple[float, float]],
    source_indexes: tuple[int, ...],
    minimum_pause_seconds: float,
    pause_unit_seconds: float,
) -> TimedMultiSequenceAlignment:
    """Insert externally detected pauses at approximate temporal positions."""
    pauses_by_boundary: dict[int, list[TimedAlignmentColumn]] = {}
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
        pause_midpoint = (pause_start + pause_end) / 2
        boundary = max(
            previous_boundary,
            _get_timed_insertion_boundary(alignment, source_indexes, pause_midpoint),
        )
        previous_boundary = boundary
        pauses_by_boundary.setdefault(boundary, []).extend(pause_columns)

    output_columns = []
    for boundary in range(len(alignment.columns) + 1):
        output_columns.extend(pauses_by_boundary.get(boundary, ()))
        if boundary < len(alignment.columns):
            output_columns.append(alignment.columns[boundary])
    return TimedMultiSequenceAlignment(
        source_names=alignment.source_names, columns=tuple(output_columns)
    )


def _get_timed_insertion_boundary(
    alignment: TimedMultiSequenceAlignment,
    source_indexes: tuple[int, ...],
    target_time: float,
) -> int:
    """Locate the profile boundary following a local target time."""
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
            column_time = float(np.median(token_midpoints)) if token_midpoints else None
        if column_time is not None and column_time <= target_time:
            boundary = column_idx + 1
    return boundary


def _get_marker_source_indexes(
    alignment: TimedMultiSequenceAlignment, source_names: Sequence[str] | None
) -> tuple[int, ...]:
    """Resolve and validate rows whose token timing positions markers."""
    if source_names is None:
        source_names = alignment.source_names
    source_indexes = tuple(
        alignment.source_names.index(source_name) for source_name in source_names
    )
    if not source_indexes:
        raise ValueError("Timed markers require at least one source row.")
    if len(set(source_indexes)) != len(source_indexes):
        raise ValueError("Timed marker source names must be unique.")
    return source_indexes


def _get_future_source_starts(
    alignment: TimedMultiSequenceAlignment,
    source_indexes: tuple[int, ...],
    end_seconds: float | None,
) -> tuple[float | None, ...]:
    """Get the earliest selected-source token start after each boundary."""
    future_starts: list[float | None] = [None] * (len(alignment.columns) + 1)
    next_start = end_seconds
    future_starts[-1] = next_start
    for column_idx in range(len(alignment.columns) - 1, -1, -1):
        starts = [
            token.start_seconds
            for source_idx in source_indexes
            if (token := alignment.columns[column_idx].tokens[source_idx]) is not None
        ]
        if starts:
            column_start = min(starts)
            if next_start is None or column_start < next_start:
                next_start = column_start
        future_starts[column_idx] = next_start
    return tuple(future_starts)


def _get_pause_columns(
    source_count: int,
    interval_seconds: tuple[float, float],
    minimum_pause_seconds: float,
    pause_unit_seconds: float,
) -> tuple[TimedAlignmentColumn, ...]:
    """Encode one shared timing gap as duration-bucketed pause columns."""
    start_seconds, end_seconds = interval_seconds
    duration_seconds = end_seconds - start_seconds
    if duration_seconds < minimum_pause_seconds or duration_seconds <= 0.0:
        return ()
    pause_count = 1 + floor(
        (duration_seconds - minimum_pause_seconds + 1e-9) / pause_unit_seconds
    )
    return tuple(
        TimedAlignmentColumn(
            (None,) * source_count,
            (
                start_seconds + pause_idx * pause_unit_seconds,
                end_seconds
                if pause_idx == pause_count - 1
                else start_seconds + (pause_idx + 1) * pause_unit_seconds,
            ),
        )
        for pause_idx in range(pause_count)
    )


def _get_pause_source_indexes(
    alignment: TimedMultiSequenceAlignment, source_names: Sequence[str] | None
) -> tuple[int, ...]:
    """Resolve and validate rows whose shared gaps define pauses."""
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


def _validate_timed_pause_arguments(
    alignment: TimedMultiSequenceAlignment,
    pause_intervals_seconds: Sequence[tuple[float, float]] | None,
    start_seconds: float | None,
    end_seconds: float | None,
    minimum_pause_seconds: float,
    pause_unit_seconds: float,
) -> None:
    """Validate timed-pause insertion settings and input alignment."""
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
