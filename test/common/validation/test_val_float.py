#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_float."""

from __future__ import annotations

from collections.abc import Iterable
from math import inf, isnan, nextafter
from typing import Any, cast

from pytest import raises

from scinoephile.common.exceptions import ArgumentConflictError
from scinoephile.common.validation import val_float
from test.helpers import parametrize


@parametrize(
    ("value", "expected"), [(3.14, 3.14), (5, 5.0), ("3.14", 3.14), (-1.5, -1.5)]
)
def test_val_float_accepts_scalar_values(value: float | int | str, expected: float):
    """Test float validation accepts scalar values.

    Arguments:
        value: value
        expected: expected value
    """
    assert val_float(value) == expected


@parametrize(
    ("constraint", "value", "expected_error"),
    [("min", -1.0, "less than minimum"), ("max", 11.0, "greater than maximum")],
)
def test_val_float_rejects_scalar_constraint_violations(
    constraint: str, value: float, expected_error: str
):
    """Test float validation rejects scalar constraint violations.

    Arguments:
        constraint: constraint value
        value: value
        expected_error: expected error
    """
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
    """Test float validation accepts iterable values.

    Arguments:
        value: value
        expected: expected value
    """
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


@parametrize(("min_value", "max_value"), [(5.0, 5.0), (6.0, 5.0)])
def test_val_float_conflicting_bounds(min_value: float, max_value: float):
    """Reject equal or reversed bounds before inspecting scalar or iterable values.

    Arguments:
        min_value: lower bound that conflicts with the upper bound
        max_value: upper bound that conflicts with the lower bound
    """
    with raises(ArgumentConflictError, match="min_value must be less than max_value"):
        val_float(5, min_value=min_value, max_value=max_value)
    with raises(ArgumentConflictError, match="min_value must be less than max_value"):
        val_float([], min_value=min_value, max_value=max_value)


def test_val_float_exclusive_bounds():
    """Support open bounds without changing the default closed bounds."""
    assert val_float(0, min_value=0) == 0
    assert val_float(1, max_value=1) == 1
    assert val_float(nextafter(0, inf), min_value=0, min_exclusive=True) > 0
    assert val_float(nextafter(1, 0), max_value=1, max_exclusive=True) < 1
    assert (
        val_float(
            "0.5", min_value=0, max_value=1, min_exclusive=True, max_exclusive=True
        )
        == 0.5
    )
    with raises(ValueError, match="greater than minimum"):
        val_float(0, min_value=0, min_exclusive=True)
    with raises(ValueError, match="less than maximum"):
        val_float(1, max_value=1, max_exclusive=True)


def test_val_float_exclusive_bounds_require_values():
    """Reject exclusive-bound options without their associated bounds."""
    with raises(ArgumentConflictError, match="min_exclusive requires min_value"):
        val_float(1, min_exclusive=True)
    with raises(ArgumentConflictError, match="max_exclusive requires max_value"):
        val_float(1, max_exclusive=True)


@parametrize("value", ["nan", "inf", "-inf"])
def test_val_float_finite_constraint(value: str):
    """Reject non-finite scalars only when finite validation is requested.

    Arguments:
        value: non-finite float representation
    """
    default_value = val_float(value)
    if value == "nan":
        assert isnan(default_value)
    else:
        assert default_value == float(value)
    with raises(ValueError, match="must be finite"):
        val_float(value, finite=True)
    with raises(ValueError, match="must be finite"):
        val_float(float(value), finite=True)


def test_val_float_new_constraints_apply_to_iterables():
    """Apply open bounds and finite checks to each iterable element."""
    assert val_float(
        (x for x in [0.25, 0.75]),
        min_value=0,
        max_value=1,
        min_exclusive=True,
        max_exclusive=True,
        finite=True,
    ) == [0.25, 0.75]
    assert val_float([], n_values=0, finite=True) == []
    with raises(ValueError, match="greater than minimum"):
        val_float([0.5, 0], min_value=0, min_exclusive=True)
    with raises(ValueError, match="less than maximum"):
        val_float([0.5, 1], max_value=1, max_exclusive=True)
    with raises(ValueError, match="must be finite"):
        val_float((x for x in [0.5, inf]), finite=True)
    with raises(ValueError, match="is of length"):
        val_float([0.5], n_values=2, finite=True)
