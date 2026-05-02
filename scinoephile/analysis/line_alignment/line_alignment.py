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
        i = len(self.one)
        j = len(self.two)
        self.alignment_pairs = []
        while i != 0 or j != 0:
            backpointer = self.backpointers[i][j]
            if backpointer is None:
                break
            operation = backpointer.operation
            if operation in (
                LineAlignmentOperation.MATCH,
                LineAlignmentOperation.SUBSTITUTE,
            ):
                self.alignment_pairs.append(
                    LineAlignmentPair(
                        one=self.one[i - 1], two=self.two[j - 1], operation=operation
                    )
                )
            elif operation == LineAlignmentOperation.INSERT:
                self.alignment_pairs.append(
                    LineAlignmentPair(
                        one=None, two=self.two[j - 1], operation=operation
                    )
                )
            else:
                self.alignment_pairs.append(
                    LineAlignmentPair(
                        one=self.one[i - 1], two=None, operation=operation
                    )
                )
            i = backpointer.previous_i
            j = backpointer.previous_j
        self.alignment_pairs.reverse()

    def _fill_tables(self):
        """Fill DP tables for alignment."""
        rows = len(self.one) + 1
        cols = len(self.two) + 1

        for i in range(1, rows):
            for j in range(1, cols):
                previous_metric = self.metrics[i - 1][j - 1]
                if self.one[i - 1] == self.two[j - 1]:
                    best = (
                        previous_metric,
                        LineAlignmentBackpointer(
                            previous_i=i - 1,
                            previous_j=j - 1,
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
                            previous_i=i - 1,
                            previous_j=j - 1,
                            operation=LineAlignmentOperation.SUBSTITUTE,
                        ),
                        None,
                    )

                insert_candidate = self._get_insert_candidate(i, j)
                if self._is_better_candidate(
                    candidate_metric=insert_candidate[0],
                    candidate_operation=insert_candidate[1].operation,
                    best_metric=best[0],
                    best_operation=best[1].operation,
                ):
                    best = insert_candidate

                delete_candidate = self._get_delete_candidate(i, j)
                if self._is_better_candidate(
                    candidate_metric=delete_candidate[0],
                    candidate_operation=delete_candidate[1].operation,
                    best_metric=best[0],
                    best_operation=best[1].operation,
                ):
                    best = delete_candidate

                self.metrics[i][j] = best[0]
                self.backpointers[i][j] = best[1]
                self.last_gap_operations[i][j] = best[2]

    def _get_delete_candidate(self, i: int, j: int) -> _LineAlignmentCandidate:
        """Build the candidate produced by deleting a character from `one`.

        Arguments:
            i: current row index
            j: current column index
        Returns:
            metric, backpointer, and trailing gap operation for the candidate
        """
        previous_metric = self.metrics[i - 1][j]
        add_run = 0
        if self.last_gap_operations[i - 1][j] != LineAlignmentOperation.DELETE:
            add_run = 1
        return (
            LineAlignmentMetric(
                distance=previous_metric.distance + 1,
                gap_runs=previous_metric.gap_runs + add_run,
                insertions=previous_metric.insertions,
                deletions=previous_metric.deletions + 1,
                substitutions=previous_metric.substitutions,
            ),
            LineAlignmentBackpointer(
                previous_i=i - 1,
                previous_j=j,
                operation=LineAlignmentOperation.DELETE,
            ),
            LineAlignmentOperation.DELETE,
        )

    def _get_insert_candidate(self, i: int, j: int) -> _LineAlignmentCandidate:
        """Build the candidate produced by inserting a character from `two`.

        Arguments:
            i: current row index
            j: current column index
        Returns:
            metric, backpointer, and trailing gap operation for the candidate
        """
        previous_metric = self.metrics[i][j - 1]
        add_run = 0
        if self.last_gap_operations[i][j - 1] != LineAlignmentOperation.INSERT:
            add_run = 1
        return (
            LineAlignmentMetric(
                distance=previous_metric.distance + 1,
                gap_runs=previous_metric.gap_runs + add_run,
                insertions=previous_metric.insertions + 1,
                deletions=previous_metric.deletions,
                substitutions=previous_metric.substitutions,
            ),
            LineAlignmentBackpointer(
                previous_i=i,
                previous_j=j - 1,
                operation=LineAlignmentOperation.INSERT,
            ),
            LineAlignmentOperation.INSERT,
        )

    def _init_edges(self):
        """Initialize DP boundary conditions before filling interior cells.

        The DP grid compares prefixes of `one` and `two`. Cell `(0, 0)` is the
        empty-prefix base case created in `_init_tables()`. Before the interior
        of the grid can be filled, the top row and left column need explicit
        values:

        - the left column represents aligning a non-empty prefix of `one`
          against an empty prefix of `two`, which can only be reached by deletes
        - the top row represents aligning an empty prefix of `one` against a
          non-empty prefix of `two`, which can only be reached by inserts

        This function writes those forced edge paths into the metric,
        backpointer, and trailing-gap tables.
        """
        # Initialize the left edge: only deletes can consume `one` when `two`
        # is empty.
        for i in range(1, len(self.one) + 1):
            previous_metric = self.metrics[i - 1][0]

            # The first delete starts a gap run; consecutive deletes continue it.
            add_run = 0
            if self.last_gap_operations[i - 1][0] != LineAlignmentOperation.DELETE:
                add_run = 1

            # Extend the previous prefix by one forced delete.
            self.metrics[i][0] = LineAlignmentMetric(
                distance=previous_metric.distance + 1,
                gap_runs=previous_metric.gap_runs + add_run,
                insertions=previous_metric.insertions,
                deletions=previous_metric.deletions + 1,
                substitutions=previous_metric.substitutions,
            )

            # Backtrace from this edge cell to the previous prefix of `one`.
            self.backpointers[i][0] = LineAlignmentBackpointer(
                previous_i=i - 1,
                previous_j=0,
                operation=LineAlignmentOperation.DELETE,
            )

            # Mark this edge cell as ending in a delete gap.
            self.last_gap_operations[i][0] = LineAlignmentOperation.DELETE

        # Initialize the top edge: only inserts can consume `two` when `one`
        # is empty.
        for j in range(1, len(self.two) + 1):
            previous_metric = self.metrics[0][j - 1]

            # The first insert starts a gap run; consecutive inserts continue it.
            add_run = 0
            if self.last_gap_operations[0][j - 1] != LineAlignmentOperation.INSERT:
                add_run = 1

            # Extend the previous prefix by one forced insert.
            self.metrics[0][j] = LineAlignmentMetric(
                distance=previous_metric.distance + 1,
                gap_runs=previous_metric.gap_runs + add_run,
                insertions=previous_metric.insertions + 1,
                deletions=previous_metric.deletions,
                substitutions=previous_metric.substitutions,
            )

            # Backtrace from this edge cell to the previous prefix of `two`.
            self.backpointers[0][j] = LineAlignmentBackpointer(
                previous_i=0,
                previous_j=j - 1,
                operation=LineAlignmentOperation.INSERT,
            )

            # Mark this edge cell as ending in an insert gap.
            self.last_gap_operations[0][j] = LineAlignmentOperation.INSERT

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
        *,
        candidate_metric: LineAlignmentMetric,
        candidate_operation: LineAlignmentOperation,
        best_metric: LineAlignmentMetric,
        best_operation: LineAlignmentOperation,
    ) -> bool:
        """Check whether one candidate should replace another.

        Arguments:
            candidate_metric: candidate alignment metric
            candidate_operation: candidate alignment operation
            best_metric: current best alignment metric
            best_operation: current best alignment operation
        Returns:
            whether the candidate is preferred
        """
        candidate_key = candidate_metric.comparison_key()
        best_key = best_metric.comparison_key()
        if candidate_key < best_key:
            return True
        if candidate_key == best_key and candidate_operation < best_operation:
            return True
        return False
