#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_float."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from pytest import raises

from scinoephile.common.exceptions import ArgumentConflictError
from scinoephile.common.validation import val_float
from test.helpers import parametrize


@parametrize(
    ("value", "expected"),
    [
        (3.14, 3.14),
        (5, 5.0),
        ("3.14", 3.14),
        (-1.5, -1.5),
    ],
)
def test_val_float_accepts_scalar_values(value: float | int | str, expected: float):
    """Test float validation accepts scalar values."""
    assert val_float(value) == expected


@parametrize(
    ("constraint", "value", "expected_error"),
    [
        ("min", -1.0, "less than minimum"),
        ("max", 11.0, "greater than maximum"),
    ],
)
def test_val_float_rejects_scalar_constraint_violations(
    constraint: str, value: float, expected_error: str
):
    """Test float validation rejects scalar constraint violations."""
    with raises(ValueError, match=expected_error):
        if constraint == "min":
            val_float(value, min_value=0.0)
        else:
            val_float(value, max_value=10.0)


def test_val_float_rejects_invalid_values_and_conflicting_constraints():
    """Test float validation rejects invalid values and conflicting constraints."""
    with raises(TypeError):
        val_float(cast(Any, None))
    with raises(TypeError):
        val_float("invalid")
    with raises(ArgumentConflictError, match="min_value must be less than"):
        val_float(5.0, min_value=5.0, max_value=5.0)


@parametrize(
    ("value", "expected"),
    [
        ([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]),
        ((1, 2, 3), [1.0, 2.0, 3.0]),
        (["1.0", "2.0", "3.0"], [1.0, 2.0, 3.0]),
    ],
)
def test_val_float_accepts_iterables(value: Iterable[Any], expected: list[float]):
    """Test float validation accepts iterable values."""
    assert val_float(value) == expected


def test_val_float_applies_iterable_constraints():
    """Test float validation applies constraints to iterable values."""
    assert val_float([1.0, 2.0, 3.0], n_values=3, min_value=0.0, max_value=4.0) == [
        1.0,
        2.0,
        3.0,
    ]
    assert val_float([], n_values=0) == []
    assert val_float(x for x in [1.0, 2.0, 3.0]) == [1.0, 2.0, 3.0]

    with raises(ValueError, match="is of length"):
        val_float([1.0, 2.0], n_values=3)
    with raises(ValueError, match="less than minimum"):
        val_float([1.0, -1.0, 3.0], min_value=0.0)
    with raises(ValueError, match="greater than maximum"):
        val_float([1.0, 11.0, 3.0], max_value=10.0)
    with raises(TypeError):
        val_float([1.0, "invalid", 3.0])
