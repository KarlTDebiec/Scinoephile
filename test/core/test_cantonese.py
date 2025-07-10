#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.cantonese."""

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.cantonese import (
    _get_cantonese_text_romanization,  # noqa
    get_cantonese_romanization,
)


def _test_get_cantonese_romanization(series: Series):
    """Test get_cantonese_romanization.

    Arguments:
        series: Series with which to test
    """
    output = get_cantonese_romanization(series)
    assert len(series.events) == len(output.events)


# get_cantonese_romanization
def test_get_cantonese_romanization_kob(kob_yue_hant: Series):
    """Test get_cantonese_romanization with KOB 繁体粤文 subtitles.

    Arguments:
        kob_yue_hant: KOB 繁体粤文 series fixture
    """
    _test_get_cantonese_romanization(kob_yue_hant)


def test_get_cantonese_romanization_pdp(pdp_yue_hant: Series):
    """Test get_cantonese_romanization with PDP 繁体粤文 subtitles.

    Arguments:
        pdp_yue_hant: PDP 繁体粤文 series fixture
    """
    _test_get_cantonese_romanization(pdp_yue_hant)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("你好世界", "néih hóu sai gaai"),
    ],
)
def test_get_cantonese_text_romanization(text: str, expected: str):
    """Test _get_cantonese_text_romanization.

    Arguments:
        text: Text to romanize
        expected: Expected romanization
    """
    assert _get_cantonese_text_romanization(text) == expected
