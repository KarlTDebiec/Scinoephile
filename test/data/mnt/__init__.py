#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MNT."""

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
    "mnt_eng_fuse_proofread",
    "mnt_eng_fuse_proofread_clean",
    "mnt_eng_fuse_proofread_clean_flatten",
    "mnt_zho_hans_eng",
    "get_mnt_eng_proofreading_test_cases",
    "get_mnt_zho_proofreading_test_cases",
    "get_mnt_eng_ocr_fusion_test_cases",
    "get_mnt_zho_ocr_fusion_test_cases",
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
    prompt_cls: type[ProofreadingPrompt] = EngProofreadingPrompt,
    **kwargs: Any,
) -> list[ProofreadingTestCase]:
    """Get MNT English proofreading test cases.

    Arguments:
        prompt_cls: prompt class to use
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "core" / "eng" / "proofreading.json"
    return load_test_cases_from_json(
        path, ProofreadingTestCase, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mnt_zho_proofreading_test_cases(
    prompt_cls: type[ProofreadingPrompt] = ZhoHansProofreadingPrompt,
    **kwargs: Any,
) -> list[ProofreadingTestCase]:
    """Get MNT 中文 proofreading test cases.

    Arguments:
        prompt_cls: prompt class to use
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "core" / "zho" / "proofreading.json"
    return load_test_cases_from_json(
        path, ProofreadingTestCase, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mnt_eng_ocr_fusion_test_cases(
    prompt_cls: type[FusionPrompt] = EngOcrFusionPrompt, **kwargs: Any
) -> list[FusionTestCase]:
    """Get MNT English fusion test cases.

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
def get_mnt_zho_ocr_fusion_test_cases(
    prompt_cls: type[FusionPrompt] = ZhoHansOcrFusionPrompt, **kwargs: Any
) -> list[FusionTestCase]:
    """Get MNT 中文 fusion test cases.

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
