#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.get_zho_converted."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.lang.zho.conversion import (
    OpenCCConfig,
    get_zho_converted,
    get_zho_converter,
)


def _test_get_zho_converted(series: Series, config: OpenCCConfig, expected: Series):
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
    kob_zho_hant_ocr_fuse_clean_validate_review_flatten: Series,
    kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify: Series,
):
    """Test get_zho_converted with KOB traditional standard Chinese subtitles.

    Arguments:
        kob_zho_hant_ocr_fuse_clean_validate_review_flatten: KOB traditional
          standard Chinese series fixture
        kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify: Expected
          simplified
          KOB traditional standard Chinese series fixture
    """
    _test_get_zho_converted(
        kob_zho_hant_ocr_fuse_clean_validate_review_flatten,
        OpenCCConfig.t2s,
        kob_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify,
    )


@pytest.mark.parametrize(
    ("text", "config", "expected"),
    [
        ("繁體中文", OpenCCConfig.t2s, "繁体中文"),
        ("简体中文", OpenCCConfig.s2t, "簡體中文"),
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
