#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any, cast

import pytest

from scinoephile.core import Series
from scinoephile.core.english.proofreading import EnglishProofreadingTestCase2
from scinoephile.core.llms import load_test_cases_from_json
from scinoephile.core.zhongwen.proofreading import ZhongwenProofreadingTestCase2
from scinoephile.image.english.fusion import EnglishFusionTestCase2
from scinoephile.testing import test_data_root

# ruff: noqa: F401 F403
from test.data.mlamd.core.english.proofreading import (
    test_cases as mlamd_english_proofreading_test_cases,
)
from test.data.mlamd.core.zhongwen.proofreading import (
    test_cases as mlamd_zhongwen_proofreading_test_cases,
)
from test.data.mlamd.image.english.fusion import (
    test_cases as mlamd_english_fusion_test_cases,
)
from test.data.mlamd.image.zhongwen.fusion import (
    test_cases as mlamd_zhongwen_fusion_test_cases,
)
from test.data.mlamd.merging import mlamd_merge_test_cases
from test.data.mlamd.proofing import mlamd_proof_test_cases
from test.data.mlamd.review import mlamd_review_test_cases
from test.data.mlamd.shifting import mlamd_shift_test_cases
from test.data.mlamd.translation import mlamd_translate_test_cases

___all__ = [
    "mlamd_zho_hans_lens",
    "mlamd_zho_hans_paddle",
    "mlamd_zho_hans_fuse",
    "mlamd_zho_hans_fuse_proofread",
    "mlamd_zho_hans_fuse_proofread_clean",
    "mlamd_zho_hans_fuse_proofread_clean_flatten",
    "mlamd_zho_hant_lens",
    "mlamd_zho_hant_paddle",
    "mlamd_eng_lens",
    "mlamd_eng_tesseract",
    "mlamd_eng_fuse",
    "mlamd_eng_fuse_proofread",
    "mlamd_eng_fuse_proofread_clean",
    "mlamd_eng_fuse_proofread_clean_flatten",
    "mlamd_yue_hans",
    "mlamd_zho_hans_eng",
    "mlamd_yue_hans_eng",
    "mlamd_shift_test_cases",
    "mlamd_merge_test_cases",
    "mlamd_proof_test_cases",
    "mlamd_translate_test_cases",
    "mlamd_review_test_cases",
    "mlamd_english_fusion_test_cases",
    "mlamd_english_proofreading_test_cases",
    "mlamd_zhongwen_fusion_test_cases",
    "mlamd_zhongwen_proofreading_test_cases",
    "get_mlamd_eng_proofreading_test_cases",
    "get_mlamd_zho_proofreading_test_cases",
    "get_mlamd_eng_fusion_test_cases",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


# 简体中文 (OCR)
@pytest.fixture
def mlamd_zho_hans_lens() -> Series:
    """MLAMD 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hans_lens.srt")


@pytest.fixture
def mlamd_zho_hans_paddle() -> Series:
    """MLAMD 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hans_paddle.srt")


@pytest.fixture
def mlamd_zho_hans_fuse() -> Series:
    """MLAMD 简体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_proofread() -> Series:
    """MLAMD 简体中文 fused and proofread subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_proofread.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_proofread_clean() -> Series:
    """MLAMD 简体中文 fused, proofread, and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_proofread_clean.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_proofread_clean_flatten() -> Series:
    """MLAMD 简体中文 fused, proofread, cleaned, and flattened subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_proofread_clean_flatten.srt")


# 繁體中文 (OCR)
@pytest.fixture
def mlamd_zho_hant_lens() -> Series:
    """MLAMD 繁體中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_lens.srt")


@pytest.fixture
def mlamd_zho_hant_paddle() -> Series:
    """MLAMD 繁體中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_paddle.srt")


# English (OCR)
@pytest.fixture
def mlamd_eng_lens() -> Series:
    """MLAMD English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_lens.srt")


@pytest.fixture
def mlamd_eng_tesseract() -> Series:
    """MLAMD English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_tesseract.srt")


@pytest.fixture
def mlamd_eng_fuse() -> Series:
    """MLAMD English fused subtitles."""
    return Series.load(output_dir / "eng_fuse.srt")


@pytest.fixture
def mlamd_eng_fuse_proofread() -> Series:
    """MLAMD English fused and proofread subtitles."""
    return Series.load(output_dir / "eng_fuse_proofread.srt")


@pytest.fixture
def mlamd_eng_fuse_proofread_clean() -> Series:
    """MLAMD English fused, proofread, and cleaned subtitles."""
    return Series.load(output_dir / "eng_fuse_proofread_clean.srt")


@pytest.fixture
def mlamd_eng_fuse_proofread_clean_flatten() -> Series:
    """MLAMD English fused, proofread, cleaned, and flattened subtitles."""
    return Series.load(output_dir / "eng_fuse_proofread_clean_flatten.srt")


# 简体粤文 (Transcription)
@pytest.fixture
def mlamd_yue_hans() -> Series:
    """MLAMD 简体粤文 subtitles transcribed."""
    return Series.load(output_dir / "yue-Hans.srt")


# Bilingual 简体粤文 and English
@pytest.fixture()
def mlamd_zho_hans_eng() -> Series:
    """MLAMD Bilingual 简体中文 and English subtitles."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


# Bilingual 简体粤文 and English
@pytest.fixture()
def mlamd_yue_hans_eng() -> Series:
    """MLAMD Bilingual 简体粤文 and English subtitles."""
    return Series.load(output_dir / "yue-Hans_eng.srt")


@cache
def get_mlamd_eng_proofreading_test_cases(
    **kwargs: Any,
) -> list[EnglishProofreadingTestCase2]:
    """Get MLAMD English proofreading test cases.

    Arguments:
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        English proofreading test cases
    """
    test_cases = load_test_cases_from_json(
        title_root / "core" / "english" / "proofreading.json",
        EnglishProofreadingTestCase2,
        **kwargs,
    )
    return cast(list[EnglishProofreadingTestCase2], test_cases)


@cache
def get_mlamd_zho_proofreading_test_cases(
    **kwargs: Any,
) -> list[ZhongwenProofreadingTestCase2]:
    """Get MLAMD Zhongwen proofreading test cases.

    Arguments:
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        Zhongwen proofreading test cases
    """
    test_cases = load_test_cases_from_json(
        title_root / "core" / "zhongwen" / "proofreading.json",
        ZhongwenProofreadingTestCase2,
        **kwargs,
    )
    return cast(list[ZhongwenProofreadingTestCase2], test_cases)


@cache
def get_mlamd_eng_fusion_test_cases(
    **kwargs: Any,
) -> list[EnglishFusionTestCase2]:
    """Get MLAMD English proofreading test cases.

    Arguments:
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    test_cases = load_test_cases_from_json(
        title_root / "image" / "english" / "fusion.json",
        EnglishFusionTestCase2,
        **kwargs,
    )
    return cast(list[EnglishFusionTestCase2], test_cases)
