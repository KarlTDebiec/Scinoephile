#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.zho.validate_zho_ocr."""

# ruff: noqa: E501

from __future__ import annotations

import logging
from typing import cast

import pytest

from scinoephile.image.ocr.validation import ValidationManager
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


def test_validate_zho_ocr_configures_validation_manager(
    monkeypatch: pytest.MonkeyPatch,
    tiny_image_series: ImageSeries,
):
    """Test Chinese OCR validation configures its validation manager.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
        tiny_image_series: small image subtitle series
    """
    init_calls: list[bool] = []
    validate_calls: list[ImageSeries] = []

    class FakeValidationManager:
        """Fake validation manager."""

        def __init__(self):
            """Initialize."""
            init_calls.append(True)

        def validate(self, series: ImageSeries) -> ImageSeries:
            """Validate an image series."""
            validate_calls.append(series)
            return series

    monkeypatch.setattr(
        "scinoephile.lang.zho.ocr_validation.ValidationManager",
        FakeValidationManager,
    )
    output = validate_zho_ocr(tiny_image_series)

    assert output is tiny_image_series
    assert init_calls == [True]
    assert validate_calls == [tiny_image_series]


def test_validate_zho_ocr_uses_supplied_validation_manager(
    tiny_image_series: ImageSeries,
):
    """Test Chinese OCR validation can use a supplied validation manager.

    Arguments:
        tiny_image_series: small image subtitle series
    """
    validate_calls: list[ImageSeries] = []

    class FakeValidationManager:
        """Fake validation manager."""

        def validate(self, series: ImageSeries) -> ImageSeries:
            """Validate an image series."""
            validate_calls.append(series)
            return series

    manager = cast(ValidationManager, FakeValidationManager())

    output = validate_zho_ocr(tiny_image_series, manager)

    assert output is tiny_image_series
    assert validate_calls == [tiny_image_series]
