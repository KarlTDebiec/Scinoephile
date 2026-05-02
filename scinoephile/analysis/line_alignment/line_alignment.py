#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Character-level line alignment."""

from __future__ import annotations

from .line_alignment_backpointer import LineAlignmentBackpointer
from .line_alignment_metric import LineAlignmentMetric
from .line_alignment_operation import LineAlignmentOperation
from .line_alignment_pair import LineAlignmentPair

__all__ = ["LineAlignment"]

type _LineAlignmentCandidate = tuple[
    LineAlignmentMetric,
    LineAlignmentBackpointer,
    LineAlignmentOperation | None,
]


class LineAlignment:
    """Character-level alignment between two strings.

    Uses Levenshtein-style dynamic programming with backtrace. The metric,
    backpointer, and trailing-gap tables are owned by the alignment object so
    callers and helper methods do not need to pass them around explicitly.
    """

    def __init__(self, one: str, two: str):
        """Initialize and fill dynamic-programming tables.

        Arguments:
            one: first string
            two: second string
        """
        self.one = one
        """First string."""

        self.two = two
        """Second string."""

        self.metrics: list[list[LineAlignmentMetric]] = []
        """Dynamic-programming metric table."""

        self.backpointers: list[list[LineAlignmentBackpointer | None]] = []
        """Backpointer table used to reconstruct the chosen path."""

        self.last_gap_operations: list[list[LineAlignmentOperation | None]] = []
        """Last gap operation table used to count contiguous gap runs."""

        self.alignment_pairs: list[LineAlignmentPair] = []
        """Aligned character pairs."""

        self._init_tables()
        self._init_edges()
        self._fill_tables()
        self._populate_alignment_pairs()

    def __repr__(self) -> str:
        """Return a reconstructable representation of this alignment.

        Returns:
            reconstructable representation
        """
        return f"{type(self).__name__}({self.one!r}, {self.two!r})"

    def _populate_alignment_pairs(self):
        """Populate alignment pairs by backtracing DP pointers."""
        # Start from the cell representing the full `one` and `two` strings.
        one_idx = len(self.one)
        two_idx = len(self.two)

        # Follow backpointers until both prefixes have been consumed
        self.alignment_pairs = []
        while one_idx != 0 or two_idx != 0:
            backpointer = self.backpointers[one_idx][two_idx]
            if backpointer is None:
                break
            operation = backpointer.operation

            # Match and substitute operations consume one character from each string
            if operation in (
                LineAlignmentOperation.MATCH,
                LineAlignmentOperation.SUBSTITUTE,
            ):
                pair = LineAlignmentPair(
                    self.one[one_idx - 1], self.two[two_idx - 1], operation
                )
            # Insert operations consume one character from `two` only
            elif operation == LineAlignmentOperation.INSERT:
                pair = LineAlignmentPair(None, self.two[two_idx - 1], operation)
            # Delete operations consume one character from `one` only
            else:
                pair = LineAlignmentPair(self.one[one_idx - 1], None, operation)
            self.alignment_pairs.append(pair)

            # Move to the previous prefix selected by dynamic programming
            one_idx = backpointer.previous_i
            two_idx = backpointer.previous_j

        # Backtrace emits pairs from the end of the strings to the beginning
        self.alignment_pairs.reverse()

    def _fill_tables(self):
        """Fill DP tables for alignment."""
        # Fill each interior cell from the filled cells to the left and above
        for one_idx in range(1, len(self.one) + 1):
            for two_idx in range(1, len(self.two) + 1):
                previous_metric = self.metrics[one_idx - 1][two_idx - 1]

                # Start with the diagonal candidate: a free match when the
                # current characters agree, otherwise one substitution
                if self.one[one_idx - 1] == self.two[two_idx - 1]:
                    best = (
                        previous_metric,
                        LineAlignmentBackpointer(
                            previous_i=one_idx - 1,
                            previous_j=two_idx - 1,
                            operation=LineAlignmentOperation.MATCH,
                        ),
                        None,
                    )
                else:
                    best = (
                        LineAlignmentMetric(
                            distance=previous_metric.distance + 1,
                            gap_runs=previous_metric.gap_runs,
                            insertions=previous_metric.insertions,
                            deletions=previous_metric.deletions,
                            substitutions=previous_metric.substitutions + 1,
                        ),
                        LineAlignmentBackpointer(
                            previous_i=one_idx - 1,
                            previous_j=two_idx - 1,
                            operation=LineAlignmentOperation.SUBSTITUTE,
                        ),
                        None,
                    )

                # Compare the candidate that inserts the current character from `two`
                insert_candidate = self._get_insert_candidate(one_idx, two_idx)
                if self._is_better_candidate(insert_candidate, best):
                    best = insert_candidate

                # Compare the candidate that deletes the current character from `one`
                delete_candidate = self._get_delete_candidate(one_idx, two_idx)
                if self._is_better_candidate(delete_candidate, best):
                    best = delete_candidate

                # Persist the winning candidate
                self.metrics[one_idx][two_idx] = best[0]
                self.backpointers[one_idx][two_idx] = best[1]
                self.last_gap_operations[one_idx][two_idx] = best[2]

    def _get_delete_candidate(
        self,
        one_idx: int,
        two_idx: int,
    ) -> _LineAlignmentCandidate:
        """Build the candidate produced by deleting a character from `one`.

        Arguments:
            one_idx: current index in `one`
            two_idx: current index in `two`
        Returns:
            metric, backpointer, and trailing gap operation for the candidate
        """
        previous_metric = self.metrics[one_idx - 1][two_idx]

        # Starting a delete after a non-delete operation begins a new gap run
        add_run = 0
        if (
            self.last_gap_operations[one_idx - 1][two_idx]
            != LineAlignmentOperation.DELETE
        ):
            add_run = 1

        # Deleting consumes one character from `one` and leaves `two` unchanged
        return (
            LineAlignmentMetric(
                distance=previous_metric.distance + 1,
                gap_runs=previous_metric.gap_runs + add_run,
                insertions=previous_metric.insertions,
                deletions=previous_metric.deletions + 1,
                substitutions=previous_metric.substitutions,
            ),
            LineAlignmentBackpointer(
                previous_i=one_idx - 1,
                previous_j=two_idx,
                operation=LineAlignmentOperation.DELETE,
            ),
            LineAlignmentOperation.DELETE,
        )

    def _get_insert_candidate(
        self,
        one_idx: int,
        two_idx: int,
    ) -> _LineAlignmentCandidate:
        """Build the candidate produced by inserting a character from `two`.

        Arguments:
            one_idx: current index in `one`
            two_idx: current index in `two`
        Returns:
            metric, backpointer, and trailing gap operation for the candidate
        """
        previous_metric = self.metrics[one_idx][two_idx - 1]

        # Starting an insert after a non-insert operation begins a new gap run
        add_run = 0
        if (
            self.last_gap_operations[one_idx][two_idx - 1]
            != LineAlignmentOperation.INSERT
        ):
            add_run = 1

        # Inserting consumes one character from `two` and leaves `one` unchanged
        return (
            LineAlignmentMetric(
                distance=previous_metric.distance + 1,
                gap_runs=previous_metric.gap_runs + add_run,
                insertions=previous_metric.insertions + 1,
                deletions=previous_metric.deletions,
                substitutions=previous_metric.substitutions,
            ),
            LineAlignmentBackpointer(
                previous_i=one_idx,
                previous_j=two_idx - 1,
                operation=LineAlignmentOperation.INSERT,
            ),
            LineAlignmentOperation.INSERT,
        )

    def _init_edges(self):
        """Initialize DP boundary conditions before filling interior cells."""
        # Initialize the left edge: only deletes can consume `one` when `two` is empty
        for one_idx in range(1, len(self.one) + 1):
            previous_metric = self.metrics[one_idx - 1][0]

            # The first delete starts a gap run; consecutive deletes continue it
            add_run = 0
            if (
                self.last_gap_operations[one_idx - 1][0]
                != LineAlignmentOperation.DELETE
            ):
                add_run = 1

            # Extend the previous prefix by one forced delete
            self.metrics[one_idx][0] = LineAlignmentMetric(
                distance=previous_metric.distance + 1,
                gap_runs=previous_metric.gap_runs + add_run,
                insertions=previous_metric.insertions,
                deletions=previous_metric.deletions + 1,
                substitutions=previous_metric.substitutions,
            )

            # Backtrace from this edge cell to the previous prefix of `one`
            self.backpointers[one_idx][0] = LineAlignmentBackpointer(
                previous_i=one_idx - 1,
                previous_j=0,
                operation=LineAlignmentOperation.DELETE,
            )

            # Mark this edge cell as ending in a delete gap.
            self.last_gap_operations[one_idx][0] = LineAlignmentOperation.DELETE

        # Initialize the top edge: only inserts can consume `two` when `one` is empty
        for two_idx in range(1, len(self.two) + 1):
            previous_metric = self.metrics[0][two_idx - 1]

            # The first insert starts a gap run; consecutive inserts continue it
            add_run = 0
            if (
                self.last_gap_operations[0][two_idx - 1]
                != LineAlignmentOperation.INSERT
            ):
                add_run = 1

            # Extend the previous prefix by one forced insert
            self.metrics[0][two_idx] = LineAlignmentMetric(
                distance=previous_metric.distance + 1,
                gap_runs=previous_metric.gap_runs + add_run,
                insertions=previous_metric.insertions + 1,
                deletions=previous_metric.deletions,
                substitutions=previous_metric.substitutions,
            )

            # Backtrace from this edge cell to the previous prefix of `two`
            self.backpointers[0][two_idx] = LineAlignmentBackpointer(
                previous_i=0,
                previous_j=two_idx - 1,
                operation=LineAlignmentOperation.INSERT,
            )

            # Mark this edge cell as ending in an insert gap
            self.last_gap_operations[0][two_idx] = LineAlignmentOperation.INSERT

    def _init_tables(self):
        """Initialize DP tables for alignment."""
        self.metrics = []
        self.backpointers = []
        self.last_gap_operations = []
        for _ in range(len(self.one) + 1):
            metric_row: list[LineAlignmentMetric] = []
            backpointer_row: list[LineAlignmentBackpointer | None] = []
            last_gap_operation_row: list[LineAlignmentOperation | None] = []
            for _ in range(len(self.two) + 1):
                metric_row.append(LineAlignmentMetric(0, 0, 0, 0, 0))
                backpointer_row.append(None)
                last_gap_operation_row.append(None)
            self.metrics.append(metric_row)
            self.backpointers.append(backpointer_row)
            self.last_gap_operations.append(last_gap_operation_row)

    @staticmethod
    def _is_better_candidate(
        candidate: _LineAlignmentCandidate,
        best: _LineAlignmentCandidate,
    ) -> bool:
        """Check whether one candidate should replace another.

        Arguments:
            candidate: candidate alignment step
            best: current best alignment step
        Returns:
            whether the candidate is preferred
        """
        candidate_key = candidate[0].comparison_key()
        best_key = best[0].comparison_key()
        if candidate_key < best_key:
            return True
        if candidate_key == best_key and candidate[1].operation < best[1].operation:
            return True
        return False
