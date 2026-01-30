#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.yue.get_yue_romanized."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.lang.yue import get_yue_romanized

# noinspection PyProtectedMember
from scinoephile.lang.yue.romanization import _get_yue_text_romanized


def _test_get_yue_romanized(series: Series, expected: Series):
    """Test get_yue_romanized.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_yue_romanized(series, append=True)
    assert output == expected


@pytest.mark.parametrize(
    ("series_fixture", "expected_fixture"),
    [
        (
            "kob_yue_hans_timewarp_clean_flatten",
            "kob_yue_hans_timewarp_clean_flatten_romanize",
        ),
    ],
)
def test_get_yue_romanized_titles(
    request: pytest.FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
):
    """Test get_yue_romanized against expected romanized outputs.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: Fixture name for input series
        expected_fixture: Fixture name for expected output series
    """
    _test_get_yue_romanized(
        request.getfixturevalue(series_fixture),
        request.getfixturevalue(expected_fixture),
    )


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
