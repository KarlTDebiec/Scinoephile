#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_converted."""

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.lang.zho import get_zho_converted
from scinoephile.lang.zho.conversion import OpenCCConfig, get_zho_converter


def _test_get_zho_converted(series: Series, config: OpenCCConfig, expected):
    """Test get_zho_converted.

    Arguments:
        series: Series with which to test
        config: OpenCCConfig for conversion
        expected: Expected output series
    """
    output = get_zho_converted(series, config)
    assert len(series) == len(output)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


def test_get_zho_converted_kob(
    kob_yue_hant: Series,
    kob_yue_hant_simplify: Series,
):
    """Test get_zho_converted with KOB 繁体粤文 subtitles.

    Arguments:
        kob_yue_hant: KOB 繁体粤文 series fixture
        kob_yue_hant_simplify: Expected simplified KOB 繁体粤文 series fixture
    """
    _test_get_zho_converted(kob_yue_hant, OpenCCConfig.hk2s, kob_yue_hant_simplify)


def test_get_zho_converted_mnt(
    mnt_zho_hant_clean_flatten: Series,
    mnt_zho_hant_clean_flatten_simplify: Series,
):
    """Test get_zho_converted with MNT 繁体中文 subtitles.

    Arguments:
        mnt_zho_hant_clean_flatten: MNT 繁体中文 series fixture
        mnt_zho_hant_clean_flatten_simplify: Expected simplified MNT 繁体中文 series
          fixture
    """
    _test_get_zho_converted(
        mnt_zho_hant_clean_flatten,
        OpenCCConfig.t2s,
        mnt_zho_hant_clean_flatten_simplify,
    )


def test_get_zho_converted_t(
    t_zho_hant: Series,
    t_zho_hant_simplify: Series,
):
    """Test get_zho_converted with T 繁体中文 subtitles.

    Arguments:
        t_zho_hant: T 繁体中文 series fixture
        t_zho_hant_simplify: Expected simplified T 繁体中文 series fixture
    """
    _test_get_zho_converted(t_zho_hant, OpenCCConfig.t2s, t_zho_hant_simplify)


@pytest.mark.parametrize(
    ("text", "config", "expected"),
    [
        ("漢字轉換", OpenCCConfig.t2s, "汉字转换"),
        ("汉字转换", OpenCCConfig.s2t, "漢字轉換"),
    ],
)
def test_get_zho_converter(text: str, config: OpenCCConfig, expected: str):
    """Test get_zho_converter.

    Arguments:
        text: Text to convert
        config: Conversion configuration
        expected: Expected converted text
    """
    assert get_zho_converter(config).convert(text) == expected
