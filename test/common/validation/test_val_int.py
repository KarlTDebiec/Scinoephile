#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_int."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, cast

from pytest import raises

from scinoephile.common.exceptions import ArgumentConflictError
from scinoephile.common.validation import val_int
from test.helpers import parametrize


@parametrize(
    ("value", "expected"),
    [
        (5, 5),
        (5.0, 5),
        ("5", 5),
        (-3, -3),
    ],
)
def test_val_int_accepts_scalar_values(value: float | int | str, expected: int):
    """Test int validation accepts scalar values."""
    assert val_int(value) == expected


@parametrize(
    ("constraint", "expected_error"),
    [
        ("min", "less than minimum"),
        ("max", "greater than maximum"),
        ("acceptable", "is not one of"),
    ],
)
def test_val_int_rejects_scalar_constraint_violations(
    constraint: str, expected_error: str
):
    """Test int validation rejects scalar constraint violations."""
    with raises(ValueError, match=expected_error):
        if constraint == "min":
            val_int(-1, min_value=0)
        elif constraint == "max":
            val_int(11, max_value=10)
        else:
            val_int(11, acceptable_values=[1, 2, 3])


def test_val_int_rejects_invalid_values_and_conflicting_constraints():
    """Test int validation rejects invalid values and conflicting constraints."""
    with raises(TypeError):
        val_int(cast(Any, None))
    with raises(TypeError):
        val_int("invalid")
    with raises(ArgumentConflictError, match="min_value must be less than"):
        val_int(5, min_value=5, max_value=5)


@parametrize(
    ("value", "expected"),
    [
        ([1, 2, 3], [1, 2, 3]),
        ((1.0, 2.0, 3.0), [1, 2, 3]),
        (["1", "2", "3"], [1, 2, 3]),
    ],
)
def test_val_int_accepts_iterables(value: Iterable[Any], expected: list[int]):
    """Test int validation accepts iterable values."""
    assert val_int(value) == expected


def test_val_int_applies_iterable_constraints():
    """Test int validation applies constraints to iterable values."""
    assert val_int([1, 2, 3], n_values=3, min_value=0, max_value=4) == [1, 2, 3]
    assert val_int([], n_values=0) == []
    assert val_int(x for x in [1, 2, 3]) == [1, 2, 3]

    with raises(ValueError, match="is of length"):
        val_int([1, 2], n_values=3)
    with raises(ValueError, match="less than minimum"):
        val_int([1, -1, 3], min_value=0)
    with raises(ValueError, match="greater than maximum"):
        val_int([1, 11, 3], max_value=10)
    with raises(ValueError, match="is not one of"):
        val_int([1, 5], acceptable_values=[1, 2, 3])
    with raises(TypeError):
        val_int([1, "invalid", 3])
