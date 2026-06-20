#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for ACOPOPB."""

# ruff: noqa: E501

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

from pytest import fixture

from scinoephile.core.llms import TestCase
from scinoephile.core.llms.utils import load_test_cases_from_json
from scinoephile.core.subtitles import Series
from scinoephile.lang.eng.block_review import BlockReviewPromptEng
from scinoephile.lang.eng.ocr_fusion import OcrFusionPromptEng
from scinoephile.lang.zho.block_review import (
    BlockReviewPromptZhoHans,
    BlockReviewPromptZhoHant,
)
from scinoephile.lang.zho.ocr_fusion import (
    OcrFusionPromptZhoHans,
    OcrFusionPromptZhoHant,
)
from scinoephile.llms.dual_1_to_1 import Dual1To1Prompt
from scinoephile.llms.dual_1_to_1.ocr_fusion import OcrFusionManager
from scinoephile.llms.mono_n import MonoNManager, MonoNPrompt
from test.helpers import test_data_root

__all__ = [
    "get_acopopb_eng_block_review_test_cases",
    "get_acopopb_eng_ocr_fusion_test_cases",
    "get_acopopb_yue_hans_block_review_test_cases",
    "get_acopopb_yue_hans_ocr_fusion_test_cases",
    "get_acopopb_yue_hant_block_review_test_cases",
    "get_acopopb_yue_hant_ocr_fusion_test_cases",
    "get_acopopb_yue_hant_simplify_block_review_test_cases",
    "get_acopopb_zho_hans_block_review_test_cases",
    "get_acopopb_zho_hans_ocr_fusion_test_cases",
    "get_acopopb_zho_hant_block_review_test_cases",
    "get_acopopb_zho_hant_ocr_fusion_test_cases",
    "get_acopopb_zho_hant_simplify_block_review_test_cases",
    "acopopb_eng_ocr_fuse",
    "acopopb_eng_ocr_fuse_clean",
    "acopopb_eng_ocr_fuse_clean_validate",
    "acopopb_eng_ocr_fuse_clean_validate_review",
    "acopopb_eng_ocr_fuse_clean_validate_review_flatten",
    "acopopb_eng_ocr_lens",
    "acopopb_eng_ocr_lens_clean",
    "acopopb_eng_ocr_tesseract",
    "acopopb_eng_ocr_tesseract_clean",
    "acopopb_yue_hans_eng",
    "acopopb_yue_hans_ocr_fuse",
    "acopopb_yue_hans_ocr_fuse_clean",
    "acopopb_yue_hans_ocr_fuse_clean_validate",
    "acopopb_yue_hans_ocr_fuse_clean_validate_review",
    "acopopb_yue_hans_ocr_fuse_clean_validate_review_flatten",
    "acopopb_yue_hans_ocr_fuse_clean_validate_review_flatten_romanize",
    "acopopb_yue_hans_ocr_lens",
    "acopopb_yue_hans_ocr_lens_clean",
    "acopopb_yue_hans_ocr_paddle",
    "acopopb_yue_hans_ocr_paddle_clean",
    "acopopb_yue_hant_ocr_fuse",
    "acopopb_yue_hant_ocr_fuse_clean",
    "acopopb_yue_hant_ocr_fuse_clean_validate",
    "acopopb_yue_hant_ocr_fuse_clean_validate_review",
    "acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten",
    "acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify",
    "acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
    "acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
    "acopopb_yue_hant_ocr_lens",
    "acopopb_yue_hant_ocr_lens_clean",
    "acopopb_yue_hant_ocr_paddle",
    "acopopb_yue_hant_ocr_paddle_clean",
    "acopopb_zho_hans_eng",
    "acopopb_zho_hans_ocr_fuse",
    "acopopb_zho_hans_ocr_fuse_clean",
    "acopopb_zho_hans_ocr_fuse_clean_validate",
    "acopopb_zho_hans_ocr_fuse_clean_validate_review",
    "acopopb_zho_hans_ocr_fuse_clean_validate_review_flatten",
    "acopopb_zho_hans_ocr_fuse_clean_validate_review_flatten_romanize",
    "acopopb_zho_hans_ocr_lens",
    "acopopb_zho_hans_ocr_lens_clean",
    "acopopb_zho_hans_ocr_paddle",
    "acopopb_zho_hans_ocr_paddle_clean",
    "acopopb_zho_hant_ocr_fuse",
    "acopopb_zho_hant_ocr_fuse_clean",
    "acopopb_zho_hant_ocr_fuse_clean_validate",
    "acopopb_zho_hant_ocr_fuse_clean_validate_review",
    "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten",
    "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
    "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
    "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
    "acopopb_zho_hant_ocr_lens",
    "acopopb_zho_hant_ocr_lens_clean",
    "acopopb_zho_hant_ocr_paddle",
    "acopopb_zho_hant_ocr_paddle_clean",
    "acopopb_zho_simplify_expected_series_diff",
]

title_root = test_data_root / Path(__file__).parent.name
output_dir = title_root / "output"


@cache
def get_acopopb_eng_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptEng,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB English block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "eng_ocr/lang/eng/block_review.json"
    return load_test_cases_from_json(
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_acopopb_eng_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptEng,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB English OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "eng_ocr/lang/eng/ocr_fusion.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_acopopb_yue_hans_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB 简体粤文 block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hans_ocr/lang/yue/block_review.json"
    return load_test_cases_from_json(
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_acopopb_yue_hans_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB 简体粤文 OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hans_ocr/lang/yue/ocr_fusion.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_acopopb_yue_hant_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB 繁體粵文 block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hant_ocr/lang/yue/block_review.json"
    return load_test_cases_from_json(
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_acopopb_yue_hant_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB 繁體粵文 OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hant_ocr/lang/yue/ocr_fusion.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_acopopb_yue_hant_simplify_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB 繁體粵文 simplification block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hant_ocr/lang/yue/simplify_block_review.json"
    return load_test_cases_from_json(
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_acopopb_zho_hans_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB 简体中文 block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hans_ocr/lang/zho/block_review.json"
    return load_test_cases_from_json(
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_acopopb_zho_hans_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB 简体中文 OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hans_ocr/lang/zho/ocr_fusion.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_acopopb_zho_hant_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB 繁体中文 block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/block_review.json"
    return load_test_cases_from_json(
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_acopopb_zho_hant_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB 繁体中文 OCR fusion test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/ocr_fusion.json"
    return load_test_cases_from_json(
        path, OcrFusionManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_acopopb_zho_hant_simplify_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB 繁体中文 simplification block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/simplify_block_review.json"
    return load_test_cases_from_json(
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
    )


@fixture
def acopopb_eng_ocr_fuse() -> Series:
    """ACOPOPB English fused subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse.srt")


@fixture
def acopopb_eng_ocr_fuse_clean() -> Series:
    """ACOPOPB English fused and cleaned subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean.srt")


@fixture
def acopopb_eng_ocr_fuse_clean_validate() -> Series:
    """ACOPOPB English fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate.srt")


@fixture
def acopopb_eng_ocr_fuse_clean_validate_review() -> Series:
    """ACOPOPB English fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate_review.srt")


@fixture
def acopopb_eng_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPOPB English fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate_review_flatten.srt")


@fixture
def acopopb_eng_ocr_lens() -> Series:
    """ACOPOPB English subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "eng_ocr/lens.srt")


@fixture
def acopopb_eng_ocr_lens_clean() -> Series:
    """ACOPOPB English Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "eng_ocr/lens_clean.srt")


@fixture
def acopopb_eng_ocr_tesseract() -> Series:
    """ACOPOPB English subtitles OCRed using Tesseract."""
    return Series.load(output_dir / "eng_ocr/tesseract.srt")


@fixture
def acopopb_eng_ocr_tesseract_clean() -> Series:
    """ACOPOPB English Tesseract OCR subtitles, cleaned."""
    return Series.load(output_dir / "eng_ocr/tesseract_clean.srt")


@fixture
def acopopb_yue_hans_eng() -> Series:
    """ACOPOPB bilingual 简体粤文 and English subtitles."""
    return Series.load(output_dir / "yue-Hans_eng.srt")


@fixture
def acopopb_yue_hans_ocr_fuse() -> Series:
    """ACOPOPB 简体粤文 fused subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse.srt")


@fixture
def acopopb_yue_hans_ocr_fuse_clean() -> Series:
    """ACOPOPB 简体粤文 fused and cleaned subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean.srt")


@fixture
def acopopb_yue_hans_ocr_fuse_clean_validate() -> Series:
    """ACOPOPB 简体粤文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean_validate.srt")


@fixture
def acopopb_yue_hans_ocr_fuse_clean_validate_review() -> Series:
    """ACOPOPB 简体粤文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean_validate_review.srt")


@fixture
def acopopb_yue_hans_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPOPB 简体粤文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acopopb_yue_hans_ocr_fuse_clean_validate_review_flatten_romanize() -> Series:
    """ACOPOPB 简体粤文 fused/cleaned/validated/reviewed/flattened romanized subtitles."""
    return Series.load(
        output_dir / "yue-Hans_ocr/fuse_clean_validate_review_flatten_romanize.srt"
    )


@fixture
def acopopb_yue_hans_ocr_lens() -> Series:
    """ACOPOPB 简体粤文 subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "yue-Hans_ocr/lens.srt")


@fixture
def acopopb_yue_hans_ocr_lens_clean() -> Series:
    """ACOPOPB 简体粤文 Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hans_ocr/lens_clean.srt")


@fixture
def acopopb_yue_hans_ocr_paddle() -> Series:
    """ACOPOPB 简体粤文 subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "yue-Hans_ocr/paddle.srt")


@fixture
def acopopb_yue_hans_ocr_paddle_clean() -> Series:
    """ACOPOPB 简体粤文 PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hans_ocr/paddle_clean.srt")


@fixture
def acopopb_yue_hant_ocr_fuse() -> Series:
    """ACOPOPB 繁體粵文 fused subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse.srt")


@fixture
def acopopb_yue_hant_ocr_fuse_clean() -> Series:
    """ACOPOPB 繁體粵文 fused and cleaned subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean.srt")


@fixture
def acopopb_yue_hant_ocr_fuse_clean_validate() -> Series:
    """ACOPOPB 繁體粵文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean_validate.srt")


@fixture
def acopopb_yue_hant_ocr_fuse_clean_validate_review() -> Series:
    """ACOPOPB 繁體粵文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean_validate_review.srt")


@fixture
def acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPOPB 繁體粵文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify() -> Series:
    """ACOPOPB 繁體粵文 simplified fused/cleaned/validated/reviewed/flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hant_ocr" / "fuse_clean_validate_review_flatten_simplify.srt"
    )


@fixture
def acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """ACOPOPB 繁體粵文 simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "yue-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@fixture
def acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize() -> (
    Series
):
    """ACOPOPB 繁體粵文 simplified/reviewed fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir
        / "yue-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
    )


@fixture
def acopopb_yue_hant_ocr_lens() -> Series:
    """ACOPOPB 繁體粵文 subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "yue-Hant_ocr/lens.srt")


@fixture
def acopopb_yue_hant_ocr_lens_clean() -> Series:
    """ACOPOPB 繁體粵文 Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hant_ocr/lens_clean.srt")


@fixture
def acopopb_yue_hant_ocr_paddle() -> Series:
    """ACOPOPB 繁體粵文 subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "yue-Hant_ocr/paddle.srt")


@fixture
def acopopb_yue_hant_ocr_paddle_clean() -> Series:
    """ACOPOPB 繁體粵文 PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hant_ocr/paddle_clean.srt")


@fixture
def acopopb_zho_hans_eng() -> Series:
    """ACOPOPB bilingual 简体中文 and English subtitles."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


@fixture
def acopopb_zho_hans_ocr_fuse() -> Series:
    """ACOPOPB 简体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse.srt")


@fixture
def acopopb_zho_hans_ocr_fuse_clean() -> Series:
    """ACOPOPB 简体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean.srt")


@fixture
def acopopb_zho_hans_ocr_fuse_clean_validate() -> Series:
    """ACOPOPB 简体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate.srt")


@fixture
def acopopb_zho_hans_ocr_fuse_clean_validate_review() -> Series:
    """ACOPOPB 简体中文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate_review.srt")


@fixture
def acopopb_zho_hans_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPOPB 简体中文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acopopb_zho_hans_ocr_fuse_clean_validate_review_flatten_romanize() -> Series:
    """ACOPOPB 简体中文 fused/cleaned/validated/reviewed/flattened romanized subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten_romanize.srt"
    )


@fixture
def acopopb_zho_hans_ocr_lens() -> Series:
    """ACOPOPB 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hans_ocr/lens.srt")


@fixture
def acopopb_zho_hans_ocr_lens_clean() -> Series:
    """ACOPOPB 简体中文 Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/lens_clean.srt")


@fixture
def acopopb_zho_hans_ocr_paddle() -> Series:
    """ACOPOPB 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle.srt")


@fixture
def acopopb_zho_hans_ocr_paddle_clean() -> Series:
    """ACOPOPB 简体中文 PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle_clean.srt")


@fixture
def acopopb_zho_hant_ocr_fuse() -> Series:
    """ACOPOPB 繁体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse.srt")


@fixture
def acopopb_zho_hant_ocr_fuse_clean() -> Series:
    """ACOPOPB 繁体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean.srt")


@fixture
def acopopb_zho_hant_ocr_fuse_clean_validate() -> Series:
    """ACOPOPB 繁体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate.srt")


@fixture
def acopopb_zho_hant_ocr_fuse_clean_validate_review() -> Series:
    """ACOPOPB 繁体中文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate_review.srt")


@fixture
def acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPOPB 繁体中文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify() -> Series:
    """ACOPOPB 繁体中文 simplified fused/cleaned/validated/reviewed/flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr" / "fuse_clean_validate_review_flatten_simplify.srt"
    )


@fixture
def acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """ACOPOPB 繁体中文 simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@fixture
def acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize() -> (
    Series
):
    """ACOPOPB 繁体中文 simplified/reviewed fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
    )


@fixture
def acopopb_zho_hant_ocr_lens() -> Series:
    """ACOPOPB 繁体中文 subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hant_ocr/lens.srt")


@fixture
def acopopb_zho_hant_ocr_lens_clean() -> Series:
    """ACOPOPB 繁体中文 Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/lens_clean.srt")


@fixture
def acopopb_zho_hant_ocr_paddle() -> Series:
    """ACOPOPB 繁体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle.srt")


@fixture
def acopopb_zho_hant_ocr_paddle_clean() -> Series:
    """ACOPOPB 繁体中文 PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle_clean.srt")


@fixture
def acopopb_zho_simplify_expected_series_diff() -> list[str]:
    """Expected differences for ACOPOPB Simplified vs Traditional subtitles."""
    return [
        "edit: SIMP[15] -> TRAD[15]: '又为什么要打伤紫霞仙子？' -> '又为甚么要打伤紫霞仙子？'",
        "edit: SIMP[20] -> TRAD[20]: '要干什么？' -> '要干甚么？'",
        "edit: SIMP[30] -> TRAD[30]: '要是砸着小朋友那怎么办？' -> '要是砸著小朋友那怎么办？'",
        "edit: SIMP[31] -> TRAD[31]: '就算没有砸着小朋友' -> '就算没有砸著小朋友'",
        "edit: SIMP[32] -> TRAD[32]: '砸着那些花花草草也是不对的' -> '砸著那些花花草草也是不对的'",
        "edit: SIMP[33] -> TRAD[33]: '干什么？' -> '干甚么？'",
        "edit: SIMP[38] -> TRAD[38]: '虽然你很有诚意的看着我' -> '虽然你很有诚意的看著我'",
        "edit: SIMP[51] -> TRAD[51]: '是一堆苍蝇围着你' -> '是一堆苍蝇围著你'",
        "edit: SIMP[64] -> TRAD[64]: '悟空，你诸多藉口' -> '悟空，你诸多借口'",
        "edit: SIMP[66] -> TRAD[66]: '说那么多干什么，打吧！' -> '说那么多干甚么，打吧！'",
        "edit: SIMP[76] -> TRAD[76]: '到底他想说什么？' -> '到底他想说甚么？'",
        "edit: SIMP[86] -> TRAD[86]: '怕什么？' -> '怕甚么？'",
        "edit: SIMP[87] -> TRAD[87]: '什么人？' -> '甚么人？'",
        "edit: SIMP[89] -> TRAD[89]: '你来这里干什么？' -> '你来这里干甚么？'",
        "edit: SIMP[108] -> TRAD[108]: '春三十娘到五岳山来干什么呢？' -> '春三十娘到五岳山来干甚么呢？'",
        "edit: SIMP[220] -> TRAD[220]: '查什么？' -> '查甚么？'",
        "edit: SIMP[255] -> TRAD[255]: '糟了！这么多人它不追，老是追着我' -> '糟了！这么多人牠不追，老是追着我'",
        "edit: SIMP[257] -> TRAD[257]: '干什么？' -> '干甚么？'",
        "edit: SIMP[258] -> TRAD[258]: '什么事？' -> '甚么事？'",
        "edit: SIMP[277] -> TRAD[277]: '什么东西啊？' -> '甚么东西啊？'",
        "edit: SIMP[310] -> TRAD[310]: '通通让开！等我来烧死它！' -> '通通让开！等我来烧死牠！'",
        "edit: SIMP[347] -> TRAD[347]: '对啊！为什么呢？' -> '对啊！为甚么呢？'",
        "edit: SIMP[366] -> TRAD[366]: '怕什么？我的伤都全好了' -> '怕甚么？我的伤都全好了'",
        "edit: SIMP[374] -> TRAD[374]: '为什么每次都是我先⋯' -> '为甚么每次都是我先⋯'",
        "edit: SIMP[392] -> TRAD[392]: '大腿捱一刀算得了什么？' -> '大腿挨一刀算得了甚么？'",
        "edit: SIMP[396] -> TRAD[396]: '我只要点我曲池，疾宫两个穴道' -> '我只要点你曲池，急宫两个穴道'",
        "edit: SIMP[417] -> TRAD[417]: '什么意思嘛？' -> '甚么意思嘛？'",
        "edit: SIMP[422] -> TRAD[422]: '你来干什么？' -> '你来干甚么？'",
        "edit: SIMP[431] -> TRAD[431]: '胡说？那么你跑到五岳山来干什么？' -> '胡说？那么你跑到五岳山来干甚么？'",
        "edit: SIMP[473] -> TRAD[473]: '没什么' -> '没甚么'",
        "edit: SIMP[492] -> TRAD[492]: '为什么晶晶姑娘对我这个造型' -> '为甚么晶晶姑娘对我这个造型'",
        "edit: SIMP[515] -> TRAD[515]: '为什么？' -> '为甚么？'",
        "edit: SIMP[524] -> TRAD[524]: '等一下我一块肉一块肉地给你割下来' -> '等一下我一块肉一块肉的给你割下来'",
        "edit: SIMP[528] -> TRAD[528]: '什么人？' -> '甚么人？'",
        "edit: SIMP[580] -> TRAD[580]: '不知道要那一年才长得出来' -> '不知道要哪一年才长得出来'",
        "edit: SIMP[585] -> TRAD[585]: '什么？水濂洞？' -> '什么？水帘洞？'",
        "edit: SIMP[591] -> TRAD[591]: '我的家在五岳山第四边1 01号B1' -> '我的家在五岳山第四边101号B1'",
        "edit: SIMP[595] -> TRAD[595]: '出什么发啊？' -> '出甚么发啊？'",
        "edit: SIMP[601] -> TRAD[601]: '抢劫什么？' -> '抢劫甚么？'",
        "edit: SIMP[604] -> TRAD[604]: '看什么看？' -> '看甚么看？'",
        "edit: SIMP[619] -> TRAD[619]: '什么菩你老母？' -> '甚么菩你老母？'",
        "edit: SIMP[635] -> TRAD[635]: '为什么不做苹果？要做葡萄' -> '为甚么不做苹果？要做葡萄'",
        "edit: SIMP[644] -> TRAD[644]: '乒拎乓啷的是什么声音？' -> '乒拎乓啷的是甚么声音？'",
        "edit: SIMP[656] -> TRAD[656]: '哎菩提什么老母？' -> '哎菩甚么老母？'",
        "edit: SIMP[657] -> TRAD[657]: '菩提什么老母？' -> '菩甚么老母？'",
        "edit: SIMP[670] -> TRAD[670]: '五百年前孙悟空被观音大使所消灭' -> '五百年前孙悟空被观音大士所消灭'",
        "edit: SIMP[675] -> TRAD[675]: '唐三藏为什么在这里出现' -> '唐三藏为甚么在这里出现'",
        "edit: SIMP[679] -> TRAD[679]: '希望藉此经书来感化世人' -> '希望借此经书来感化世人'",
        "edit: SIMP[685] -> TRAD[685]: '为什么那么多妖在这儿出现' -> '为甚么那么多妖在这儿出现'",
        "edit: SIMP[689] -> TRAD[689]: '在一遍漆黑孤独的环境里头' -> '在一片漆黑孤独的环境里头'",
        "edit: SIMP[691] -> TRAD[691]: '一直盯着我看' -> '一直盯著我看'",
        "edit: SIMP[699] -> TRAD[699]: '趁她们不注意，你就套在他们头上' -> '趁她们不注意，你就套在她们头上'",
        "edit: SIMP[752] -> TRAD[752]: '妈的！\\u3000现在该你还钱' -> '妈的！现在该你还钱'",
        "edit: SIMP[800] -> TRAD[800]: '什么？' -> '甚么？'",
        "edit: SIMP[915] -> TRAD[915]: '看看你们还有什么法宝？' -> '看看你们还有甚么法宝？'",
        "edit: SIMP[992] -> TRAD[992]: '废话少说，干丢你' -> '废话少说，干掉你'",
        "edit: SIMP[1014] -> TRAD[1014]: '什么？' -> '甚么？'",
        "edit: SIMP[1019] -> TRAD[1019]: '你在干什么？' -> '你在干甚么？'",
        "edit: SIMP[1058] -> TRAD[1058]: '你干什么？' -> '你干甚么？'",
        "edit: SIMP[1076] -> TRAD[1076]: '什么？你不是他？' -> '甚么？你不是他？'",
        "edit: SIMP[1152] -> TRAD[1152]: '为什么让我睡一个晚上？' -> '为甚么让我睡一个晚上？'",
        "edit: SIMP[1159] -> TRAD[1159]: '什么？' -> '甚么？'",
        "edit: SIMP[1160] -> TRAD[1160]: '大王，我们发现白晶晶昏倒山崖下' -> '大王，我们发现白晶晶昏倒山崖'",
        "edit: SIMP[1169] -> TRAD[1169]: '我把你伤治好' -> '我把你的伤治好'",
        "edit: SIMP[1176] -> TRAD[1176]: '什么东西呀？' -> '甚么东西呀？'",
        "edit: SIMP[1188] -> TRAD[1188]: '你装成这个样子干什么？' -> '你装成这个样子干甚么？'",
        "edit: SIMP[1191] -> TRAD[1191]: '你干什么嘛？' -> '你干甚么嘛？'",
        "edit: SIMP[1249] -> TRAD[1249]: '把孩大带大' -> '把孩子带大'",
        "edit: SIMP[1258] -> TRAD[1258]: '你说什么？' -> '你说甚么？'",
        "edit: SIMP[1313] -> TRAD[1313]: '波罗什么玩意忘光光了' -> '波罗甚么玩意忘光光了'",
        "edit: SIMP[1314] -> TRAD[1314]: '般若波罗蜜⋯！' -> '般若波罗密⋯！'",
        "edit: SIMP[1320] -> TRAD[1320]: '你老婆就快出来了，你急什么？' -> '你老婆就快出来了，你急甚么？'",
        "edit: SIMP[1324] -> TRAD[1324]: '般若波罗蜜！' -> '般若波罗密！'",
        "edit: SIMP[1326] -> TRAD[1326]: '为什么又说〝又〞呢？' -> '为甚么又说〝又〞呢？'",
        "edit: SIMP[1331] -> TRAD[1331]: '为什么要我别烦你？还要警告我？' -> '为甚么要我别烦你？还要警告我？'",
        "edit: SIMP[1334] -> TRAD[1334]: '为什么？' -> '为甚么？'",
        "edit: SIMP[1346] -> TRAD[1346]: '为什么要打我呢？' -> '为甚么要打我呢？'",
        "edit: SIMP[1381] -> TRAD[1381]: '般若波罗密⋯' -> '般若波罗蜜⋯'",
    ]
