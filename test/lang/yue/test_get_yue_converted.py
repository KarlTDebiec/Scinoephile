#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.yue.get_yue_converted."""

from __future__ import annotations

from contextlib import AbstractContextManager, nullcontext

import pytest

from scinoephile.core import UnsupportedCharacterError
from scinoephile.lang.yue.conversion import get_yue_converted


@pytest.mark.parametrize(
    ("text", "expected", "expectation"),
    [
        ("舂暈\ue527", "舂暈鷄", nullcontext()),
        ("蜞\ueb06", "蜞乸", nullcontext()),
        (
            "過樹\uefbe",
            None,
            pytest.raises(UnsupportedCharacterError),
        ),
        (
            "蝦\ueec9",
            None,
            pytest.raises(UnsupportedCharacterError),
        ),
    ],
)
def test_get_yue_converted(
    text: str,
    expected: str | None,
    expectation: AbstractContextManager[object],
):
    """Test get_yue_converted converts or rejects HKSCS characters.

    Arguments:
        text: source text
        expected: expected converted text, if conversion succeeds
        expectation: expected test context
    """
    with expectation:
        output = get_yue_converted(text)
        assert output == expected
