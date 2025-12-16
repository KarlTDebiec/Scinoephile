#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

import pytest

from scinoephile.audio.cantonese.merging import MergingTestCase
from scinoephile.audio.cantonese.proofing import ProofingTestCase
from scinoephile.audio.cantonese.shifting import ShiftingTestCase
from scinoephile.audio.cantonese.translation import (
    TranslationPrompt,
    TranslationTestCase,
)
from scinoephile.core import Series
from scinoephile.core.fusion import FusionPrompt, FusionTestCase
from scinoephile.core.llms import load_test_cases_from_json
from scinoephile.core.proofreading import ProofreadingPrompt, ProofreadingTestCase
from scinoephile.core.review import ReviewPrompt, ReviewTestCase
from scinoephile.lang.eng.ocr_fusion import EngOcrFusionPrompt
from scinoephile.lang.eng.proofreading import EngProofreadingPrompt
from scinoephile.lang.zho.ocr_fusion import ZhoHansOcrFusionPrompt
from scinoephile.lang.zho.proofreading import ZhoHansProofreadingPrompt
from scinoephile.testing import test_data_root

__all__ = [
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
    "get_mlamd_yue_shifting_test_cases",
    "get_mlamd_yue_merging_test_cases",
    "get_mlamd_yue_proofing_test_cases",
    "get_mlamd_yue_translation_test_cases",
    "get_mlamd_yue_review_test_cases",
    "get_mlamd_eng_proofreading_test_cases",
    "get_mlamd_zho_proofreading_test_cases",
    "get_mlamd_eng_ocr_fusion_test_cases",
    "get_mlamd_zho_ocr_fusion_test_cases",
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
def get_mlamd_yue_shifting_test_cases(**kwargs: Any) -> list[ShiftingTestCase]:
    """Get MLAMD 粵文 shifting test cases.

    Arguments:
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "audio" / "cantonese" / "shifting.json"
    return load_test_cases_from_json(path, ShiftingTestCase, **kwargs)


@cache
def get_mlamd_yue_merging_test_cases(**kwargs: Any) -> list[MergingTestCase]:
    """Get MLAMD 粵文 merging test cases.

    Arguments:
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "audio" / "cantonese" / "merging.json"
    return load_test_cases_from_json(path, MergingTestCase, **kwargs)


@cache
def get_mlamd_yue_proofing_test_cases(**kwargs: Any) -> list[ProofingTestCase]:
    """Get MLAMD 粵文 proofing test cases.

    Arguments:
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "audio" / "cantonese" / "proofing.json"
    return load_test_cases_from_json(path, ProofingTestCase, **kwargs)


@cache
def get_mlamd_yue_translation_test_cases(
    prompt_cls: type[ProofreadingPrompt] = TranslationPrompt,
    **kwargs: Any,
) -> list[TranslationTestCase]:
    """Get MLAMD 粵文 translation test cases.

    Arguments:
        prompt_cls: prompt class to use
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "audio" / "cantonese" / "translation.json"
    return load_test_cases_from_json(
        path, TranslationTestCase, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_review_test_cases(
    prompt_cls: type[ProofreadingPrompt] = ReviewPrompt,
    **kwargs: Any,
) -> list[ReviewTestCase]:
    """Get MLAMD 粵文 review test cases.

    Arguments:
        prompt_cls: prompt class to use
        kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "audio" / "cantonese" / "review.json"
    return load_test_cases_from_json(
        path, ReviewTestCase, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_eng_proofreading_test_cases(
    prompt_cls: type[ProofreadingPrompt] = EngProofreadingPrompt,
    **kwargs: Any,
) -> list[ProofreadingTestCase]:
    """Get MLAMD English proofreading test cases.

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
def get_mlamd_zho_proofreading_test_cases(
    prompt_cls: type[ProofreadingPrompt] = ZhoHansProofreadingPrompt,
    **kwargs: Any,
) -> list[ProofreadingTestCase]:
    """Get MLAMD 中文 proofreading test cases.

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
def get_mlamd_eng_ocr_fusion_test_cases(
    prompt_cls: type[FusionPrompt] = EngOcrFusionPrompt, **kwargs: Any
) -> list[FusionTestCase]:
    """Get MLAMD English fusion test cases.

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
def get_mlamd_zho_ocr_fusion_test_cases(
    prompt_cls: type[FusionPrompt] = ZhoHansOcrFusionPrompt, **kwargs: Any
) -> list[FusionTestCase]:
    """Get MLAMD 中文 fusion test cases.

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
