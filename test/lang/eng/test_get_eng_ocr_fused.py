#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.lang.eng.get_eng_ocr_fused."""

from __future__ import annotations

from collections.abc import Callable
from unittest.mock import Mock

import pytest

from scinoephile.core.llms import LLMProvider, TestCase
from scinoephile.lang.eng.cleaning import get_eng_cleaned
from scinoephile.lang.eng.ocr_fusion import get_eng_ocr_fused, get_eng_ocr_fuser
from test.data.kob import get_kob_eng_ocr_fusion_test_cases
from test.data.mlamd import get_mlamd_eng_ocr_fusion_test_cases
from test.data.mnt import get_mnt_eng_ocr_fusion_test_cases
from test.data.t import get_t_eng_ocr_fusion_test_cases
from test.helpers import assert_series_equal


@pytest.mark.parametrize(
    ("lens_fixture", "tesseract_fixture", "expected_fixture", "test_case_loader"),
    [
        pytest.param(
            "kob_eng_ocr_lens",
            "kob_eng_ocr_tesseract",
            "kob_eng_ocr_fuse",
            get_kob_eng_ocr_fusion_test_cases,
            id="kob-eng",
        ),
        pytest.param(
            "mlamd_eng_ocr_lens",
            "mlamd_eng_ocr_tesseract",
            "mlamd_eng_fuse",
            get_mlamd_eng_ocr_fusion_test_cases,
            id="mlamd-eng",
        ),
        pytest.param(
            "mnt_eng_ocr_lens",
            "mnt_eng_ocr_tesseract",
            "mnt_eng_fuse",
            get_mnt_eng_ocr_fusion_test_cases,
            id="mnt-eng",
        ),
        pytest.param(
            "t_eng_ocr_lens",
            "t_eng_ocr_tesseract",
            "t_eng_fuse",
            get_t_eng_ocr_fusion_test_cases,
            id="t-eng",
        ),
    ],
)
def test_get_eng_ocr_fused(
    request: pytest.FixtureRequest,
    lens_fixture: str,
    tesseract_fixture: str,
    expected_fixture: str,
    test_case_loader: Callable[[], list[TestCase]],
):
    """Test get_eng_ocr_fused against expected fused outputs.

    Arguments:
        request: pytest request for fixture lookup
        lens_fixture: fixture name for Google Lens OCR subtitles
        tesseract_fixture: fixture name for Tesseract OCR subtitles
        expected_fixture: fixture name for expected output series
        test_case_loader: loader for OCR fusion test cases
    """
    lens = get_eng_cleaned(request.getfixturevalue(lens_fixture), remove_empty=False)
    tesseract = get_eng_cleaned(
        request.getfixturevalue(tesseract_fixture),
        remove_empty=False,
    )
    provider = Mock(spec=LLMProvider)
    processor = get_eng_ocr_fuser(
        test_cases=test_case_loader(),
        provider=provider,
    )
    output = get_eng_ocr_fused(lens, tesseract, processor=processor)

    assert len(lens) == len(output)
    assert_series_equal(output, request.getfixturevalue(expected_fixture))
    provider.chat_completion.assert_not_called()
