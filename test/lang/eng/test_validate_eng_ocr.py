#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.eng.validate_eng_ocr."""

from __future__ import annotations

import logging
from typing import cast

import pytest

from scinoephile.image.ocr.validation import ValidationManager
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng.ocr_validation import validate_eng_ocr
from test.helpers import assert_expected_warnings, get_warning_messages


def test_validate_eng_ocr_mlamd(
    mlamd_eng_image: ImageSeries, caplog: pytest.LogCaptureFixture
):
    """Test validate_eng_ocr with MLAMD English image subtitles.

    Arguments:
        mlamd_eng_image: MLAMD English image subtitles
        caplog: pytest log capture fixture
    """
    caplog.set_level(logging.WARNING)
    validate_eng_ocr(mlamd_eng_image)
    warnings = get_warning_messages(caplog.records)
    assert_expected_warnings(warnings, [], "English")


def test_validate_eng_ocr_configures_validation_manager(
    monkeypatch: pytest.MonkeyPatch,
    tiny_image_series: ImageSeries,
):
    """Test English OCR validation configures its validation manager.

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
        "scinoephile.lang.eng.ocr_validation.ValidationManager",
        FakeValidationManager,
    )
    output = validate_eng_ocr(tiny_image_series)

    assert output is tiny_image_series
    assert init_calls == [True]
    assert validate_calls == [tiny_image_series]


def test_validate_eng_ocr_uses_supplied_validation_manager(
    tiny_image_series: ImageSeries,
):
    """Test English OCR validation can use a supplied validation manager.

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

    output = validate_eng_ocr(tiny_image_series, manager)

    assert output is tiny_image_series
    assert validate_calls == [tiny_image_series]
