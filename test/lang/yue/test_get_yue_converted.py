#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.yue.get_yue_converted."""

from __future__ import annotations

import pytest

from scinoephile.core import UnsupportedCharacterError
from scinoephile.lang.yue import get_yue_converted


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("舂暈\ue527", "舂暈鷄"),
        ("蜞\ueb06", "蜞乸"),
    ],
)
def test_get_yue_converted(text: str, expected: str):
    """Test get_yue_converted converts HKSCS characters.

    Arguments:
        text: source text
        expected: expected converted text
    """
    output = get_yue_converted(text)

    assert output == expected


@pytest.mark.parametrize(
    "text",
    [
        "過樹\uefbe",
        "蝦\ueec9",
    ],
)
def test_get_yue_converted_raises_for_unsupported_characters(text: str):
    """Test get_yue_converted rejects unsupported private-use characters.

    Arguments:
        text: source text
    """
    with pytest.raises(UnsupportedCharacterError) as exc_info:
        get_yue_converted(text)

    assert str(exc_info.value) == (
        f"Unsupported Hanzi after HKSCS normalization: {text!r} -> {text!r}"
    )
