#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_literal."""

from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext
from typing import Any, Literal

from common.exceptions import ArgumentConflictError
from common.validation import val_literal
from pytest import mark, param, raises

type Color = Literal["red", "green", "blue"]
type Level = Literal[1, 2, 3]


@mark.parametrize(
    ("value", "literal_type", "exception", "message"),
    [
        param("green", Literal["red", "green", "blue"], None, None, id="literal"),
        param("red", Color, None, None, id="string-alias"),
        param(2, Level, None, None, id="integer-alias"),
        param("yellow", Color, ValueError, "not one of options", id="invalid-choice"),
        param(
            "red",
            str,
            ArgumentConflictError,
            "does not contain Literal options",
            id="not-literal",
        ),
    ],
)
def test_val_literal(
    value: str | int,
    literal_type: Any,
    exception: type[Exception] | None,
    message: str | None,
):
    """Validate literal types and aliases without coercing their values.

    Arguments:
        value: candidate literal value
        literal_type: runtime type expression passed to the validator
        exception: expected error type, or None for success
        message: expected diagnostic fragment
    """
    expectation: AbstractContextManager[object] = nullcontext()
    if exception is not None:
        expectation = raises(exception, match=message)
    with expectation:
        assert val_literal(value, literal_type) == value
