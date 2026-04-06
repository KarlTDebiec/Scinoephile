#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.cmn.get_cmn_romanized."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.lang.cmn import get_cmn_romanized

# noinspection PyProtectedMember
from scinoephile.lang.cmn.romanization import _get_cmn_text_romanized


def _test_get_cmn_romanized(series: Series, expected: Series):
    """Test get_cmn_romanized.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_cmn_romanized(series, append=True)
    assert output == expected


@pytest.mark.parametrize(
    ("series_fixture", "expected_fixture"),
    [
        (
            "mlamd_zho_hans_fuse_clean_validate_proofread_flatten",
            "mlamd_zho_hans_fuse_clean_validate_proofread_flatten_romanize",
        ),
        (
            "mnt_zho_hans_fuse_clean_validate_proofread_flatten",
            "mnt_zho_hans_fuse_clean_validate_proofread_flatten_romanize",
        ),
        (
            "t_zho_hans_fuse_clean_validate_proofread_flatten",
            "t_zho_hans_fuse_clean_validate_proofread_flatten_romanize",
        ),
    ],
)
def test_get_cmn_romanized_titles(
    request: pytest.FixtureRequest,
    series_fixture: str,
    expected_fixture: str,
):
    """Test get_cmn_romanized against expected romanized outputs.

    Arguments:
        request: pytest request for fixture lookup
        series_fixture: Fixture name for input series
        expected_fixture: Fixture name for expected output series
    """
    _test_get_cmn_romanized(
        request.getfixturevalue(series_fixture),
        request.getfixturevalue(expected_fixture),
    )


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
