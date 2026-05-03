#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Character-level line alignment."""

from __future__ import annotations

from .line_alignment_operation import LineAlignmentOperation
from .line_alignment_pair import LineAlignmentPair

__all__ = ["LineAlignment"]

_OPERATION_NONE = 255
_OPERATION_MATCH = LineAlignmentOperation.MATCH.value
_OPERATION_SUBSTITUTE = LineAlignmentOperation.SUBSTITUTE.value
_OPERATION_DELETE = LineAlignmentOperation.DELETE.value
_OPERATION_INSERT = LineAlignmentOperation.INSERT.value
_GAP_NONE = -1

type _MetricKey = tuple[int, int, int, int, int]


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
    ) -> list[bytearray]:
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
            bytearray([_OPERATION_NONE]) * (two_length + 1)
            for _ in range(one_length + 1)
        ]
        if two_length > 0:
            operation_table[0][1:] = bytearray([_OPERATION_INSERT]) * two_length

        # The top edge aligns an empty first string with prefixes of `two`, so
        # every non-origin cell is reached by one contiguous insert run.
        previous_metrics = [
            self._get_insert_metric(two_idx) for two_idx in range(two_length + 1)
        ]
        previous_gaps = [_GAP_NONE]
        previous_gaps.extend(_OPERATION_INSERT for _ in range(two_length))

        for one_idx in range(1, one_length + 1):
            # The left edge aligns prefixes of `one` with an empty second string,
            # so each row starts with one contiguous delete run.
            operation_table[one_idx][0] = _OPERATION_DELETE
            current_metrics = [self._get_delete_metric(one_idx)]
            current_gaps = [_OPERATION_DELETE]
            one_char = self.one[one_idx - 1]
            operation_row = operation_table[one_idx]

            for two_idx in range(1, two_length + 1):
                two_char = self.two[two_idx - 1]

                # The diagonal candidate consumes one character from both sides.
                # It is free for a match and costs one substitution otherwise.
                previous_diagonal = previous_metrics[two_idx - 1]
                if one_char == two_char:
                    best_key = previous_diagonal
                    best_operation = _OPERATION_MATCH
                    best_gap = _GAP_NONE
                else:
                    best_key = (
                        previous_diagonal[0] + 1,
                        previous_diagonal[1],
                        previous_diagonal[2] + 1,
                        previous_diagonal[3],
                        previous_diagonal[4],
                    )
                    best_operation = _OPERATION_SUBSTITUTE
                    best_gap = _GAP_NONE

                # The left candidate consumes the next character from `two`.
                # Starting a new insert run is worse than extending an existing one.
                previous_insert = current_metrics[two_idx - 1]
                insert_gap_runs = previous_insert[1]
                if current_gaps[two_idx - 1] != _OPERATION_INSERT:
                    insert_gap_runs += 1
                insert_key = (
                    previous_insert[0] + 1,
                    insert_gap_runs,
                    previous_insert[2],
                    previous_insert[3],
                    previous_insert[4] + 1,
                )
                if insert_key < best_key:
                    best_key = insert_key
                    best_operation = _OPERATION_INSERT
                    best_gap = _OPERATION_INSERT

                # The upper candidate consumes the next character from `one`.
                # Ties are resolved by operation enum order to match prior behavior.
                previous_delete = previous_metrics[two_idx]
                delete_gap_runs = previous_delete[1]
                if previous_gaps[two_idx] != _OPERATION_DELETE:
                    delete_gap_runs += 1
                delete_key = (
                    previous_delete[0] + 1,
                    delete_gap_runs,
                    previous_delete[2],
                    previous_delete[3] + 1,
                    previous_delete[4],
                )
                if delete_key < best_key or (
                    delete_key == best_key and _OPERATION_DELETE < best_operation
                ):
                    best_key = delete_key
                    best_operation = _OPERATION_DELETE
                    best_gap = _OPERATION_DELETE

                current_metrics.append(best_key)
                current_gaps.append(best_gap)
                operation_row[two_idx] = best_operation

            previous_metrics = current_metrics
            previous_gaps = current_gaps

        return operation_table

    @staticmethod
    def _get_delete_metric(count: int) -> _MetricKey:
        """Build an edge metric for forced deletes.

        Arguments:
            count: number of deleted characters
        Returns:
            metric for a prefix aligned only by deletes
        """
        if count == 0:
            return (0, 0, 0, 0, 0)
        return (count, 1, 0, count, 0)

    @staticmethod
    def _get_insert_metric(count: int) -> _MetricKey:
        """Build an edge metric for forced inserts.

        Arguments:
            count: number of inserted characters
        Returns:
            metric for a prefix aligned only by inserts
        """
        if count == 0:
            return (0, 0, 0, 0, 0)
        return (count, 1, 0, 0, count)

    def _populate_alignment_pairs(
        self,
        operation_table: list[bytearray],
    ):
        """Populate alignment pairs by backtracing DP operations.

        Arguments:
            operation_table: operation table produced by dynamic programming
        """
        one_idx = len(self.one)
        two_idx = len(self.two)
        self.alignment_pairs = []
        while one_idx != 0 or two_idx != 0:
            operation_value = operation_table[one_idx][two_idx]
            if operation_value == _OPERATION_NONE:
                break
            operation = LineAlignmentOperation(operation_value)

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
