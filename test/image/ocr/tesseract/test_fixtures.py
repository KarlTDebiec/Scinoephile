#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of Tesseract OCR subtitle fixtures."""

from __future__ import annotations

import pytest

from scinoephile.core.subtitles import Series
from test.helpers import test_data_root


@pytest.mark.parametrize(
    "fixture_path",
    [
        "mlamd/input/eng_ocr/tesseract3_new.srt",
        "mlamd/input/eng_ocr/tesseract5_new.srt",
        "mlamd/input/zho-Hans_ocr/tesseract3_new.srt",
        "mlamd/input/zho-Hans_ocr/tesseract5_new.srt",
        "mlamd/input/zho-Hant_ocr/tesseract3_new.srt",
        "mlamd/input/zho-Hant_ocr/tesseract5_new.srt",
    ],
)
def test_mlamd_tesseract_fixtures_parse(fixture_path: str):
    """Test MLAMD Tesseract fixtures parse as subtitle series.

    Arguments:
        fixture_path: Tesseract OCR fixture path relative to test data root
    """
    series = Series.load(test_data_root / fixture_path)

    assert len(series) > 0
