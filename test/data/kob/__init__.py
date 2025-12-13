#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for KOB."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

import pytest

from scinoephile.core import Series
from scinoephile.core.english.proofreading import EnglishProofreadingPrompt
from scinoephile.core.llms import load_test_cases_from_json
from scinoephile.core.proofreading import ProofreadingTestCase
from scinoephile.core.zhongwen.proofreading import ZhongwenProofreadingPrompt
from scinoephile.image.english.fusion import EnglishFusionTestCase
from scinoephile.image.zhongwen.fusion import ZhongwenFusionTestCase
from scinoephile.testing import test_data_root

__all__ = [
    "kob_zho_hant_lens",
    "kob_zho_hant_paddle",
    "kob_zho_hant_fuse",
    "kob_zho_hant_fuse_proofread",
    "kob_eng_lens",
    "kob_eng_tesseract",
    "kob_eng_fuse",
    "kob_eng_fuse_proofread",
    "kob_yue_hans",
    "kob_yue_hans_clean",
    "kob_yue_hans_clean_flatten",
    "kob_yue_hant",
    "kob_yue_hant_simplify",
    "kob_eng",
    "kob_eng_clean",
    "kob_eng_clean_flatten",
    "kob_yue_hans_eng",
    "get_kob_eng_proofreading_test_cases",
    "get_kob_zho_proofreading_test_cases",
    "get_kob_eng_fusion_test_cases",
    "get_kob_zho_fusion_test_cases",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


# 繁體中文 (OCR)
@pytest.fixture
def kob_zho_hant_lens() -> Series:
    """KOB 繁體中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_lens.srt")


@pytest.fixture
def kob_zho_hant_paddle() -> Series:
    """KOB 繁體中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_paddle.srt")


@pytest.fixture
def kob_zho_hant_fuse() -> Series:
    """KOB 繁體中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse.srt")


@pytest.fixture
def kob_zho_hant_fuse_proofread() -> Series:
    """KOB 简体粤文 fused and proofread subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_proofread.srt")


# English (OCR)
@pytest.fixture
def kob_eng_lens() -> Series:
    """KOB English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_lens.srt")


@pytest.fixture
def kob_eng_tesseract() -> Series:
    """KOB English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_tesseract.srt")


@pytest.fixture
def kob_eng_fuse() -> Series:
    """KOB English fused subtitles."""
    return Series.load(output_dir / "eng_fuse.srt")


@pytest.fixture
def kob_eng_fuse_proofread() -> Series:
    """KOB English fused and proofread subtitles."""
    return Series.load(output_dir / "eng_fuse_proofread.srt")


# 简体粤文 (SRT)
@pytest.fixture
def kob_yue_hans() -> Series:
    """KOB 简体粤文 subtitles."""
    return Series.load(input_dir / "yue-Hans.srt")


@pytest.fixture
def kob_yue_hans_clean() -> Series:
    """KOB 简体粤文 cleaned subtitles."""
    return Series.load(output_dir / "yue-Hans_clean.srt")


@pytest.fixture
def kob_yue_hans_clean_flatten() -> Series:
    """KOB 简体粤文 cleaned and flattened subtitles."""
    return Series.load(output_dir / "yue-Hans_clean_flatten.srt")


# 繁体粤文 (SRT)
@pytest.fixture
def kob_yue_hant() -> Series:
    """KOB 繁体粤文 subtitles."""
    return Series.load(input_dir / "yue-Hant.srt")


@pytest.fixture
def kob_yue_hant_simplify() -> Series:
    """KOB 繁体粤文 simplified subtitles."""
    return Series.load(output_dir / "yue-Hant_simplify.srt")


# English (SRT)
@pytest.fixture
def kob_eng() -> Series:
    """KOB English subtitles."""
    return Series.load(input_dir / "eng.srt")


@pytest.fixture
def kob_eng_clean() -> Series:
    """KOB English cleaned subtitles."""
    return Series.load(output_dir / "eng_clean.srt")


@pytest.fixture
def kob_eng_clean_flatten() -> Series:
    """KOB English cleaned and flattened subtitles."""
    return Series.load(output_dir / "eng_clean_flatten.srt")


# Bilingual 简体粤文 and English
@pytest.fixture()
def kob_yue_hans_eng() -> Series:
    """KOB Bilingual 简体粤文 and English subtitles."""
    return Series.load(output_dir / "yue-Hans_eng.srt")


@cache
def get_kob_eng_proofreading_test_cases(
    prompt_cls: type[EnglishProofreadingPrompt] = EnglishProofreadingPrompt,
    **kwargs: Any,
) -> list[ProofreadingTestCase]:
    """Get KOB English proofreading test cases.

    Arguments:
        prompt_cls: prompt class to use
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "core" / "english" / "proofreading.json"
    return load_test_cases_from_json(
        path, ProofreadingTestCase, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_kob_zho_proofreading_test_cases(
    prompt_cls: type[ZhongwenProofreadingPrompt] = ZhongwenProofreadingPrompt,
    **kwargs: Any,
) -> list[ProofreadingTestCase]:
    """Get KOB Zhongwen proofreading test cases.

    Arguments:
        prompt_cls: prompt class to use
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "core" / "zhongwen" / "proofreading.json"
    return load_test_cases_from_json(
        path, ProofreadingTestCase, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_kob_eng_fusion_test_cases(
    **kwargs: Any,
) -> list[EnglishFusionTestCase]:
    """Get KOB English fusion test cases.

    Arguments:
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "image" / "english" / "fusion.json"
    return load_test_cases_from_json(path, EnglishFusionTestCase, **kwargs)


@cache
def get_kob_zho_fusion_test_cases(
    **kwargs: Any,
) -> list[ZhongwenFusionTestCase]:
    """Get KOB Zhongwen fusion test cases.

    Arguments:
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "image" / "zhongwen" / "fusion.json"
    return load_test_cases_from_json(path, ZhongwenFusionTestCase, **kwargs)
