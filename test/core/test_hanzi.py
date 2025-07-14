#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.core.hanzi."""

from __future__ import annotations

import pytest

from scinoephile.core import Series
from scinoephile.core.hanzi import (
    OpenCCConfig,  # noqa
    _get_hanzi_text_flattened,
    get_hanzi_cleaned,
    get_hanzi_converted,
    get_hanzi_converter,
    get_hanzi_flattened,
)


# region Implementations
def _test_get_hanzi_cleaned(series: Series, expected: Series):
    """Test get_hanzi_cleaned.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_hanzi_cleaned(series)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


def _test_get_hanzi_flattened(series: Series, expected: Series):
    """Test get_hanzi_flattened.

    Arguments:
        series: Series with which to test
        expected: Expected output series
    """
    output = get_hanzi_flattened(series)
    assert len(series) == len(output)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event.text.count("\n") != 0:
            errors.append(f"Subtitle {i} contains newline")
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


def _test_get_hanzi_converted(series: Series, config: OpenCCConfig, expected):
    """Test get_hanzi_converted.

    Arguments:
        series: Series with which to test
        config: OpenCCConfig for conversion
        expected: Expected output series
    """
    output = get_hanzi_converted(series, config)
    assert len(series) == len(output)

    errors = []
    for i, (event, expected_event) in enumerate(zip(output, expected), 1):
        if event != expected_event:
            errors.append(f"Subtitle {i} does not match: {event} != {expected_event}")

    if errors:
        for error in errors:
            print(error)
        pytest.fail(f"Found {len(errors)} discrepancies")


# endregion


# region get_hanzi_cleaned
def test_get_hanzi_cleaned_kob(kob_yue_hans: Series, kob_yue_hans_clean: Series):
    """Test get_hanzi_cleaned with KOB 简体粤文 subtitles.

    Arguments:
        kob_yue_hans: KOB 简体粤文 series fixture
        kob_yue_hans_clean: Expected cleaned KOB 简体粤文 series fixture
    """
    _test_get_hanzi_cleaned(kob_yue_hans, kob_yue_hans_clean)


def test_get_hanzi_cleaned_mnt(mnt_zho_hant: Series, mnt_zho_hant_clean: Series):
    """Test get_hanzi_cleaned with MNT 繁体中文 subtitles.

    Arguments:
        mnt_zho_hant: MNT 繁体中文 series fixture
        mnt_zho_hant_clean: Expected cleaned MNT 繁体中文 series fixture
    """
    _test_get_hanzi_cleaned(mnt_zho_hant, mnt_zho_hant_clean)


def test_get_hanzi_cleaned_pdp(pdp_yue_hant: Series, pdp_yue_hant_clean: Series):
    """Test get_hanzi_cleaned with PDP 繁体粤文 subtitles.

    Arguments:
        pdp_yue_hant: PDP 繁体粤文 series fixture
        pdp_yue_hant_clean: Expected cleaned PDP 繁体粤文 series fixture
    """
    _test_get_hanzi_cleaned(pdp_yue_hant, pdp_yue_hant_clean)


def test_get_hanzi_cleaned_t(t_zho_hans: Series, t_zho_hans_clean: Series):
    """Test get_hanzi_cleaned with T 簡體中文 subtitles.

    Arguments:
        t_zho_hans: T 簡體中文 series fixture
        t_zho_hans_clean: Expected cleaned T 簡體中文 series fixture
    """
    _test_get_hanzi_cleaned(t_zho_hans, t_zho_hans_clean)


# endregion


# region get_hanzi_flattened
def test_get_hanzi_flattened_kob(kob_yue_hans: Series, kob_yue_hans_flatten: Series):
    """Test get_hanzi_flattened with KOB 简体粤文 subtitles.

    Arguments:
        kob_yue_hans: KOB 简体粤文 series fixture
        kob_yue_hans_flatten: Expected flattened KOB 简体粤文 series fixture
    """
    _test_get_hanzi_flattened(kob_yue_hans, kob_yue_hans_flatten)


def test_get_hanzi_flattened_mnt(mnt_zho_hant: Series, mnt_zho_hant_flatten: Series):
    """Test get_hanzi_flattened with MNT 繁体中文 subtitles.

    Arguments:
        mnt_zho_hant: MNT 繁体中文 series fixture
        mnt_zho_hant_flatten: Expected flattened MNT 繁体中文 series fixture
    """
    _test_get_hanzi_flattened(mnt_zho_hant, mnt_zho_hant_flatten)


def test_get_hanzi_flattened_pdp(pdp_yue_hant: Series, pdp_yue_hant_flatten: Series):
    """Test get_hanzi_flattened with PDP 繁体粤文 subtitles.

    Arguments:
        pdp_yue_hant: PDP 繁体粤文 series fixture
        pdp_yue_hant_flatten: Expected flattened PDP 繁体粤文 series fixture
    """
    _test_get_hanzi_flattened(pdp_yue_hant, pdp_yue_hant_flatten)


def test_get_hanzi_flattened_t(t_zho_hans: Series, t_zho_hans_flatten: Series):
    """Test get_hanzi_flattened with T 簡體中文 subtitles.

    Arguments:
        t_zho_hans: T 簡體中文 series fixture
        t_zho_hans_flatten: Expected flattened T 簡體中文 series fixture
    """
    _test_get_hanzi_flattened(t_zho_hans, t_zho_hans_flatten)


# endregion


# region get_hanzi_converted
def test_get_hanzi_converted_kob(kob_yue_hant: Series, kob_yue_hant_simplify: Series):
    """Test get_hanzi_converted with KOB 繁体粤文 subtitles.

    Arguments:
        kob_yue_hant: KOB 繁体粤文 series fixture
        kob_yue_hant_simplify: Expected simplified KOB 繁体粤文 series fixture
    """
    _test_get_hanzi_converted(kob_yue_hant, OpenCCConfig.hk2s, kob_yue_hant_simplify)


def test_get_hanzi_converted_mnt(mnt_zho_hant: Series, mnt_zho_hant_simplify: Series):
    """Test get_hanzi_converted with MNT 繁体中文 subtitles.

    Arguments:
        mnt_zho_hant: MNT 繁体中文 series fixture
        mnt_zho_hant_simplify: Expected simplified MNT 繁体中文 series fixture
    """
    _test_get_hanzi_converted(mnt_zho_hant, OpenCCConfig.t2s, mnt_zho_hant_simplify)


def test_get_hanzi_converted_pdp(pdp_yue_hant: Series, pdp_yue_hant_simplify: Series):
    """Test get_hanzi_converted with PDP 繁体粤文 subtitles.

    Arguments:
        pdp_yue_hant: PDP 繁体粤文 series fixture
        pdp_yue_hant_simplify: Expected simplified PDP 繁体粤文 series fixture
    """
    _test_get_hanzi_converted(pdp_yue_hant, OpenCCConfig.hk2s, pdp_yue_hant_simplify)


def test_get_hanzi_converted_t(t_zho_hant: Series, t_zho_hant_simplify: Series):
    """Test get_hanzi_converted with T 繁体中文 subtitles.

    Arguments:
        t_zho_hant: T 繁体中文 series fixture
        t_zho_hant_simplify: Expected simplified T 繁体中文 series fixture
    """
    _test_get_hanzi_converted(t_zho_hant, OpenCCConfig.t2s, t_zho_hant_simplify)


# endregion


@pytest.mark.parametrize(
    ("text", "config", "expected"),
    [
        ("漢字轉換", OpenCCConfig.t2s, "汉字转换"),
        ("汉字转换", OpenCCConfig.s2t, "漢字轉換"),
    ],
)
def test_get_hanzi_converter(text: str, config: OpenCCConfig, expected: str):
    """Test get_hanzi_converter.

    Arguments:
        text: Text to convert
        config: Conversion configuration
        expected: Expected converted text
    """
    assert get_hanzi_converter(config).convert(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("line 1\nline 2", "line 1　line 2"),
    ],
)
def test_get_hanzi_text_flattened(text: str, expected: str):
    """Test _get_hanzi_text_flattened.

    Arguments:
        text: Text to flatten
        expected: Expected flattened text
    """
    assert _get_hanzi_text_flattened(text) == expected
