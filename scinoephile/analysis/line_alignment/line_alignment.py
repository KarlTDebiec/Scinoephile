#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Character-level line alignment."""

from __future__ import annotations

from .line_alignment_metric import LineAlignmentMetric
from .line_alignment_operation import LineAlignmentOperation
from .line_alignment_pair import LineAlignmentPair

__all__ = ["LineAlignment"]


class LineAlignment:
    """Character-level alignment between two strings.

    Uses Levenshtein-style dynamic programming with backtrace. The fill step
    keeps only the previous and current metric rows, plus one compact operation
    table for backtrace, to avoid allocating Python objects for every candidate
    in large subtitle blocks.
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

        self.alignment_pairs: list[LineAlignmentPair] = []
        """Aligned character pairs."""

        operation_table = self._get_operation_table()
        self._populate_alignment_pairs(operation_table)

    def __repr__(self) -> str:
        """Return a reconstructable representation of this alignment.

        Returns:
            reconstructable representation
        """
        return f"{type(self).__name__}({self.one!r}, {self.two!r})"

    def _get_operation_table(  # noqa: PLR0915
        self,
    ) -> list[list[LineAlignmentOperation | None]]:
        """Get the compact dynamic-programming operation table.

        Returns:
            operation table used to backtrace the best alignment
        """
        one_length = len(self.one)
        two_length = len(self.two)

        # Initialize the backtrace-only table. Metrics are kept only for the
        # previous and current rows, but every chosen operation must be retained
        # so the final alignment can be reconstructed from bottom-right to top-left.
        operation_table = [
            [None for _ in range(two_length + 1)] for _ in range(one_length + 1)
        ]
        if two_length > 0:
            operation_table[0][1:] = [
                LineAlignmentOperation.INSERT for _ in range(two_length)
            ]

        # The top edge aligns an empty first string with prefixes of `two`, so
        # every non-origin cell is reached by one contiguous insert run.
        previous_metrics = [
            LineAlignmentMetric.for_inserts(two_idx)
            for two_idx in range(two_length + 1)
        ]
        previous_gaps: list[LineAlignmentOperation | None] = [None]
        previous_gaps.extend(LineAlignmentOperation.INSERT for _ in range(two_length))

        for one_idx in range(1, one_length + 1):
            # The left edge aligns prefixes of `one` with an empty second string,
            # so each row starts with one contiguous delete run.
            operation_table[one_idx][0] = LineAlignmentOperation.DELETE
            current_metrics = [LineAlignmentMetric.for_deletes(one_idx)]
            current_gaps: list[LineAlignmentOperation | None] = [
                LineAlignmentOperation.DELETE
            ]
            one_char = self.one[one_idx - 1]
            operation_row = operation_table[one_idx]

            for two_idx in range(1, two_length + 1):
                two_char = self.two[two_idx - 1]

                # The diagonal candidate consumes one character from both sides.
                # It is free for a match and costs one substitution otherwise.
                previous_diagonal = previous_metrics[two_idx - 1]
                if one_char == two_char:
                    best_metric = previous_diagonal
                    best_key = (
                        previous_diagonal.distance,
                        previous_diagonal.gap_runs,
                        previous_diagonal.substitutions,
                        previous_diagonal.deletions,
                        previous_diagonal.insertions,
                    )
                    best_operation = LineAlignmentOperation.MATCH
                    best_gap = None
                else:
                    best_metric = None
                    best_key = (
                        previous_diagonal.distance + 1,
                        previous_diagonal.gap_runs,
                        previous_diagonal.substitutions + 1,
                        previous_diagonal.deletions,
                        previous_diagonal.insertions,
                    )
                    best_operation = LineAlignmentOperation.SUBSTITUTE
                    best_gap = None

                # The left candidate consumes the next character from `two`.
                # Starting a new insert run is worse than extending an existing one.
                previous_insert = current_metrics[two_idx - 1]
                insert_gap_runs = previous_insert.gap_runs
                if current_gaps[two_idx - 1] != LineAlignmentOperation.INSERT:
                    insert_gap_runs += 1
                insert_key = (
                    previous_insert.distance + 1,
                    insert_gap_runs,
                    previous_insert.substitutions,
                    previous_insert.deletions,
                    previous_insert.insertions + 1,
                )
                if insert_key < best_key:
                    best_metric = None
                    best_key = insert_key
                    best_operation = LineAlignmentOperation.INSERT
                    best_gap = LineAlignmentOperation.INSERT

                # The upper candidate consumes the next character from `one`.
                # Ties are resolved by operation enum order to match prior behavior.
                previous_delete = previous_metrics[two_idx]
                delete_gap_runs = previous_delete.gap_runs
                if previous_gaps[two_idx] != LineAlignmentOperation.DELETE:
                    delete_gap_runs += 1
                delete_key = (
                    previous_delete.distance + 1,
                    delete_gap_runs,
                    previous_delete.substitutions,
                    previous_delete.deletions + 1,
                    previous_delete.insertions,
                )
                if self._is_better_candidate(
                    delete_key,
                    LineAlignmentOperation.DELETE,
                    best_key,
                    best_operation,
                ):
                    best_metric = None
                    best_key = delete_key
                    best_operation = LineAlignmentOperation.DELETE
                    best_gap = LineAlignmentOperation.DELETE

                if best_metric is None:
                    best_metric = LineAlignmentMetric(
                        best_key[0],
                        best_key[1],
                        best_key[2],
                        best_key[3],
                        best_key[4],
                    )
                current_metrics.append(best_metric)
                current_gaps.append(best_gap)
                operation_row[two_idx] = best_operation

            previous_metrics = current_metrics
            previous_gaps = current_gaps

        return operation_table

    @staticmethod
    def _is_better_candidate(
        candidate_key: tuple[int, ...],
        candidate_operation: LineAlignmentOperation,
        best_key: tuple[int, ...],
        best_operation: LineAlignmentOperation,
    ) -> bool:
        """Check whether one candidate should replace another.

        Arguments:
            candidate_key: candidate alignment metric comparison key
            candidate_operation: operation used by the candidate
            best_key: current best metric comparison key
            best_operation: operation used by the current best
        Returns:
            whether the candidate is preferred
        """
        if candidate_key < best_key:
            return True
        if candidate_key == best_key and candidate_operation < best_operation:
            return True
        return False

    def _populate_alignment_pairs(
        self,
        operation_table: list[list[LineAlignmentOperation | None]],
    ):
        """Populate alignment pairs by backtracing DP operations.

        Arguments:
            operation_table: operation table produced by dynamic programming
        """
        one_idx = len(self.one)
        two_idx = len(self.two)
        self.alignment_pairs = []
        while one_idx != 0 or two_idx != 0:
            operation = operation_table[one_idx][two_idx]
            if operation is None:
                break

            if operation in (
                LineAlignmentOperation.MATCH,
                LineAlignmentOperation.SUBSTITUTE,
            ):
                pair = LineAlignmentPair(
                    self.one[one_idx - 1],
                    self.two[two_idx - 1],
                    operation,
                )
                one_idx -= 1
                two_idx -= 1
            elif operation == LineAlignmentOperation.INSERT:
                pair = LineAlignmentPair(
                    None,
                    self.two[two_idx - 1],
                    operation,
                )
                two_idx -= 1
            else:
                pair = LineAlignmentPair(
                    self.one[one_idx - 1],
                    None,
                    operation,
                )
                one_idx -= 1
            self.alignment_pairs.append(pair)

        self.alignment_pairs.reverse()
