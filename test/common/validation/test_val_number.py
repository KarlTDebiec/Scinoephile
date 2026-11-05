#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared contracts for integer and float validation."""

from __future__ import annotations

from collections.abc import Callable
from contextlib import AbstractContextManager, nullcontext
from typing import Any

from common.exceptions import ArgumentConflictError
from common.validation import val_float, val_int
from pytest import mark, param, raises


@mark.parametrize("validator", [val_int, val_float], ids=["int", "float"])
@mark.parametrize(
    ("value", "options", "expected", "exception", "message"),
    [
        param(5, {}, 5, None, None, id="integer"),
        param(5.0, {}, 5, None, None, id="float"),
        param("5", {}, 5, None, None, id="string"),
        param(-3, {}, -3, None, None, id="negative"),
        param(None, {}, None, TypeError, None, id="none"),
        param("invalid", {}, None, TypeError, None, id="invalid-string"),
        param(0, {"min_value": 0}, 0, None, None, id="inclusive-min"),
        param(1, {"max_value": 1}, 1, None, None, id="inclusive-max"),
        param(
            -1, {"min_value": 0}, None, ValueError, "less than minimum", id="below-min"
        ),
        param(
            11,
            {"max_value": 10},
            None,
            ValueError,
            "greater than maximum",
            id="above-max",
        ),
        param(
            [1, 2, 3],
            {"n_values": 3, "min_value": 0, "max_value": 4},
            [1, 2, 3],
            None,
            None,
            id="list",
        ),
        param((1.0, 2.0, 3.0), {}, [1, 2, 3], None, None, id="tuple"),
        param(["1", "2", "3"], {}, [1, 2, 3], None, None, id="string-list"),
        param([], {"n_values": 0}, [], None, None, id="empty-list"),
        param(
            [1, 2], {"n_values": 3}, None, ValueError, "is of length", id="wrong-length"
        ),
        param(
            [1, -1, 3],
            {"min_value": 0},
            None,
            ValueError,
            "less than minimum",
            id="element-below-min",
        ),
        param(
            [1, 11, 3],
            {"max_value": 10},
            None,
            ValueError,
            "greater than maximum",
            id="element-above-max",
        ),
        param([1, "invalid", 3], {}, None, TypeError, None, id="invalid-element"),
    ],
)
def test_numeric_validation(
    validator: Callable[..., int | float | list[int] | list[float]],
    value: Any,
    options: dict[str, Any],
    expected: int | list[int] | None,
    exception: type[Exception] | None,
    message: str | None,
):
    """Apply shared scalar and iterable constraints with explicit outcomes.

    Arguments:
        validator: numeric validator under test
        value: deliberately valid or invalid input
        options: keyword constraints passed to the validator
        expected: converted result when validation succeeds
        exception: expected failure type, or None for success
        message: diagnostic fragment for failures
    """
    expectation: AbstractContextManager[object] = nullcontext()
    if exception is not None:
        expectation = raises(exception, match=message)
    with expectation:
        result = validator(value, **options)
        assert result == expected
        scalar_type: type[int] | type[float] = float
        if validator is val_int:
            scalar_type = int
        if isinstance(result, list):
            assert all(type(item) is scalar_type for item in result)
        else:
            assert type(result) is scalar_type


@mark.parametrize("validator", [val_int, val_float], ids=["int", "float"])
@mark.parametrize("value", [5, []], ids=["scalar", "empty-iterable"])
@mark.parametrize("bounds", [(5, 5), (6, 5)], ids=["equal", "reversed"])
def test_numeric_validation_conflicting_bounds(
    validator: Callable[..., object], value: int | list[int], bounds: tuple[int, int]
):
    """Reject conflicting bounds even when no iterable elements need checking.

    Arguments:
        validator: numeric validator under test
        value: scalar or empty iterable
        bounds: conflicting lower and upper bounds
    """
    with raises(ArgumentConflictError, match="min_value must be less than max_value"):
        validator(value, min_value=bounds[0], max_value=bounds[1])


@mark.parametrize("validator", [val_int, val_float], ids=["int", "float"])
def test_numeric_validation_consumes_generators(validator: Callable[..., object]):
    """Accept iterables that can only be consumed once.

    Arguments:
        validator: numeric validator under test
    """
    assert validator(value for value in [1, 2, 3]) == [1, 2, 3]


@mark.parametrize("value", [11, [1, 5]], ids=["scalar", "iterable"])
def test_val_int_rejects_values_outside_choices(value: int | list[int]):
    """Enforce integer-only choice constraints for scalars and iterables.

    Arguments:
        value: input containing an unsupported integer
    """
    with raises(ValueError, match="is not one of"):
        val_int(value, acceptable_values=[1, 2, 3])
