#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MNT."""

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
from scinoephile.image.zhongwen.fusion import ZhongwenFusionTestCase2
from scinoephile.testing import test_data_root

# ruff: noqa: F401 F403
from test.data.mnt.core.english.proofreading import (
    test_cases as mnt_english_proofreading_test_cases,
)
from test.data.mnt.core.zhongwen.proofreading import (
    test_cases as mnt_zhongwen_proofreading_test_cases,
)
from test.data.mnt.image.english.fusion import (
    test_cases as mnt_english_fusion_test_cases,
)
from test.data.mnt.image.zhongwen.fusion import (
    test_cases as mnt_zhongwen_fusion_test_cases,
)

__all__ = [
    "mnt_zho_hans_lens",
    "mnt_zho_hans_paddle",
    "mnt_zho_hans_fuse",
    "mnt_zho_hans_fuse_proofread",
    "mnt_zho_hans_fuse_proofread_clean",
    "mnt_zho_hans_fuse_proofread_clean_flatten",
    "mnt_zho_hant",
    "mnt_zho_hant_clean",
    "mnt_zho_hant_clean_flatten",
    "mnt_zho_hant_clean_flatten_simplify",
    "mnt_eng_lens",
    "mnt_eng_tesseract",
    "mnt_eng_fuse",
    "mnt_zho_hans_eng",
    "mnt_english_fusion_test_cases",
    "mnt_english_proofreading_test_cases",
    "mnt_zhongwen_fusion_test_cases",
    "mnt_zhongwen_proofreading_test_cases",
    "get_mnt_eng_proofreading_test_cases",
    "get_mnt_zho_proofreading_test_cases",
    "get_mnt_eng_fusion_test_cases",
    "get_mnt_zho_fusion_test_cases",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


# 简体中文 (OCR)
@pytest.fixture
def mnt_zho_hans_lens() -> Series:
    """MNT 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hans_lens.srt")


@pytest.fixture
def mnt_zho_hans_paddle() -> Series:
    """MNT 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hans_paddle.srt")


@pytest.fixture
def mnt_zho_hans_fuse() -> Series:
    """MNT 简体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse.srt")


@pytest.fixture
def mnt_zho_hans_fuse_proofread() -> Series:
    """MNT 简体中文 fused and proofread subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_proofread.srt")


@pytest.fixture
def mnt_zho_hans_fuse_proofread_clean() -> Series:
    """MNT 简体中文 fused, proofread, and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_proofread_clean.srt")


@pytest.fixture
def mnt_zho_hans_fuse_proofread_clean_flatten() -> Series:
    """MNT 简体中文 fused, proofread, cleaned, and flattened subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_proofread_clean_flatten.srt")


# 繁体中文 (SRT)
@pytest.fixture
def mnt_zho_hant() -> Series:
    """MNT 繁体中文 series."""
    return Series.load(input_dir / "zho-Hant.srt")


@pytest.fixture
def mnt_zho_hant_clean() -> Series:
    """MNT 繁体中文 cleaned series."""
    return Series.load(output_dir / "zho-Hant_clean.srt")


@pytest.fixture
def mnt_zho_hant_clean_flatten() -> Series:
    """MNT 繁体中文 cleaned and flattened series."""
    return Series.load(output_dir / "zho-Hant_clean_flatten.srt")


@pytest.fixture
def mnt_zho_hant_clean_flatten_simplify() -> Series:
    """MNT 繁体中文 cleaned, flattened, and simplified series."""
    return Series.load(output_dir / "zho-Hant_clean_flatten_simplify.srt")


# English (OCR)
@pytest.fixture
def mnt_eng_lens() -> Series:
    """MNT English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_lens.srt")


@pytest.fixture
def mnt_eng_tesseract() -> Series:
    """MNT English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_tesseract.srt")


@pytest.fixture
def mnt_eng_fuse() -> Series:
    """MNT English fused subtitles."""
    return Series.load(output_dir / "eng_fuse.srt")


@pytest.fixture
def mnt_eng_fuse_proofread() -> Series:
    """MNT English fused and proofread subtitles."""
    return Series.load(output_dir / "eng_fuse_proofread.srt")


@pytest.fixture
def mnt_eng_fuse_proofread_clean() -> Series:
    """MNT English fused, proofread, and cleaned subtitles."""
    return Series.load(output_dir / "eng_fuse_proofread_clean.srt")


@pytest.fixture
def mnt_eng_fuse_proofread_clean_flatten() -> Series:
    """MNT English fused, proofread, cleaned, and flattened subtitles."""
    return Series.load(output_dir / "eng_fuse_proofread_clean_flatten.srt")


# Bilingual 简体中文 and English
@pytest.fixture
def mnt_zho_hans_eng() -> Series:
    """MNT Bilingual 简体中文 and English series."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


@cache
def get_mnt_eng_proofreading_test_cases(
    **kwargs: Any,
) -> list[EnglishProofreadingTestCase2]:
    """Get MNT English proofreading test cases.

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
def get_mnt_zho_proofreading_test_cases(
    **kwargs: Any,
) -> list[ZhongwenProofreadingTestCase2]:
    """Get MNT Zhongwen proofreading test cases.

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
def get_mnt_eng_fusion_test_cases(
    **kwargs: Any,
) -> list[EnglishFusionTestCase2]:
    """Get MNT English fusion test cases.

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


@cache
def get_mnt_zho_fusion_test_cases(
    **kwargs: Any,
) -> list[ZhongwenFusionTestCase2]:
    """Get MNT Zhongwen fusion test cases.

    Arguments:
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    test_cases = load_test_cases_from_json(
        title_root / "image" / "zhongwen" / "fusion.json",
        ZhongwenFusionTestCase2,
        **kwargs,
    )
    return cast(list[ZhongwenFusionTestCase2], test_cases)
