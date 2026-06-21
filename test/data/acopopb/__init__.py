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
        "edit: SIMP[64] -> TRAD[64]: '悟空，你诸多藉口' -> '悟空，你诸多借口'",
        "edit: SIMP[392] -> TRAD[392]: '大腿捱一刀算得了什么？' -> '大腿挨一刀算得了什么？'",
        "edit: SIMP[585] -> TRAD[585]: '什么？水濂洞？' -> '什么？水帘洞？'",
        "edit: SIMP[591] -> TRAD[591]: '我的家在五岳山第四边1 01号B1' -> '我的家在五岳山第四边101号B1'",
        "edit: SIMP[670] -> TRAD[670]: '五百年前孙悟空被观音大使所消灭' -> '五百年前孙悟空被观音大士所消灭'",
        "edit: SIMP[679] -> TRAD[679]: '希望藉此经书来感化世人' -> '希望借此经书来感化世人'",
        "edit: SIMP[689] -> TRAD[689]: '在一遍漆黑孤独的环境里头' -> '在一片漆黑孤独的环境里头'",
        "edit: SIMP[699] -> TRAD[699]: '趁她们不注意，你就套在他们头上' -> '趁她们不注意，你就套在她们头上'",
        "edit: SIMP[752] -> TRAD[752]: '妈的！\\u3000现在该你还钱' -> '妈的！现在该你还钱'",
        "edit: SIMP[992] -> TRAD[992]: '废话少说，干丢你' -> '废话少说，干掉你'",
        "edit: SIMP[1160] -> TRAD[1160]: '大王，我们发现白晶晶昏倒山崖下' -> '大王，我们发现白晶晶昏倒山崖'",
        "edit: SIMP[1169] -> TRAD[1169]: '我把你伤治好' -> '我把你的伤治好'",
        "edit: SIMP[1249] -> TRAD[1249]: '把孩大带大' -> '把孩子带大'",
    ]
