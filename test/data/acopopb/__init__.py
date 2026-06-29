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
    "acopopb_zho_simplify_expected_series_diff",
    "acopopb_yue_simplify_expected_series_diff",
    "acopopb_zho_hant_ocr_lens",
    "acopopb_zho_hant_ocr_lens_clean",
    "acopopb_zho_hant_ocr_paddle",
    "acopopb_zho_hant_ocr_paddle_clean",
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
def acopopb_yue_simplify_expected_series_diff() -> list[str]:
    """Expected differences for ACOPOPB subtitles."""
    return [
        "edit: SIMP[58] -> TRAD[58]: '咁你而家明白……' -> '咁你而家明白⋯⋯'",
        "edit: SIMP[60] -> TRAD[60]: '悟空，你诸多藉口' -> '悟空，你诸多借口'",
        "edit: SIMP[76] -> TRAD[76]: '蒋旧肉俾佢' -> '奖旧肉俾佢'",
        "edit: SIMP[78] -> TRAD[78]: '出面有嗰女人入紧嚟！' -> '出面有个女人入紧嚟！'",
        "edit: SIMP[80] -> TRAD[80]: '怪唔知得你叫盲炳啦' -> '怪不得你叫盲炳啦'",
        "edit: SIMP[81] -> TRAD[81]: '头先你睇唔到哑仔扭吓个箩友嘅咩' -> '头先你睇唔到哑仔扭吓个箩友嘅咩？'",
        "edit: SIMP[98] -> TRAD[98]: '边个系羊？\\u3000边个系虎？' -> '边个系羊？边个系虎？'",
        "edit: SIMP[161] -> TRAD[161]: '冇！小完便穿番条裤啫！' -> '冇！小完便搵番条裤啫！'",
        "edit: SIMP[214] -> TRAD[214]: '我去喽，唔使跪啦帮主！' -> '我去吓啦，唔使跪啦，帮主！'",
        "edit: SIMP[264] -> TRAD[264]: '放火！\\u3000\\u3000是' -> '放火！\\u3000\\u3000系'",
        "edit: SIMP[294] -> TRAD[294]: '帮主嚟喇，快啲救帮主' -> '帮主来啦，快啲救帮主'",
        "edit: SIMP[307] -> TRAD[307]: '熄嘞挂？' -> '熄咗挂？'",
        "edit: SIMP[328] -> TRAD[328]: '去你妈的！你干什么？干你娘你！' -> '去你妈的！你干甚么？干你娘你！'",
        "edit: SIMP[344] -> TRAD[344]: '定啲嚟吖，我哋呢度几廿把嘢〝航〞住㗎嘛' -> '定啲嚟吖，我哋呢度几廿把嘢「航」住㗎嘛'",
        "edit: SIMP[348] -> TRAD[348]: '起身！喺我面前唔好〝诈诈谛谛〞，我话你听' -> '起身！喺我面前唔好「诈诈谛谛」，我话你听'",
        "edit: SIMP[358] -> TRAD[358]: '只要我点曲池，疾宫两个穴位即时冇血流' -> '只要我点曲池、疾宫两个穴位，即时冇血流'",
        "edit: SIMP[386] -> TRAD[386]: '你可以喺菩提老祖口中“氹”佢讲出呢个天机' -> '你可以在菩提老祖口中“氹”佢讲出呢个天机'",
        "edit: SIMP[398] -> TRAD[398]: '分别祗不过佢上次死喺观世音手上' -> '分别只不过佢上次死喺观世音手上'",
        "edit: SIMP[476] -> TRAD[476]: '过去看吓' -> '过去睇吓'",
        "edit: SIMP[490] -> TRAD[490]: '有错！自从见到姑娘之后' -> '右错！自从见到姑娘之后'",
        "edit: SIMP[511] -> TRAD[511]: '你唔做山贼想做状元呀' -> '你唔做山贼想做状元呀？'",
        "edit: SIMP[521] -> TRAD[521]: '孙悟空，你同我躙出来！' -> '孙悟空，你同我𨅬出嚟！'",
        "edit: SIMP[523] -> TRAD[523]: '喺我十八岁嗰年你话会来娶我' -> '喺我十八岁嗰年你话会嚟娶我'",
        "edit: SIMP[527] -> TRAD[527]: '佢话白姑娘来了，就将呢件嘢交返俾你' -> '佢话白姑娘嚟咗，就将呢件嘢交返给你'",
        "edit: SIMP[541] -> TRAD[541]: '我屋企在五岳山第四边第1 01号地下' -> '我屋企在五岳山第四边第101号地下'",
        "edit: SIMP[551] -> TRAD[551]: '打劫咩嘢话？' -> '打劫咩话？'",
        "edit: SIMP[596] -> TRAD[596]: '月光，有呀' -> '月光，冇呀'",
        "edit: SIMP[600] -> TRAD[600]: '边个？\\u3000边个老母？⋯⋯' -> '边个？边个老母？⋯⋯'",
        "edit: SIMP[602] -> TRAD[602]: '我变咗荔枝呀' -> '我变咗提子呀'",
        "edit: SIMP[605] -> TRAD[605]: '哗！咁大坨挂喺度' -> '哗！咁大揪挂喺度'",
        "edit: SIMP[614] -> TRAD[614]: '五百年前孙悟空俾观音大士所消灭' -> '五百年前孙悟空俾观音大使所消灭'",
        "edit: SIMP[628] -> TRAD[628]: '唔怪得一路以嚟我都发着同一个恶梦' -> '唔怪得一路以嚟我都发著同一个恶梦'",
        "edit: SIMP[656] -> TRAD[656]: '冇办法，为咗帮主吩咐咋' -> '有办法，为咗帮主吩咐咋'",
        "edit: SIMP[657] -> TRAD[657]: '你等下' -> '你等一下'",
        "edit: SIMP[670] -> TRAD[670]: '你不〝嬲〞都睇唔到嘅啦' -> '你不嬲都睇唔到嘅啦'",
        "edit: SIMP[676] -> TRAD[676]: '帮主！着火啦！' -> '帮主！着火啦'",
        "edit: SIMP[677] -> TRAD[677]: '好还钱喎，靓仔！' -> '好讨钱喎，靓仔！'",
        "edit: SIMP[696] -> TRAD[696]: '明刀明枪同佢炼过！\\u3000现身啦！\\u3000兄弟' -> '明刀明枪同佢炼过！现身啦！兄弟'",
        "edit: SIMP[713] -> TRAD[713]: '行， ⋯⋯行呀' -> '行，……行呀'",
        "edit: SIMP[729] -> TRAD[729]: '天堂有路你唔走，地狱无门\\u3000闯进来' -> '天堂有路你唔走，地狱无门闯进来'",
        "edit: SIMP[796] -> TRAD[796]: '睇吓你自己只掌' -> '睇吓你自己只手掌'",
        "edit: SIMP[807] -> TRAD[807]: '唔好呀！ ⋯' -> '唔好呀！⋯'",
        "edit: SIMP[908] -> TRAD[908]: '俾把剑佢！' -> '俾把劍佢！'",
        "edit: SIMP[909] -> TRAD[909]: '佢呀！ 知道' -> '佢呀！知道'",
        "edit: SIMP[922] -> TRAD[922]: '响出来' -> '墙外边'",
        "edit: SIMP[925] -> TRAD[925]: '行开' -> '走开'",
        "edit: SIMP[946] -> TRAD[946]: '你冇事吗？' -> '你冇事吖吗？'",
        "edit: SIMP[964] -> TRAD[964]: '攞条匙嚟！困佢喺里面' -> '摆条匙嚟！困佢喺里面'",
        "edit: SIMP[1028] -> TRAD[1028]: '天有眼啰' -> '天冇眼啰'",
        "edit: SIMP[1030] -> TRAD[1030]: '竟然同个咁肉酸嘅男人有了' -> '竟然同个咁肉酸嘅男人有咗'",
        "edit: SIMP[1056] -> TRAD[1056]: '奶妈锡番你' -> '奶妈识番你'",
        "edit: SIMP[1091] -> TRAD[1091]: '咦，块地都唔系好硬' -> '咦，这块地都唔系好硬'",
        "edit: SIMP[1092] -> TRAD[1092]: '今次无死喇' -> '今次冇死喇'",
        "edit: SIMP[1094] -> TRAD[1094]: '我而家医番好你嘅伤' -> '我而家医返好你嘅伤'",
        "edit: SIMP[1098] -> TRAD[1098]: '如果唔系我就要你死得俾而家痛苦十倍' -> '如果唔系我就要你死得比而家痛苦十倍'",
        "edit: SIMP[1102] -> TRAD[1102]: '般若波罗蜜，梵文嚟嗰喎' -> '般若波罗蜜，梵文嚟㗎喎'",
        "edit: SIMP[1104] -> TRAD[1104]: '盘丝大仙留下嘅宝物？' -> '盘丝大仙留低嘅宝物？'",
        "edit: SIMP[1210] -> TRAD[1210]: '“元神出窍”' -> '「元神出窍」'",
        "edit: SIMP[1224] -> TRAD[1224]: '好好哋凑大我哋嗰仔佢' -> '好好哋凑大我哋嗰仔，佢'",
        "edit: SIMP[1251] -> TRAD[1251]: '点解我讲〝又〞嘅？' -> '点解我讲「又」嘅？'",
        "edit: SIMP[1261] -> TRAD[1261]: '出嚟啦！？' -> '出嚟啦！'",
        "edit: SIMP[1263] -> TRAD[1263]: '娘子！娘子！ ⋯⋯' -> '娘子！娘子！⋯⋯'",
        "edit: SIMP[1265] -> TRAD[1265]: '般若波罗密⋯⋯' -> '般若波罗蜜⋯⋯'",
        "edit: SIMP[1309] -> TRAD[1309]: '再嚟' -> '再来'",
        "edit: SIMP[1319] -> TRAD[1319]: '你「虾」我唔识字呀！' -> '你「吓」我唔识字呀！'",
        "edit: SIMP[1332] -> TRAD[1332]: '如果有人“恰”你，你就“挞”我啦' -> '如果有人「恰」你，你就「挞」我啦'",
    ]


@fixture
def acopopb_zho_simplify_expected_series_diff() -> list[str]:
    """Expected differences for ACOPOPB subtitles."""
    return [
        "edit: SIMP[15] -> TRAD[15]: '又为什么要打伤紫霞仙子？' -> '又为甚么要打伤紫霞仙子？'",
        "edit: SIMP[20] -> TRAD[20]: '要干什么？' -> '要干甚么？'",
        "edit: SIMP[30] -> TRAD[30]: '要是砸着小朋友那怎么办？' -> '要是砸著小朋友那怎么办？'",
        "edit: SIMP[31] -> TRAD[31]: '就算没有砸着小朋友' -> '就算没有砸著小朋友'",
        "edit: SIMP[32] -> TRAD[32]: '砸着那些花花草草也是不对的' -> '砸著那些花花草草也是不对的'",
        "edit: SIMP[33] -> TRAD[33]: '干什么？' -> '干甚么？'",
        "edit: SIMP[38] -> TRAD[38]: '虽然你很有诚意的看着我' -> '虽然你很有诚意的看著我'",
        "edit: SIMP[51] -> TRAD[51]: '是一堆苍蝇围着你' -> '是一堆苍蝇围著你'",
        "edit: SIMP[63] -> TRAD[63]: '现在大家明白为什么我要杀它啦' -> '现在大家明白为甚么我要杀它啦'",
        "edit: SIMP[66] -> TRAD[66]: '说那么多干什么，打吧！' -> '说那么多干甚么，打吧！'",
        "edit: SIMP[76] -> TRAD[76]: '到底他想说什么？' -> '到底他想说甚么？'",
        "edit: SIMP[86] -> TRAD[86]: '怕什么？' -> '怕甚么？'",
        "edit: SIMP[87] -> TRAD[87]: '什么人？' -> '甚么人？'",
        "edit: SIMP[89] -> TRAD[89]: '你来这里干什么？' -> '你来这里干甚么？'",
        "edit: SIMP[108] -> TRAD[108]: '春三十娘到五岳山来干什么呢？' -> '春三十娘到五岳山来干甚么呢？'",
        "edit: SIMP[112] -> TRAD[112]: '还把银子顶在头上干什么？' -> '还把银子顶在头上干甚么？'",
        "edit: SIMP[115] -> TRAD[115]: '你说什么？' -> '你说甚么？'",
        "edit: SIMP[118] -> TRAD[118]: '帮主，我不是二当家，我是瞎子啊' -> '帮主，我不是二当家，我系瞎子啊'",
        "edit: SIMP[151] -> TRAD[151]: '收到⋯啊！⋯' -> '收到⋯啊！ ⋯'",
        "edit: SIMP[154] -> TRAD[154]: '怕什么！万事有我！' -> '怕甚么！万事有我！'",
        "edit: SIMP[220] -> TRAD[220]: '查什么？' -> '查甚么？'",
        "edit: SIMP[248] -> TRAD[248]: '蜘蛛！蜘蛛呀！ ⋯' -> '蜘蛛！蜘蛛呀！⋯'",
        "edit: SIMP[255] -> TRAD[255]: '糟了！这么多人它不追，老是追着我' -> '糟了！这么多人牠不追，老是追着我'",
        "edit: SIMP[257] -> TRAD[257]: '干什么？' -> '干甚么？'",
        "edit: SIMP[258] -> TRAD[258]: '什么事？' -> '甚么事？'",
        "edit: SIMP[277] -> TRAD[277]: '什么东西啊？' -> '甚么东西啊？'",
        "edit: SIMP[279] -> TRAD[279]: '二当家那么开心扛着什么东西走啦？' -> '二当家那么开心扛着甚么东西走啦？'",
        "edit: SIMP[310] -> TRAD[310]: '通通让开！等我来烧死它！' -> '通通让开！等我来烧死牠！'",
        "edit: SIMP[348] -> TRAD[348]: '我明白了！' -> '我明白\\u3000了！'",
        "edit: SIMP[366] -> TRAD[366]: '怕什么？我的伤都全好了' -> '怕甚么？我的伤都全好了'",
        "edit: SIMP[374] -> TRAD[374]: '为什么每次都是我先⋯' -> '为甚么每次都是我先⋯'",
        "edit: SIMP[392] -> TRAD[392]: '大腿捱一刀算得了什么？' -> '大腿挨一刀算得了甚么？'",
        "edit: SIMP[396] -> TRAD[396]: '我只要点你曲池，疾宫两个穴道' -> '我只要点你曲池，急宫两个穴道'",
        "edit: SIMP[417] -> TRAD[417]: '什么意思嘛？' -> '甚么意思嘛？'",
        "edit: SIMP[422] -> TRAD[422]: '你来干什么？' -> '你来干甚么？'",
        "edit: SIMP[426] -> TRAD[426]: '尝佢长生不老之肉' -> '尝她长生不老之肉'",
        "edit: SIMP[431] -> TRAD[431]: '胡说？那么你跑到五岳山来干什么？' -> '胡说？那么你跑到五岳山来干甚么？'",
        "edit: SIMP[453] -> TRAD[453]: '我结鞋带。' -> '我系鞋带'",
        "edit: SIMP[456] -> TRAD[456]: '到时候群妖会合五指山' -> '到时候群妖汇合五指山'",
        "edit: SIMP[473] -> TRAD[473]: '没什么' -> '没甚么'",
        "edit: SIMP[492] -> TRAD[492]: '为什么晶晶姑娘对我这个造型' -> '为甚么晶晶姑娘对我这个造型'",
        "edit: SIMP[515] -> TRAD[515]: '为什么？' -> '为甚么？'",
        "edit: SIMP[521] -> TRAD[521]: '这么英气潇洒你说有鬼！' -> '这么英雄潇洒你说有鬼！'",
        "edit: SIMP[524] -> TRAD[524]: '等一下我一块肉一块肉地给你割下来' -> '等一下我一块肉一块肉的给你割下来'",
        "edit: SIMP[528] -> TRAD[528]: '什么人？' -> '甚么人？'",
        "edit: SIMP[529] -> TRAD[529]: '长夜漫漫， 无心睡眠' -> '长夜漫漫，无心睡眠'",
        "edit: SIMP[559] -> TRAD[559]: '省省吧你，改变什么形象' -> '省省吧你，改变什么形像'",
        "edit: SIMP[564] -> TRAD[564]: '什么不好像，像个臭猴子' -> '甚么不好像，像个臭猴子'",
        "edit: SIMP[580] -> TRAD[580]: '不知道要那一年才长得出来' -> '不知道要哪一年才长得出来'",
        "edit: SIMP[585] -> TRAD[585]: '什么？水濂洞？' -> '什么？水帘洞？'",
        "edit: SIMP[586] -> TRAD[586]: '你是谁你？' -> '你是谁？'",
        "edit: SIMP[591] -> TRAD[591]: '我的家在五岳山第四边1 01号B1' -> '我的家在五岳山第四边101号B1'",
        "edit: SIMP[595] -> TRAD[595]: '出什么发啊？' -> '出甚么发啊？'",
        "edit: SIMP[604] -> TRAD[604]: '看什么看？' -> '看甚么看？'",
        "edit: SIMP[619] -> TRAD[619]: '什么菩提老母？' -> '甚么菩提老祖？'",
        "edit: SIMP[631] -> TRAD[631]: '没有？那我的葡萄到哪儿去了？' -> '没有？那我的葡萄到那儿去了？'",
        "edit: SIMP[635] -> TRAD[635]: '为什么不做苹果？要做葡萄' -> '为甚么不做苹果？要做葡萄'",
        "edit: SIMP[644] -> TRAD[644]: '乒拎乓啷的是什么声音？' -> '乒伶乓啷的是甚么声音？'",
        "edit: SIMP[654] -> TRAD[654]: '天还没有黑，哪来的月光' -> '天还没有黑，那来的月光'",
        "edit: SIMP[657] -> TRAD[657]: '菩提老母？' -> '菩提什么老母？'",
        "edit: SIMP[670] -> TRAD[670]: '五百年前孙悟空被观音大使所消灭' -> '五百年前孙悟空被观音大士所消灭'",
        "edit: SIMP[675] -> TRAD[675]: '唐三藏为什么在这里出现' -> '唐三藏为什么在这里出现？'",
        "edit: SIMP[685] -> TRAD[685]: '为什么那么多妖在这儿出现' -> '为什么那么多妖在这儿出现？'",
        "edit: SIMP[690] -> TRAD[690]: '一对一对非常迷蒙的眼睛' -> '一对一对非常迷迷的眼睛'",
        "edit: SIMP[697] -> TRAD[697]: '这两个乾坤袋，一叠隐身符' -> '这两个乾坤袋，一叠隐身符，'",
        "edit: SIMP[699] -> TRAD[699]: '趁她们不注意，你就套在他们头上' -> '趁她们不注意，你就套在她们头上'",
        "edit: SIMP[752] -> TRAD[752]: '妈的！\\u3000现在该你还钱' -> '妈的！现在该你还钱'",
        "edit: SIMP[800] -> TRAD[800]: '什么？' -> '甚么？'",
        "edit: SIMP[849] -> TRAD[849]: '今次算是少走了一步' -> '今次算少走了一步'",
        "edit: SIMP[853] -> TRAD[853]: '我最有眼光就是跟着帮主' -> '我最有眼光就是跟着帮主。'",
        "edit: SIMP[992] -> TRAD[992]: '废话少说，干丢你' -> '废话少说，干掉你'",
        "edit: SIMP[1005] -> TRAD[1005]: '等他回复真身之后' -> '等他恢复真身之后'",
        "edit: SIMP[1014] -> TRAD[1014]: '什么？' -> '甚么？'",
        "edit: SIMP[1019] -> TRAD[1019]: '你在干什么？' -> '你在干甚么？'",
        "edit: SIMP[1058] -> TRAD[1058]: '你干什么？' -> '你干甚么？'",
        "edit: SIMP[1076] -> TRAD[1076]: '什么？你不是他？' -> '甚么？你不是他？'",
        "edit: SIMP[1105] -> TRAD[1105]: '居然跟这么丑的男人有了' -> '居然跟这么丑的男人有了孩子'",
        "edit: SIMP[1152] -> TRAD[1152]: '为什么让我睡一个晚上？' -> '为甚么让我睡一个晚上？'",
        "edit: SIMP[1156] -> TRAD[1156]: '你别希望我把唐僧的告诉你' -> '你别希望我把唐僧的事告诉你'",
        "edit: SIMP[1159] -> TRAD[1159]: '什么？' -> '甚么？'",
        "edit: SIMP[1160] -> TRAD[1160]: '大王，我们发现白晶晶昏倒山崖下' -> '大王，我们发现白晶晶昏倒山崖'",
        "edit: SIMP[1176] -> TRAD[1176]: '什么东西呀？' -> '甚么东西呀？'",
        "edit: SIMP[1188] -> TRAD[1188]: '你装成这个样子干什么？' -> '你装成这个样子干甚么？'",
        "edit: SIMP[1191] -> TRAD[1191]: '你干什么嘛？' -> '你干甚么嘛？'",
        "edit: SIMP[1249] -> TRAD[1249]: '把孩大带大' -> '把孩子带大'",
        "edit: SIMP[1258] -> TRAD[1258]: '你说什么？' -> '你说甚么？'",
        "edit: SIMP[1289] -> TRAD[1289]: '“元神出窍”' -> '「元神出窍」'",
        "edit: SIMP[1326] -> TRAD[1326]: '为什么又说〝又〞呢？' -> '为什么又说“又”呢？'",
        "edit: SIMP[1331] -> TRAD[1331]: '为什么要我别烦你？还要警告我？' -> '为甚么要我别烦你？还要警告我？'",
        "edit: SIMP[1334] -> TRAD[1334]: '为什么？' -> '为甚么？'",
        "edit: SIMP[1346] -> TRAD[1346]: '为什么要打我呢？' -> '为甚么要打我呢？'",
        "edit: SIMP[1361] -> TRAD[1361]: '你完全误会了 找死？' -> '你完全误会了，找死？'",
        "edit: SIMP[1381] -> TRAD[1381]: '般若波罗密⋯' -> '般若波罗蜜⋯'",
    ]
