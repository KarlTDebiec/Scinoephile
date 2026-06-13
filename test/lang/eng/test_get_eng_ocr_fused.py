#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.eng.get_eng_ocr_fused."""

from __future__ import annotations

import pytest

from scinoephile.lang.eng.cleaning import get_eng_cleaned
from scinoephile.lang.eng.ocr_fusion import get_eng_ocr_fused
from test.helpers import assert_series_equal


@pytest.mark.parametrize(
    ("lens_fixture", "tesseract_fixture", "expected_fixture"),
    [
        ("kob_eng_ocr_lens", "kob_eng_ocr_tesseract", "kob_eng_ocr_fuse"),
        ("mlamd_eng_ocr_lens", "mlamd_eng_ocr_tesseract", "mlamd_eng_fuse"),
        ("mnt_eng_ocr_lens", "mnt_eng_ocr_tesseract", "mnt_eng_fuse"),
        ("t_eng_ocr_lens", "t_eng_ocr_tesseract", "t_eng_fuse"),
    ],
)
def test_get_eng_ocr_fused(
    request: pytest.FixtureRequest,
    lens_fixture: str,
    tesseract_fixture: str,
    expected_fixture: str,
):
    """Test get_eng_ocr_fused against expected fused outputs.

    Arguments:
        request: pytest request for fixture lookup
        lens_fixture: fixture name for Google Lens OCR subtitles
        tesseract_fixture: fixture name for Tesseract OCR subtitles
        expected_fixture: fixture name for expected output series
    """
    lens = get_eng_cleaned(request.getfixturevalue(lens_fixture), remove_empty=False)
    tesseract = get_eng_cleaned(
        request.getfixturevalue(tesseract_fixture),
        remove_empty=False,
    )
    output = get_eng_ocr_fused(lens, tesseract)

    assert len(lens) == len(output)
    assert_series_equal(output, request.getfixturevalue(expected_fixture))
