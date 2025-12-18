#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for KOB."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

import pytest

from scinoephile.core import Series
from scinoephile.core.blockwise import BlockwisePrompt, BlockwiseTestCase
from scinoephile.core.llms import load_test_cases_from_json
from scinoephile.core.pairwise import PairwisePrompt, PairwiseTestCase
from scinoephile.lang.eng.ocr_fusion import EngOcrFusionPrompt
from scinoephile.lang.eng.proofreading import EngProofreadingPrompt
from scinoephile.lang.zho.ocr_fusion import ZhoHantOcrFusionPrompt
from scinoephile.lang.zho.proofreading import ZhoHantProofreadingPrompt
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
    "get_kob_eng_ocr_fusion_test_cases",
    "get_kob_zho_ocr_fusion_test_cases",
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
    prompt_cls: type[BlockwisePrompt] = EngProofreadingPrompt,
    **kwargs: Any,
) -> list[BlockwiseTestCase]:
    """Get KOB English proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "eng" / "proofreading.json"
    return load_test_cases_from_json(
        path, BlockwiseTestCase, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_kob_zho_proofreading_test_cases(
    prompt_cls: type[BlockwisePrompt] = ZhoHantProofreadingPrompt,
    **kwargs: Any,
) -> list[BlockwiseTestCase]:
    """Get KOB 中文 proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "zho" / "proofreading.json"
    return load_test_cases_from_json(
        path, BlockwiseTestCase, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_kob_eng_ocr_fusion_test_cases(
    prompt_cls: type[PairwisePrompt] = EngOcrFusionPrompt,
    **kwargs: Any,
) -> list[PairwiseTestCase]:
    """Get KOB English OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "eng" / "ocr_fusion.json"
    return load_test_cases_from_json(
        path, PairwiseTestCase, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_kob_zho_ocr_fusion_test_cases(
    prompt_cls: type[PairwisePrompt] = ZhoHantOcrFusionPrompt,
    **kwargs: Any,
) -> list[PairwiseTestCase]:
    """Get KOB 中文 OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "zho" / "ocr_fusion.json"
    return load_test_cases_from_json(
        path, PairwiseTestCase, prompt_cls=prompt_cls, **kwargs
    )
