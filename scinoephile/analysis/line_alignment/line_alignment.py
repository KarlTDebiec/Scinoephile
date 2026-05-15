#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Character-level line alignment."""

from __future__ import annotations

import numba as nb
import numpy as np

from .line_alignment_operation import LineAlignmentOperation
from .line_alignment_pair import LineAlignmentPair

__all__ = ["LineAlignment"]

_OPERATION_NONE = 255
_OPERATION_MATCH = LineAlignmentOperation.MATCH.value
_OPERATION_SUBSTITUTE = LineAlignmentOperation.SUBSTITUTE.value
_OPERATION_DELETE = LineAlignmentOperation.DELETE.value
_OPERATION_INSERT = LineAlignmentOperation.INSERT.value
_GAP_NONE = -1


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

        # Fill the alignment from the compact operation table
        operation_table = self._get_operation_table()
        self._populate_alignment_pairs(operation_table)

    def __repr__(self) -> str:
        """Return a reconstructable representation of this alignment.

        Returns:
            reconstructable representation
        """
        return f"{type(self).__name__}({self.one!r}, {self.two!r})"

    def _get_operation_table(self) -> np.ndarray:
        """Get the compact dynamic-programming operation table.

        Returns:
            operation table used to backtrace the best alignment
        """
        one = _get_codepoints(self.one)
        two = _get_codepoints(self.two)
        return _get_alignment_operation_table(one, two)

    def _populate_alignment_pairs(
        self,
        operation_table: np.ndarray,
    ):
        """Populate alignment pairs by backtracing DP operations.

        Arguments:
            operation_table: operation table produced by dynamic programming
        """
        # Start from the bottom-right table cell
        one_idx = len(self.one)
        two_idx = len(self.two)
        self.alignment_pairs = []

        # Walk backward through chosen edit operations
        while one_idx != 0 or two_idx != 0:
            operation_value = int(operation_table[one_idx, two_idx])
            if operation_value == _OPERATION_NONE:
                break
            operation = LineAlignmentOperation(operation_value)

            # Resolve matches and substitutions diagonally
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
            # Resolve insertions horizontally
            elif operation == LineAlignmentOperation.INSERT:
                pair = LineAlignmentPair(
                    None,
                    self.two[two_idx - 1],
                    operation,
                )
                two_idx -= 1
            # Resolve deletions vertically
            else:
                pair = LineAlignmentPair(
                    self.one[one_idx - 1],
                    None,
                    operation,
                )
                one_idx -= 1
            self.alignment_pairs.append(pair)

        # Store pairs in forward order
        self.alignment_pairs.reverse()


@nb.jit(nopython=True, nogil=True, cache=True)
def _get_alignment_operation_table(  # noqa: PLR0915
    one: np.ndarray,
    two: np.ndarray,
) -> np.ndarray:
    """Get the compact dynamic-programming operation table.

    Arguments:
        one: first string as Unicode code points
        two: second string as Unicode code points
    Returns:
        operation table used to backtrace the best alignment
    """
    # Allocate backtrace table and rolling metric state
    one_length = len(one)
    two_length = len(two)
    operation_table = np.full(
        (one_length + 1, two_length + 1),
        _OPERATION_NONE,
        dtype=np.uint8,
    )
    if two_length > 0:
        operation_table[0, 1:] = _OPERATION_INSERT

    previous_metrics = np.zeros((two_length + 1, 5), dtype=np.int32)
    current_metrics = np.empty((two_length + 1, 5), dtype=np.int32)
    previous_gaps = np.empty(two_length + 1, dtype=np.int16)
    current_gaps = np.empty(two_length + 1, dtype=np.int16)

    # Seed the first row with insertions
    previous_gaps[0] = _GAP_NONE
    for two_idx in range(1, two_length + 1):
        _set_metric(previous_metrics, two_idx, two_idx, 1, 0, 0, two_idx)
        previous_gaps[two_idx] = _OPERATION_INSERT

    # Fill each dynamic-programming row
    for one_idx in range(1, one_length + 1):
        # Seed the first column with deletions
        operation_table[one_idx, 0] = _OPERATION_DELETE
        _set_metric(current_metrics, 0, one_idx, 1, 0, one_idx, 0)
        current_gaps[0] = _OPERATION_DELETE
        one_char = one[one_idx - 1]

        for two_idx in range(1, two_length + 1):
            # Choose the diagonal match or substitution candidate
            two_char = two[two_idx - 1]
            previous_diagonal_idx = two_idx - 1
            if one_char == two_char:
                best_0 = previous_metrics[previous_diagonal_idx, 0]
                best_1 = previous_metrics[previous_diagonal_idx, 1]
                best_2 = previous_metrics[previous_diagonal_idx, 2]
                best_3 = previous_metrics[previous_diagonal_idx, 3]
                best_4 = previous_metrics[previous_diagonal_idx, 4]
                best_operation = _OPERATION_MATCH
                best_gap = _GAP_NONE
            else:
                best_0 = previous_metrics[previous_diagonal_idx, 0] + 1
                best_1 = previous_metrics[previous_diagonal_idx, 1]
                best_2 = previous_metrics[previous_diagonal_idx, 2] + 1
                best_3 = previous_metrics[previous_diagonal_idx, 3]
                best_4 = previous_metrics[previous_diagonal_idx, 4]
                best_operation = _OPERATION_SUBSTITUTE
                best_gap = _GAP_NONE

            # Compare the insertion candidate
            previous_insert_idx = two_idx - 1
            insert_1 = current_metrics[previous_insert_idx, 1]
            if current_gaps[previous_insert_idx] != _OPERATION_INSERT:
                insert_1 += 1
            insert_0 = current_metrics[previous_insert_idx, 0] + 1
            insert_2 = current_metrics[previous_insert_idx, 2]
            insert_3 = current_metrics[previous_insert_idx, 3]
            insert_4 = current_metrics[previous_insert_idx, 4] + 1
            if _is_metric_less(
                insert_0,
                insert_1,
                insert_2,
                insert_3,
                insert_4,
                best_0,
                best_1,
                best_2,
                best_3,
                best_4,
            ):
                best_0 = insert_0
                best_1 = insert_1
                best_2 = insert_2
                best_3 = insert_3
                best_4 = insert_4
                best_operation = _OPERATION_INSERT
                best_gap = _OPERATION_INSERT

            # Compare the deletion candidate
            delete_1 = previous_metrics[two_idx, 1]
            if previous_gaps[two_idx] != _OPERATION_DELETE:
                delete_1 += 1
            delete_0 = previous_metrics[two_idx, 0] + 1
            delete_2 = previous_metrics[two_idx, 2]
            delete_3 = previous_metrics[two_idx, 3] + 1
            delete_4 = previous_metrics[two_idx, 4]
            delete_is_less = _is_metric_less(
                delete_0,
                delete_1,
                delete_2,
                delete_3,
                delete_4,
                best_0,
                best_1,
                best_2,
                best_3,
                best_4,
            )
            delete_is_equal = _is_metric_equal(
                delete_0,
                delete_1,
                delete_2,
                delete_3,
                delete_4,
                best_0,
                best_1,
                best_2,
                best_3,
                best_4,
            )
            if delete_is_less or (
                delete_is_equal and _OPERATION_DELETE < best_operation
            ):
                best_0 = delete_0
                best_1 = delete_1
                best_2 = delete_2
                best_3 = delete_3
                best_4 = delete_4
                best_operation = _OPERATION_DELETE
                best_gap = _OPERATION_DELETE

            # Store the chosen candidate and operation
            _set_metric(
                current_metrics,
                two_idx,
                best_0,
                best_1,
                best_2,
                best_3,
                best_4,
            )
            current_gaps[two_idx] = best_gap
            operation_table[one_idx, two_idx] = best_operation

        # Roll current state forward
        previous_metrics, current_metrics = current_metrics, previous_metrics
        previous_gaps, current_gaps = current_gaps, previous_gaps

    return operation_table


def _get_codepoints(text: str) -> np.ndarray:
    """Convert text to Unicode code points.

    Arguments:
        text: text to convert
    Returns:
        integer code points
    """
    return np.fromiter((ord(char) for char in text), dtype=np.int32, count=len(text))


@nb.jit(nopython=True, nogil=True, inline="always")
def _is_metric_equal(
    left_0: int,
    left_1: int,
    left_2: int,
    left_3: int,
    left_4: int,
    right_0: int,
    right_1: int,
    right_2: int,
    right_3: int,
    right_4: int,
) -> bool:
    """Check whether two alignment metrics are equal.

    Arguments:
        left_0: first element of the left metric
        left_1: second element of the left metric
        left_2: third element of the left metric
        left_3: fourth element of the left metric
        left_4: fifth element of the left metric
        right_0: first element of the right metric
        right_1: second element of the right metric
        right_2: third element of the right metric
        right_3: fourth element of the right metric
        right_4: fifth element of the right metric
    Returns:
        whether the two metrics are equal
    """
    return (
        left_0 == right_0
        and left_1 == right_1
        and left_2 == right_2
        and left_3 == right_3
        and left_4 == right_4
    )


@nb.jit(nopython=True, nogil=True, inline="always")
def _is_metric_less(
    left_0: int,
    left_1: int,
    left_2: int,
    left_3: int,
    left_4: int,
    right_0: int,
    right_1: int,
    right_2: int,
    right_3: int,
    right_4: int,
) -> bool:
    """Check whether one alignment metric sorts before another.

    Arguments:
        left_0: first element of the left metric
        left_1: second element of the left metric
        left_2: third element of the left metric
        left_3: fourth element of the left metric
        left_4: fifth element of the left metric
        right_0: first element of the right metric
        right_1: second element of the right metric
        right_2: third element of the right metric
        right_3: fourth element of the right metric
        right_4: fifth element of the right metric
    Returns:
        whether the left metric sorts before the right metric
    """
    if left_0 != right_0:
        return left_0 < right_0
    if left_1 != right_1:
        return left_1 < right_1
    if left_2 != right_2:
        return left_2 < right_2
    if left_3 != right_3:
        return left_3 < right_3
    return left_4 < right_4


@nb.jit(nopython=True, nogil=True, inline="always")
def _set_metric(
    metrics: np.ndarray,
    idx: int,
    value_0: int,
    value_1: int,
    value_2: int,
    value_3: int,
    value_4: int,
):
    """Set one row of the alignment metric table.

    Arguments:
        metrics: metric table to update
        idx: row index to update
        value_0: first metric value
        value_1: second metric value
        value_2: third metric value
        value_3: fourth metric value
        value_4: fifth metric value
    """
    metrics[idx, 0] = value_0
    metrics[idx, 1] = value_1
    metrics[idx, 2] = value_2
    metrics[idx, 3] = value_3
    metrics[idx, 4] = value_4
