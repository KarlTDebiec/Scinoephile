#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.cmn.romanization.get_cmn_pinyin_query_strings."""

from __future__ import annotations

import pytest

from scinoephile.lang.cmn.romanization import get_cmn_pinyin_query_strings


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("shàng biàn", ["shang4 bian4"]),
        ("Shàng Biàn", ["shang4 bian4"]),
        ("lüè", ["lu:e4", "lüe4", "lve4"]),
        ("lu:e4", ["lu:e4", "lüe4", "lve4"]),
        ("上便", []),
    ],
)
def test_get_cmn_pinyin_query_strings(text: str, expected: list[str]):
    """Test get_cmn_pinyin_query_strings.

    Arguments:
        text: raw query text
        expected: expected query variants
    """
    assert sorted(get_cmn_pinyin_query_strings(text)) == sorted(expected)
