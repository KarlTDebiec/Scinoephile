#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""

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
    "t_zho_hans_lens",
    "t_zho_hans_paddle",
    "t_zho_hans_fuse",
    "t_zho_hans_fuse_proofread",
    "t_zho_hans",
    "t_zho_hans_clean",
    "t_zho_hans_clean_flatten",
    "t_zho_hant",
    "t_zho_hant_simplify",
    "t_eng",
    "t_eng_lens",
    "t_eng_tesseract",
    "t_eng_fuse",
    "t_eng_fuse_proofread",
    "t_eng_clean",
    "t_eng_clean_flatten",
    "t_zho_hans_eng",
    "get_t_eng_proofreading_test_cases",
    "get_t_zho_proofreading_test_cases",
    "get_t_eng_fusion_test_cases",
    "get_t_zho_fusion_test_cases",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


# 简体中文 (OCR)
@pytest.fixture
def t_zho_hans_lens() -> Series:
    """T 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hans_lens.srt")


@pytest.fixture
def t_zho_hans_paddle() -> Series:
    """T 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hans_paddle.srt")


@pytest.fixture
def t_zho_hans_fuse() -> Series:
    """T 简体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse.srt")


@pytest.fixture
def t_zho_hans_fuse_proofread() -> Series:
    """T 简体中文 fused and proofread subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_proofread.srt")


# 繁體中文 (OCR)
@pytest.fixture
def t_zho_hant_lens() -> Series:
    """T 繁體中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_lens.srt")


@pytest.fixture
def t_zho_hant_paddle() -> Series:
    """T 繁體中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_paddle.srt")


# English (OCR)
@pytest.fixture
def t_eng_lens() -> Series:
    """T English subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "eng_lens.srt")


@pytest.fixture
def t_eng_tesseract() -> Series:
    """T English subtitles OCRed using Tesseract."""
    return Series.load(input_dir / "eng_tesseract.srt")


@pytest.fixture
def t_eng_fuse() -> Series:
    """T English fused subtitles."""
    return Series.load(output_dir / "eng_fuse.srt")


@pytest.fixture
def t_eng_fuse_proofread() -> Series:
    """T English fused and proofread subtitles."""
    return Series.load(output_dir / "eng_fuse_proofread.srt")


# 简体中文 (SRT)
@pytest.fixture
def t_zho_hans() -> Series:
    """T 简体中文 series."""
    return Series.load(input_dir / "zho-Hans.srt")


@pytest.fixture
def t_zho_hans_clean() -> Series:
    """T 简体中文 cleaned series."""
    return Series.load(output_dir / "zho-Hans_clean.srt")


@pytest.fixture
def t_zho_hans_clean_flatten() -> Series:
    """T 简体中文 cleaned and flattened series."""
    return Series.load(output_dir / "zho-Hans_clean_flatten.srt")


# 繁体中文
@pytest.fixture
def t_zho_hant() -> Series:
    """T 繁体中文 series."""
    return Series.load(input_dir / "zho-Hant.srt")


@pytest.fixture
def t_zho_hant_simplify() -> Series:
    """T 繁体中文 simplified series."""
    return Series.load(output_dir / "zho-Hant_simplify.srt")


# English (SRT)
@pytest.fixture
def t_eng() -> Series:
    """T English series."""
    return Series.load(input_dir / "eng.srt")


@pytest.fixture
def t_eng_clean() -> Series:
    """T English cleaned series."""
    return Series.load(output_dir / "eng_clean.srt")


@pytest.fixture
def t_eng_clean_flatten() -> Series:
    """T English cleaned and flattened series."""
    return Series.load(output_dir / "eng_clean_flatten.srt")


# Bilingual 简体中文 and English
@pytest.fixture
def t_zho_hans_eng() -> Series:
    """T Bilingual 简体粤文 and English series."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


@cache
def get_t_eng_proofreading_test_cases(
    **kwargs: Any,
) -> list[ProofreadingTestCase]:
    """Get T English proofreading test cases.

    Arguments:
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        English proofreading test cases
    """
    path = title_root / "core" / "english" / "proofreading.json"
    return load_test_cases_from_json(
        path, ProofreadingTestCase, prompt_cls=EnglishProofreadingPrompt, **kwargs
    )


@cache
def get_t_zho_proofreading_test_cases(
    **kwargs: Any,
) -> list[ProofreadingTestCase]:
    """Get T Zhongwen proofreading test cases.

    Arguments:
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        Zhongwen proofreading test cases
    """
    path = title_root / "core" / "zhongwen" / "proofreading.json"
    return load_test_cases_from_json(
        path, ProofreadingTestCase, prompt_cls=ZhongwenProofreadingPrompt, **kwargs
    )


@cache
def get_t_eng_fusion_test_cases(
    **kwargs: Any,
) -> list[EnglishFusionTestCase]:
    """Get T English fusion test cases.

    Arguments:
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "image" / "english" / "fusion.json"
    return load_test_cases_from_json(path, EnglishFusionTestCase, **kwargs)


@cache
def get_t_zho_fusion_test_cases(
    **kwargs: Any,
) -> list[ZhongwenFusionTestCase]:
    """Get T Zhongwen fusion test cases.

    Arguments:
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "image" / "zhongwen" / "fusion.json"
    return load_test_cases_from_json(path, ZhongwenFusionTestCase, **kwargs)
