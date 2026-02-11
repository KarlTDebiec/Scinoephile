#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.eng.validate_eng_ocr."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from pytest import LogCaptureFixture

from scinoephile.lang.eng import validate_eng_ocr
from test.helpers import assert_expected_warnings, get_warning_messages

if TYPE_CHECKING:
    from scinoephile.image.subtitles import ImageSeries


def test_validate_eng_ocr_mlamd(
    mlamd_eng_image: ImageSeries, caplog: LogCaptureFixture
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
