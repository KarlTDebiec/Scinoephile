#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of character-level line alignment."""

from __future__ import annotations

import numpy as np

from scinoephile.analysis.line_alignment import (
    LineAlignment,
    LineAlignmentOperation,
)
from test.helpers import parametrize


@parametrize(
    ("one", "two", "expected_pairs"),
    [
        (
            "abc",
            "abc",
            [
                ("a", "a", LineAlignmentOperation.MATCH),
                ("b", "b", LineAlignmentOperation.MATCH),
                ("c", "c", LineAlignmentOperation.MATCH),
            ],
        ),
        (
            "abc",
            "abxc",
            [
                ("a", "a", LineAlignmentOperation.MATCH),
                ("b", "b", LineAlignmentOperation.MATCH),
                (None, "x", LineAlignmentOperation.INSERT),
                ("c", "c", LineAlignmentOperation.MATCH),
            ],
        ),
        (
            "abc",
            "ac",
            [
                ("a", "a", LineAlignmentOperation.MATCH),
                ("b", None, LineAlignmentOperation.DELETE),
                ("c", "c", LineAlignmentOperation.MATCH),
            ],
        ),
        (
            "abc",
            "axc",
            [
                ("a", "a", LineAlignmentOperation.MATCH),
                ("b", "x", LineAlignmentOperation.SUBSTITUTE),
                ("c", "c", LineAlignmentOperation.MATCH),
            ],
        ),
    ],
)
def test_line_alignment_operations(
    one: str,
    two: str,
    expected_pairs: list[tuple[str | None, str | None, LineAlignmentOperation]],
):
    """Test operation sequence for simple alignments.

    Arguments:
        one: first string
        two: second string
        expected_pairs: expected aligned character pairs
    """
    alignment = LineAlignment(one, two)
    pairs = [(pair.one, pair.two, pair.operation) for pair in alignment.alignment_pairs]
    assert pairs == expected_pairs


def test_line_alignment_operation_table_uses_numeric_array():
    """Test alignment operation table uses a compact numeric array."""
    alignment = LineAlignment("廣東話", "广东话")

    operation_table = alignment._get_operation_table()

    assert isinstance(operation_table, np.ndarray)
    assert operation_table.dtype == np.uint8
