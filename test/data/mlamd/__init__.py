#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for MLAMD."""

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

import pytest

from scinoephile.core.subtitles import Series
from scinoephile.core.testing import test_data_root
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng.ocr_fusion import EngOcrFusionPrompt
from scinoephile.lang.eng.proofreading import EngProofreadingPrompt
from scinoephile.lang.zho.ocr_fusion import ZhoHansOcrFusionPrompt
from scinoephile.lang.zho.proofreading import ZhoHansProofreadingPrompt
from scinoephile.llms.base import TestCase, load_test_cases_from_json
from scinoephile.llms.dual_block import DualBlockManager, DualBlockPrompt
from scinoephile.llms.dual_block_gapped import (
    DualBlockGappedManager,
    DualBlockGappedPrompt,
)
from scinoephile.llms.dual_multi_single import DualMultiSinglePrompt
from scinoephile.llms.dual_pair import DualPairManager, DualPairPrompt
from scinoephile.llms.dual_single import DualSinglePrompt
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionManager
from scinoephile.llms.mono_block import MonoBlockManager, MonoBlockPrompt
from scinoephile.multilang.yue_zho.proofreading import (
    YueZhoHansProofreadingPrompt,
    YueZhoProofreadingManager,
)
from scinoephile.multilang.yue_zho.review import YueHansReviewPrompt
from scinoephile.multilang.yue_zho.transcription.merging import (
    YueZhoHansMergingPrompt,
    YueZhoMergingManager,
)
from scinoephile.multilang.yue_zho.transcription.shifting import (
    YueZhoHansShiftingPrompt,
)
from scinoephile.multilang.yue_zho.translation import YueHansFromZhoTranslationPrompt

__all__ = [
    "mlamd_zho_hans_sup_path",
    "mlamd_zho_hans_image_path",
    "mlamd_zho_hans_image",
    "mlamd_zho_hans_lens",
    "mlamd_zho_hans_paddle",
    "mlamd_zho_hans_fuse",
    "mlamd_zho_hans_fuse_clean",
    "mlamd_zho_hans_fuse_clean_validate",
    "mlamd_zho_hans_fuse_clean_validate_proofread",
    "mlamd_zho_hans_fuse_clean_validate_proofread_flatten",
    "mlamd_zho_hant_sup_path",
    "mlamd_zho_hant_lens",
    "mlamd_zho_hant_paddle",
    "mlamd_zho_hant_fuse",
    "mlamd_zho_hant_fuse_clean",
    "mlamd_zho_hant_fuse_clean_validate",
    "mlamd_zho_hant_fuse_clean_validate_flatten",
    "mlamd_eng_sup_path",
    "mlamd_eng_image_path",
    "mlamd_eng_image",
    "mlamd_eng_lens",
    "mlamd_eng_tesseract",
    "mlamd_eng_fuse",
    "mlamd_eng_fuse_clean",
    "mlamd_eng_fuse_clean_validate",
    "mlamd_eng_fuse_clean_validate_flatten",
    "mlamd_yue_hans",
    "mlamd_yue_hans_proofread",
    "mlamd_yue_hans_proofread_translate",
    "mlamd_yue_hans_proofread_translate_review",
    "mlamd_zho_hans_eng",
    "mlamd_yue_hans_eng",
    "get_mlamd_yue_shifting_test_cases",
    "get_mlamd_yue_merging_test_cases",
    "get_mlamd_yue_vs_zho_proofreading_test_cases",
    "get_mlamd_yue_from_zho_translation_test_cases",
    "get_mlamd_yue_vs_zho_review_test_cases",
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
def mlamd_zho_hans_sup_path() -> Path:
    """Path to MLAMD 简体中文 SUP subtitles."""
    return input_dir / "zho-Hans.sup"


@pytest.fixture
def mlamd_zho_hans_image_path() -> Path:
    """Path to MLAMD 简体中文 image subtitles."""
    return output_dir / "zho-Hans_image"


@pytest.fixture
def mlamd_zho_hans_image() -> ImageSeries:
    """MLAMD 简体中文 image subtitles."""
    return ImageSeries.load(output_dir / "zho-Hans_image", encoding="utf-8")


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
def mlamd_zho_hans_fuse_clean() -> Series:
    """MLAMD 简体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_clean.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_clean_validate() -> Series:
    """MLAMD 简体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_clean_validate.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_clean_validate_proofread() -> Series:
    """MLAMD 简体中文 fused, cleaned, validated, and proofread subtitles."""
    return Series.load(output_dir / "zho-Hans_fuse_clean_validate_proofread.srt")


@pytest.fixture
def mlamd_zho_hans_fuse_clean_validate_proofread_flatten() -> Series:
    """MLAMD 简体中文 fused, cleaned, validated, proofread, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_fuse_clean_validate_proofread_flatten.srt"
    )


@pytest.fixture
def mlamd_zho_hant_sup_path() -> Path:
    """Path to MLAMD 繁體中文 SUP subtitles."""
    return input_dir / "zho-Hant.sup"


@pytest.fixture
def mlamd_zho_hant_lens() -> Series:
    """MLAMD 繁體中文 subtitles OCRed using Google Lens."""
    return Series.load(input_dir / "zho-Hant_lens.srt")


@pytest.fixture
def mlamd_zho_hant_paddle() -> Series:
    """MLAMD 繁體中文 subtitles OCRed using PaddleOCR."""
    return Series.load(input_dir / "zho-Hant_paddle.srt")


@pytest.fixture
def mlamd_zho_hant_fuse() -> Series:
    """MLAMD 繁體中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse.srt")


@pytest.fixture
def mlamd_zho_hant_fuse_clean() -> Series:
    """MLAMD 繁體中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean.srt")


@pytest.fixture
def mlamd_zho_hant_fuse_clean_validate() -> Series:
    """MLAMD 繁體中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean_validate.srt")


@pytest.fixture
def mlamd_zho_hant_fuse_clean_validate_flatten() -> Series:
    """MLAMD 繁體中文 fused, cleaned, validated, and flattened subtitles."""
    return Series.load(output_dir / "zho-Hant_fuse_clean_validate_flatten.srt")


# English (OCR)
@pytest.fixture
def mlamd_eng_sup_path() -> Path:
    """Path to MLAMD English SUP subtitles."""
    return input_dir / "eng.sup"


@pytest.fixture
def mlamd_eng_image_path() -> Path:
    """Path to MLAMD English image subtitles."""
    return output_dir / "eng_image"


@pytest.fixture
def mlamd_eng_image() -> ImageSeries:
    """MLAMD English image subtitles."""
    return ImageSeries.load(output_dir / "eng_image", encoding="utf-8")


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
def mlamd_eng_fuse_clean() -> Series:
    """MLAMD English fused and cleaned subtitles."""
    return Series.load(output_dir / "eng_fuse_clean.srt")


@pytest.fixture
def mlamd_eng_fuse_clean_validate() -> Series:
    """MLAMD English fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate.srt")


@pytest.fixture
def mlamd_eng_fuse_clean_validate_flatten() -> Series:
    """MLAMD English fused, cleaned, validated, and flattened subtitles."""
    return Series.load(output_dir / "eng_fuse_clean_validate_flatten.srt")


@pytest.fixture
def mlamd_yue_hans() -> Series:
    """MLAMD 简体粤文 transcribed subtitles."""
    return Series.load(output_dir / "yue-Hans.srt")


@pytest.fixture
def mlamd_yue_hans_proofread() -> Series:
    """MLAMD 简体粤文 transcribed and proofread subtitles."""
    return Series.load(output_dir / "yue-Hans_proofread.srt")


@pytest.fixture
def mlamd_yue_hans_proofread_translate() -> Series:
    """MLAMD 简体粤文 transcribed, proofread, and translated subtitles."""
    return Series.load(output_dir / "yue-Hans_proofread_translate.srt")


@pytest.fixture
def mlamd_yue_hans_proofread_translate_review() -> Series:
    """MLAMD 简体粤文 transcribed, proofread, translated, and reviewed subtitles."""
    return Series.load(output_dir / "yue-Hans_proofread_translate_review.srt")


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
def get_mlamd_yue_shifting_test_cases(
    prompt_cls: type[DualPairPrompt] = YueZhoHansShiftingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 粵文 shifting test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "multilang" / "yue_zho" / "transcription" / "shifting.json"
    return load_test_cases_from_json(
        path, DualPairManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_merging_test_cases(
    prompt_cls: type[DualMultiSinglePrompt] = YueZhoHansMergingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 粵文 merging test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "multilang" / "yue_zho" / "transcription" / "merging.json"
    return load_test_cases_from_json(
        path, YueZhoMergingManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_vs_zho_proofreading_test_cases(
    prompt_cls: type[DualSinglePrompt] = YueZhoHansProofreadingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 粵文 proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "multilang" / "yue_zho" / "proofreading.json"
    return load_test_cases_from_json(
        path, YueZhoProofreadingManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_from_zho_translation_test_cases(
    prompt_cls: type[DualBlockGappedPrompt] = YueHansFromZhoTranslationPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 粵文 translation test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "multilang" / "yue_zho" / "translation.json"
    return load_test_cases_from_json(
        path, DualBlockGappedManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_yue_vs_zho_review_test_cases(
    prompt_cls: type[DualBlockPrompt] = YueHansReviewPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 粵文 review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "multilang" / "yue_zho" / "review.json"
    return load_test_cases_from_json(
        path, DualBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_eng_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = EngProofreadingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD English proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "eng" / "proofreading.json"
    return load_test_cases_from_json(
        path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_zho_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = ZhoHansProofreadingPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 中文 proofreading test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "zho" / "proofreading.json"
    return load_test_cases_from_json(
        path, MonoBlockManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_eng_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = EngOcrFusionPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD English OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "eng" / "ocr_fusion.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_mlamd_zho_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHansOcrFusionPrompt,
    **kwargs: Any,
) -> list[TestCase]:
    """Get MLAMD 中文 OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = title_root / "lang" / "zho" / "ocr_fusion.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )
