#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.yue.get_yue_romanized."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.lang.yue import get_yue_romanized

# noinspection PyProtectedMember
from scinoephile.lang.yue.romanization import _get_yue_text_romanized


def _test_get_yue_romanized(series: Series):
    """Test get_cantonese_romanization.

    Arguments:
        series: Series with which to test
    """
    output = get_yue_romanized(series)
    assert len(series) == len(output)


# get_cantonese_romanization
def test_get_yue_romanized_kob(kob_yue_hant: Series):
    """Test get_cantonese_romanization with KOB 繁体粵文 subtitles.

    Arguments:
        kob_yue_hant: KOB 繁体粤文 series fixture
    """
    _test_get_yue_romanized(kob_yue_hant)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "néih hóu sai gaai"),
    ],
)
def test_get_yue_text_romanized(text: str, expected: str):
    """Test _get_cantonese_text_romanization.

    Arguments:
        text: Text to romanize
        expected: Expected romanization
    """
    assert _get_yue_text_romanized(text) == expected
