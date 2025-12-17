#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.cmn.get_cmn_romanized."""

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.lang.cmn import get_cmn_romanized

# noinspection PyProtectedMember
from scinoephile.lang.cmn.romanization import _get_cmn_text_romanized


def _test_get_mandarin_romanization(series: Series):
    """Test get_mandarin_romanization.

    Arguments:
        series: Series with which to test
    """
    output = get_cmn_romanized(series)
    assert len(series) == len(output)


# get_mandarin_romanization
def test_get_mandarin_romanization_mnt(mnt_zho_hant: Series):
    """Test get_mandarin_romanization with MNT 繁体中文 subtitles.

    Arguments:
        mnt_zho_hant: MNT 繁体中文 series fixture
    """
    _test_get_mandarin_romanization(mnt_zho_hant)


def test_get_mandarin_romanization_t(t_zho_hans: Series):
    """Test get_mandarin_romanization with T 简体中文 subtitles.

    Arguments:
        t_zho_hans: T 简体中文 series fixture
    """
    _test_get_mandarin_romanization(t_zho_hans)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "nǐhǎo shìjiè"),
    ],
)
def test_get_mandarin_text_romanization(text: str, expected: str):
    """Test _get_mandarin_text_romanization.

    Arguments:
        text: Text to romanize
        expected: Expected romanization
    """
    assert _get_cmn_text_romanized(text) == expected
