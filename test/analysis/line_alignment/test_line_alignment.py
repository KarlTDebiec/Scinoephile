#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of character-level line alignment."""

from __future__ import annotations

import numpy as np
import pytest

from scinoephile.analysis.line_alignment import (
    LineAlignment,
    LineAlignmentOperation,
)


@pytest.mark.parametrize(
    ("one", "two", "expected_counts"),
    [
        ("abc", "abc", {LineAlignmentOperation.MATCH: 3}),
        (
            "abc",
            "abxc",
            {
                LineAlignmentOperation.INSERT: 1,
                LineAlignmentOperation.MATCH: 3,
            },
        ),
        (
            "abc",
            "ac",
            {
                LineAlignmentOperation.DELETE: 1,
                LineAlignmentOperation.MATCH: 2,
            },
        ),
        (
            "abc",
            "axc",
            {
                LineAlignmentOperation.SUBSTITUTE: 1,
                LineAlignmentOperation.MATCH: 2,
            },
        ),
    ],
)
def test_line_alignment_operations(
    one: str,
    two: str,
    expected_counts: dict[LineAlignmentOperation, int],
):
    """Test operation counts for simple alignments.

    Arguments:
        one: first string
        two: second string
        expected_counts: expected operation counts
    """
    alignment = LineAlignment(one, two)
    ops = [c.operation for c in alignment.alignment_pairs]
    assert len(ops) == sum(expected_counts.values())
    for operation, expected_count in expected_counts.items():
        assert ops.count(operation) == expected_count


def test_line_alignment_operation_table_uses_numeric_array():
    """Test alignment operation table uses a compact numeric array."""
    alignment = object.__new__(LineAlignment)
    alignment.one = "廣東話"
    alignment.two = "广东话"

    operation_table = alignment._get_operation_table()

    assert isinstance(operation_table, np.ndarray)
    assert operation_table.dtype == np.uint8
