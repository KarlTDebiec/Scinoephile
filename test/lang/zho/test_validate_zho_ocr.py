#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.validate_zho_ocr."""

# ruff: noqa: E501

from __future__ import annotations

import logging

import pytest

from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.zho.ocr_validation import validate_zho_ocr
from test.helpers import assert_expected_warnings, get_warning_messages


def test_validate_zho_ocr_mlamd_hans(
    mlamd_zho_hans_image: ImageSeries, caplog: pytest.LogCaptureFixture
):
    """Test validate_zho_ocr with MLAMD simplified standard Chinese image subtitles.

    Arguments:
        mlamd_zho_hans_image: MLAMD simplified standard Chinese image subtitles
        caplog: pytest log capture fixture
    """
    caplog.set_level(logging.WARNING)
    validate_zho_ocr(mlamd_zho_hans_image)
    warnings = get_warning_messages(caplog.records)
    expected: list[str] = []
    assert_expected_warnings(warnings, expected, "Simplified Chinese")


def test_validate_zho_ocr_mlamd_hant(
    mlamd_zho_hant_image: ImageSeries, caplog: pytest.LogCaptureFixture
):
    """Test validate_zho_ocr with MLAMD traditional standard Chinese image subtitles.

    Arguments:
        mlamd_zho_hant_image: MLAMD traditional standard Chinese image subtitles
        caplog: pytest log capture fixture
    """
    caplog.set_level(logging.WARNING)
    validate_zho_ocr(mlamd_zho_hant_image)
    warnings = get_warning_messages(caplog.records)
    expected: list[str] = []
    assert_expected_warnings(warnings, expected, "Traditional Chinese")
