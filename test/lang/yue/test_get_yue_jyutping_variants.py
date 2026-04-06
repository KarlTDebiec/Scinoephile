#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.yue.romanization.get_yue_jyutping_variants."""

from __future__ import annotations

import pytest

from scinoephile.lang.yue.romanization import get_yue_jyutping_variants


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("soeng6 bin6", "soeng6 bin6"),
        ("hei'hauh", "hei3 hau6"),
        ("gwóngdūngwá", "gwong2 dung1 waa2"),
    ],
)
def test_get_yue_jyutping_variants(text: str, expected: str):
    """Test get_yue_jyutping_variants.

    Arguments:
        text: raw query text
        expected: expected Jyutping variant
    """
    assert expected in get_yue_jyutping_variants(text)
