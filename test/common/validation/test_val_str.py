#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of common.validation.val_str."""

from __future__ import annotations

from common.validation import val_str
from pytest import mark, raises


@mark.parametrize(
    ("value", "options", "message"),
    [
        (
            "invalid",
            ["option1", "option2"],
            "'invalid' is not one of the supported values: option1, option2",
        ),
        (None, ["option1", "option2"], "'none' is not one of the supported values"),
        ("any", [], "'any' is not one of the supported values: $"),
    ],
    ids=["unknown", "none-input", "empty-options"],
)
def test_val_str_rejects_unknown_choice(
    value: str | None, options: list[str], message: str
):
    """Reject values outside the allowed choices, including an empty choice set.

    Arguments:
        value: invalid candidate value
        options: allowed choices
        message: expected diagnostic fragment
    """
    with raises(ValueError, match=message):
        val_str(value, options)


@mark.parametrize(
    ("value", "options", "expected"),
    [
        ("option2", ["option1", "option2"], "option2"),
        ("Option1", ["option1", "option2"], "option1"),
        ("option1", ["OPTION1", "OPTION2"], "OPTION1"),
        (1, ["1", "2"], "1"),
        ("NONE", [None, "option2"], "None"),
        ("ONLY", ["only"], "only"),
    ],
    ids=[
        "membership",
        "case-insensitive",
        "canonical-case",
        "integer",
        "none-option",
        "single-option",
    ],
)
def test_val_str_returns_canonical_choice(
    value: str | int, options: list[str | None], expected: str
):
    """Normalize input and return the matching option's string representation.

    Arguments:
        value: candidate value
        options: allowed choices before string conversion
        expected: canonical string for the matching choice
    """
    assert val_str(value, options) == expected
