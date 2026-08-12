#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of pairwise character alignment."""

from __future__ import annotations

import numpy as np

from scinoephile.analysis.alignment import pairwise
from test.helpers import parametrize


def test_alignment_operation_table_uses_numeric_array():
    """Test alignment operation table uses a compact numeric array."""
    alignment = pairwise.Alignment("廣東話", "广东话")

    operation_table = alignment._get_operation_table()

    assert isinstance(operation_table, np.ndarray)
    assert operation_table.dtype == np.uint8


@parametrize(
    ("one", "two", "expected_columns"),
    [
        (
            "abc",
            "abc",
            [
                ("a", "a", pairwise.Operation.MATCH),
                ("b", "b", pairwise.Operation.MATCH),
                ("c", "c", pairwise.Operation.MATCH),
            ],
        ),
        (
            "abc",
            "abxc",
            [
                ("a", "a", pairwise.Operation.MATCH),
                ("b", "b", pairwise.Operation.MATCH),
                (None, "x", pairwise.Operation.INSERT),
                ("c", "c", pairwise.Operation.MATCH),
            ],
        ),
        (
            "abc",
            "ac",
            [
                ("a", "a", pairwise.Operation.MATCH),
                ("b", None, pairwise.Operation.DELETE),
                ("c", "c", pairwise.Operation.MATCH),
            ],
        ),
        (
            "abc",
            "axc",
            [
                ("a", "a", pairwise.Operation.MATCH),
                ("b", "x", pairwise.Operation.SUBSTITUTE),
                ("c", "c", pairwise.Operation.MATCH),
            ],
        ),
    ],
)
def test_alignment_operations(
    one: str,
    two: str,
    expected_columns: list[tuple[str | None, str | None, pairwise.Operation]],
):
    """Test operation sequence for simple alignments.

    Arguments:
        one: first string
        two: second string
        expected_columns: expected aligned character columns
    """
    alignment = pairwise.Alignment(one, two)
    columns = [
        (column.one, column.two, column.operation) for column in alignment.columns
    ]
    assert columns == expected_columns
