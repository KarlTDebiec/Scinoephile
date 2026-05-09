#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Tesseract OCR subtitle fixtures."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series


@pytest.mark.parametrize(
    "fixture_name",
    [
        "mlamd_eng_ocr_tesseract_new",
        "mlamd_zho_hans_ocr_tesseract_new",
        "mlamd_zho_hant_ocr_tesseract_new",
    ],
)
def test_mlamd_tesseract_fixtures_parse(
    request: pytest.FixtureRequest,
    fixture_name: str,
):
    """Test MLAMD Tesseract fixtures parse as subtitle series.

    Arguments:
        request: pytest request
        fixture_name: Tesseract OCR fixture name
    """
    series: Series = request.getfixturevalue(fixture_name)

    assert len(series) > 0
