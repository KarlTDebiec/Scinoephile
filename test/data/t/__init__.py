#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for T."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

import pytest

from scinoephile.core import Series
from scinoephile.core.fusion import FusionPrompt, FusionTestCase
from scinoephile.core.llms import load_test_cases_from_json
from scinoephile.core.proofreading import ProofreadingPrompt, ProofreadingTestCase
from scinoephile.lang.eng.ocr_fusion import EngOcrFusionPrompt
from scinoephile.lang.eng.proofreading import EngProofreadingPrompt
from scinoephile.lang.zho.ocr_fusion import ZhoHansOcrFusionPrompt
from scinoephile.lang.zho.proofreading import ZhoHansProofreadingPrompt
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
    "get_t_eng_ocr_fusion_test_cases",
    "get_t_zho_ocr_fusion_test_cases",
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
    prompt_cls: type[ProofreadingPrompt] = EngProofreadingPrompt,
    **kwargs: Any,
) -> list[ProofreadingTestCase]:
    """Get T English proofreading test cases.

    Arguments:
        prompt_cls: prompt class to use
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        English proofreading test cases
    """
    path = title_root / "eng" / "proofreading.json"
    return load_test_cases_from_json(
        path, ProofreadingTestCase, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_t_zho_proofreading_test_cases(
    prompt_cls: type[ProofreadingPrompt] = ZhoHansProofreadingPrompt,
    **kwargs: Any,
) -> list[ProofreadingTestCase]:
    """Get T 中文 proofreading test cases.

    Arguments:
        prompt_cls: prompt class to use
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "zho" / "proofreading.json"
    return load_test_cases_from_json(
        path, ProofreadingTestCase, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_t_eng_ocr_fusion_test_cases(
    prompt_cls: type[FusionPrompt] = EngOcrFusionPrompt, **kwargs: Any
) -> list[FusionTestCase]:
    """Get T English fusion test cases.

    Arguments:
        prompt_cls: prompt class to use for test cases
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "eng" / "ocr_fusion.json"
    return load_test_cases_from_json(
        path, FusionTestCase, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_t_zho_ocr_fusion_test_cases(
    prompt_cls: type[FusionPrompt] = ZhoHansOcrFusionPrompt, **kwargs: Any
) -> list[FusionTestCase]:
    """Get T 中文 fusion test cases.

    Arguments:
        prompt_cls: prompt class to use for test cases
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "zho" / "ocr_fusion.json"
    return load_test_cases_from_json(
        path, FusionTestCase, prompt_cls=prompt_cls, **kwargs
    )
