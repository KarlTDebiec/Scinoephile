#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_float."""

from __future__ import annotations

from math import inf, isnan, nextafter

from common.exceptions import ArgumentConflictError
from common.validation import val_float
from pytest import mark, raises


def test_val_float_exclusive_bounds():
    """Support open bounds without changing the default closed bounds."""
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


@mark.parametrize("value", ["nan", "inf", "-inf"])
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


@mark.parametrize(
    ("value", "expected"),
    [(3.14, 3.14), ("3.14", 3.14), (-1.5, -1.5), (["1.0", "2.5"], [1.0, 2.5])],
)
def test_val_float_preserves_fractional_values(
    value: float | str | list[str], expected: float | list[float]
):
    """Keep fractional values instead of truncating them to integers.

    Arguments:
        value: fractional number, decimal string, or list of decimal strings
        expected: converted float or list of floats
    """
    assert val_float(value) == expected
