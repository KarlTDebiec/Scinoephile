#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.eng.validate_eng_ocr."""

from __future__ import annotations

import logging

import pytest

from scinoephile.core.testing import assert_expected_warnings, get_warning_messages
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng import validate_eng_ocr


def test_validate_eng_ocr_mlamd(
    mlamd_eng_image: ImageSeries, caplog: pytest.LogCaptureFixture
):
    """Test validate_eng_ocr with MLAMD English image subtitles.

    Arguments:
        mlamd_eng_image: MLAMD English image subtitles
        caplog: pytest log capture fixture
    """
    caplog.set_level(logging.WARNING)
    validate_eng_ocr(mlamd_eng_image, interactive=False)
    warnings = get_warning_messages(caplog.records)
    assert_expected_warnings(warnings, [], "English")
