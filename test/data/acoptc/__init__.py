#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for ACOPTC."""

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
    "acoptc_eng",
    "acoptc_zho_hans",
    "acoptc_zho_hant",
    "get_acoptc_eng_block_review_test_cases",
    "get_acoptc_eng_ocr_fusion_test_cases",
    "get_acoptc_yue_hans_block_review_test_cases",
    "get_acoptc_yue_hans_ocr_fusion_test_cases",
    "get_acoptc_yue_hant_block_review_test_cases",
    "get_acoptc_yue_hant_ocr_fusion_test_cases",
    "get_acoptc_yue_hant_simplify_block_review_test_cases",
    "get_acoptc_zho_hans_block_review_test_cases",
    "get_acoptc_zho_hans_ocr_fusion_test_cases",
    "get_acoptc_zho_hant_block_review_test_cases",
    "get_acoptc_zho_hant_ocr_fusion_test_cases",
    "get_acoptc_zho_hant_simplify_block_review_test_cases",
    "acoptc_eng_ocr_fuse",
    "acoptc_eng_ocr_fuse_clean",
    "acoptc_eng_ocr_fuse_clean_validate",
    "acoptc_eng_ocr_fuse_clean_validate_review",
    "acoptc_eng_ocr_fuse_clean_validate_review_flatten",
    "acoptc_eng_ocr_lens",
    "acoptc_eng_ocr_lens_clean",
    "acoptc_eng_ocr_tesseract",
    "acoptc_eng_ocr_tesseract_clean",
    "acoptc_yue_hans_eng",
    "acoptc_yue_hans_ocr_fuse",
    "acoptc_yue_hans_ocr_fuse_clean",
    "acoptc_yue_hans_ocr_fuse_clean_validate",
    "acoptc_yue_hans_ocr_fuse_clean_validate_review",
    "acoptc_yue_hans_ocr_fuse_clean_validate_review_flatten",
    "acoptc_yue_hans_ocr_fuse_clean_validate_review_flatten_romanize",
    "acoptc_yue_hans_ocr_lens",
    "acoptc_yue_hans_ocr_lens_clean",
    "acoptc_yue_hans_ocr_paddle",
    "acoptc_yue_hans_ocr_paddle_clean",
    "acoptc_yue_hant_ocr_fuse",
    "acoptc_yue_hant_ocr_fuse_clean",
    "acoptc_yue_hant_ocr_fuse_clean_validate",
    "acoptc_yue_hant_ocr_fuse_clean_validate_review",
    "acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten",
    "acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify",
    "acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
    "acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
    "acoptc_yue_hant_ocr_lens",
    "acoptc_yue_hant_ocr_lens_clean",
    "acoptc_yue_hant_ocr_paddle",
    "acoptc_yue_hant_ocr_paddle_clean",
    "acoptc_zho_hans_eng",
    "acoptc_zho_hans_ocr_fuse",
    "acoptc_zho_hans_ocr_fuse_clean",
    "acoptc_zho_hans_ocr_fuse_clean_validate",
    "acoptc_zho_hans_ocr_fuse_clean_validate_review",
    "acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten",
    "acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten_romanize",
    "acoptc_zho_hans_ocr_lens",
    "acoptc_zho_hans_ocr_lens_clean",
    "acoptc_zho_hans_ocr_paddle",
    "acoptc_zho_hans_ocr_paddle_clean",
    "acoptc_zho_hant_ocr_fuse",
    "acoptc_zho_hant_ocr_fuse_clean",
    "acoptc_zho_hant_ocr_fuse_clean_validate",
    "acoptc_zho_hant_ocr_fuse_clean_validate_review",
    "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten",
    "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
    "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
    "acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
    "acoptc_zho_simplify_expected_series_diff",
    "acoptc_yue_simplify_expected_series_diff",
    "acoptc_zho_hant_ocr_lens",
    "acoptc_zho_hant_ocr_lens_clean",
    "acoptc_zho_hant_ocr_paddle",
    "acoptc_zho_hant_ocr_paddle_clean",
]

title_root = test_data_root / Path(__file__).parent.name
input_path = title_root / "input"
output_dir = title_root / "output"


@fixture
def acoptc_eng() -> Series:
    """ACOPTC English subtitles."""
    return Series.load(input_path / "eng.srt")


@fixture
def acoptc_zho_hans() -> Series:
    """ACOPTC 简体中文 subtitles."""
    return Series.load(input_path / "zho-Hans.srt")


@fixture
def acoptc_zho_hant() -> Series:
    """ACOPTC 繁体中文 subtitles."""
    return Series.load(input_path / "zho-Hant.srt")


@cache
def get_acoptc_eng_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptEng,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC English block review test cases.

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
def get_acoptc_eng_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptEng,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC English OCR fusion test cases.

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
def get_acoptc_yue_hans_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC 简体粤文 block review test cases.

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
def get_acoptc_yue_hans_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC 简体粤文 OCR fusion test cases.

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
def get_acoptc_yue_hant_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC 繁體粵文 block review test cases.

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
def get_acoptc_yue_hant_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC 繁體粵文 OCR fusion test cases.

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
def get_acoptc_yue_hant_simplify_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC 繁體粵文 simplification block review test cases.

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
def get_acoptc_zho_hans_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC 简体中文 block review test cases.

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
def get_acoptc_zho_hans_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC 简体中文 OCR fusion test cases.

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
def get_acoptc_zho_hant_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC 繁体中文 block review test cases.

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
def get_acoptc_zho_hant_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC 繁体中文 OCR fusion test cases.

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
def get_acoptc_zho_hant_simplify_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC 繁体中文 simplification block review test cases.

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
def acoptc_eng_ocr_fuse() -> Series:
    """ACOPTC English fused subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse.srt")


@fixture
def acoptc_eng_ocr_fuse_clean() -> Series:
    """ACOPTC English fused and cleaned subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean.srt")


@fixture
def acoptc_eng_ocr_fuse_clean_validate() -> Series:
    """ACOPTC English fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate.srt")


@fixture
def acoptc_eng_ocr_fuse_clean_validate_review() -> Series:
    """ACOPTC English fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate_review.srt")


@fixture
def acoptc_eng_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPTC English fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate_review_flatten.srt")


@fixture
def acoptc_eng_ocr_lens() -> Series:
    """ACOPTC English subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "eng_ocr/lens.srt")


@fixture
def acoptc_eng_ocr_lens_clean() -> Series:
    """ACOPTC English Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "eng_ocr/lens_clean.srt")


@fixture
def acoptc_eng_ocr_tesseract() -> Series:
    """ACOPTC English subtitles OCRed using Tesseract."""
    return Series.load(output_dir / "eng_ocr/tesseract.srt")


@fixture
def acoptc_eng_ocr_tesseract_clean() -> Series:
    """ACOPTC English Tesseract OCR subtitles, cleaned."""
    return Series.load(output_dir / "eng_ocr/tesseract_clean.srt")


@fixture
def acoptc_yue_hans_eng() -> Series:
    """ACOPTC bilingual 简体粤文 and English subtitles."""
    return Series.load(output_dir / "yue-Hans_eng.srt")


@fixture
def acoptc_yue_hans_ocr_fuse() -> Series:
    """ACOPTC 简体粤文 fused subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse.srt")


@fixture
def acoptc_yue_hans_ocr_fuse_clean() -> Series:
    """ACOPTC 简体粤文 fused and cleaned subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean.srt")


@fixture
def acoptc_yue_hans_ocr_fuse_clean_validate() -> Series:
    """ACOPTC 简体粤文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean_validate.srt")


@fixture
def acoptc_yue_hans_ocr_fuse_clean_validate_review() -> Series:
    """ACOPTC 简体粤文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean_validate_review.srt")


@fixture
def acoptc_yue_hans_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPTC 简体粤文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acoptc_yue_hans_ocr_fuse_clean_validate_review_flatten_romanize() -> Series:
    """ACOPTC 简体粤文 fused/cleaned/validated/reviewed/flattened romanized subtitles."""
    return Series.load(
        output_dir / "yue-Hans_ocr/fuse_clean_validate_review_flatten_romanize.srt"
    )


@fixture
def acoptc_yue_hans_ocr_lens() -> Series:
    """ACOPTC 简体粤文 subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "yue-Hans_ocr/lens.srt")


@fixture
def acoptc_yue_hans_ocr_lens_clean() -> Series:
    """ACOPTC 简体粤文 Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hans_ocr/lens_clean.srt")


@fixture
def acoptc_yue_hans_ocr_paddle() -> Series:
    """ACOPTC 简体粤文 subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "yue-Hans_ocr/paddle.srt")


@fixture
def acoptc_yue_hans_ocr_paddle_clean() -> Series:
    """ACOPTC 简体粤文 PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hans_ocr/paddle_clean.srt")


@fixture
def acoptc_yue_hant_ocr_fuse() -> Series:
    """ACOPTC 繁體粵文 fused subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse.srt")


@fixture
def acoptc_yue_hant_ocr_fuse_clean() -> Series:
    """ACOPTC 繁體粵文 fused and cleaned subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean.srt")


@fixture
def acoptc_yue_hant_ocr_fuse_clean_validate() -> Series:
    """ACOPTC 繁體粵文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean_validate.srt")


@fixture
def acoptc_yue_hant_ocr_fuse_clean_validate_review() -> Series:
    """ACOPTC 繁體粵文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean_validate_review.srt")


@fixture
def acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPTC 繁體粵文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify() -> Series:
    """ACOPTC 繁體粵文 simplified fused/cleaned/validated/reviewed/flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hant_ocr" / "fuse_clean_validate_review_flatten_simplify.srt"
    )


@fixture
def acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """ACOPTC 繁體粵文 simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "yue-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@fixture
def acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize() -> (
    Series
):
    """ACOPTC 繁體粵文 simplified/reviewed fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir
        / "yue-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
    )


@fixture
def acoptc_yue_hant_ocr_lens() -> Series:
    """ACOPTC 繁體粵文 subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "yue-Hant_ocr/lens.srt")


@fixture
def acoptc_yue_hant_ocr_lens_clean() -> Series:
    """ACOPTC 繁體粵文 Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hant_ocr/lens_clean.srt")


@fixture
def acoptc_yue_hant_ocr_paddle() -> Series:
    """ACOPTC 繁體粵文 subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "yue-Hant_ocr/paddle.srt")


@fixture
def acoptc_yue_hant_ocr_paddle_clean() -> Series:
    """ACOPTC 繁體粵文 PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hant_ocr/paddle_clean.srt")


@fixture
def acoptc_zho_hans_eng() -> Series:
    """ACOPTC bilingual 简体中文 and English subtitles."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


@fixture
def acoptc_zho_hans_ocr_fuse() -> Series:
    """ACOPTC 简体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse.srt")


@fixture
def acoptc_zho_hans_ocr_fuse_clean() -> Series:
    """ACOPTC 简体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean.srt")


@fixture
def acoptc_zho_hans_ocr_fuse_clean_validate() -> Series:
    """ACOPTC 简体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate.srt")


@fixture
def acoptc_zho_hans_ocr_fuse_clean_validate_review() -> Series:
    """ACOPTC 简体中文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate_review.srt")


@fixture
def acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPTC 简体中文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten_romanize() -> Series:
    """ACOPTC 简体中文 fused/cleaned/validated/reviewed/flattened romanized subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten_romanize.srt"
    )


@fixture
def acoptc_zho_hans_ocr_lens() -> Series:
    """ACOPTC 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hans_ocr/lens.srt")


@fixture
def acoptc_zho_hans_ocr_lens_clean() -> Series:
    """ACOPTC 简体中文 Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/lens_clean.srt")


@fixture
def acoptc_zho_hans_ocr_paddle() -> Series:
    """ACOPTC 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle.srt")


@fixture
def acoptc_zho_hans_ocr_paddle_clean() -> Series:
    """ACOPTC 简体中文 PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle_clean.srt")


@fixture
def acoptc_zho_hant_ocr_fuse() -> Series:
    """ACOPTC 繁体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse.srt")


@fixture
def acoptc_zho_hant_ocr_fuse_clean() -> Series:
    """ACOPTC 繁体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean.srt")


@fixture
def acoptc_zho_hant_ocr_fuse_clean_validate() -> Series:
    """ACOPTC 繁体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate.srt")


@fixture
def acoptc_zho_hant_ocr_fuse_clean_validate_review() -> Series:
    """ACOPTC 繁体中文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate_review.srt")


@fixture
def acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPTC 繁体中文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify() -> Series:
    """ACOPTC 繁体中文 simplified fused/cleaned/validated/reviewed/flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr" / "fuse_clean_validate_review_flatten_simplify.srt"
    )


@fixture
def acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """ACOPTC 繁体中文 simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@fixture
def acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize() -> (
    Series
):
    """ACOPTC 繁体中文 simplified/reviewed fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
    )


@fixture
def acoptc_zho_hant_ocr_lens() -> Series:
    """ACOPTC 繁体中文 subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hant_ocr/lens.srt")


@fixture
def acoptc_zho_hant_ocr_lens_clean() -> Series:
    """ACOPTC 繁体中文 Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/lens_clean.srt")


@fixture
def acoptc_zho_hant_ocr_paddle() -> Series:
    """ACOPTC 繁体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle.srt")


@fixture
def acoptc_zho_hant_ocr_paddle_clean() -> Series:
    """ACOPTC 繁体中文 PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle_clean.srt")


@fixture
def acoptc_yue_simplify_expected_series_diff() -> list[str]:
    """Expected differences for ACOPTC Yue Simplified vs Traditional subtitles."""
    return []


@fixture
def acoptc_zho_simplify_expected_series_diff() -> list[str]:
    """Expected differences for ACOPTC Zho Simplified vs Traditional subtitles."""
    return [
        "edit: SIMP[3] -> TRAD[3]: '耽搁大家一会，很快就点着了' -> '担搁大家一会，很快就点着了'",
        "edit: SIMP[8] -> TRAD[8]: '可是灯芯不见了，有什么办法呢？' -> '可是灯芯不见了，有甚么办法呢？'",
        "edit: SIMP[61] -> TRAD[61]: '这个山头所有东西都属于我的' -> '这个山头所有东西都属于我'",
        "edit: SIMP[71] -> TRAD[71]: '你没有变成孙悟空托生' -> '你没有变成孙悟空投世'",
        "edit: SIMP[93] -> TRAD[93]: '这个月光宝盒呢⋯\\u3000\\u3000我的！' -> '这个月光宝盒呢⋯我的！'",
        "edit: SIMP[107] -> TRAD[107]: '还有这个宝盒呢⋯' -> '还有这个宝盒呢⋯我的！'",
        "edit: SIMP[117] -> TRAD[117]: '我为什么要对你这么好？' -> '我为甚么要对你这么好？'",
        "edit: SIMP[119] -> TRAD[119]: '你走了我一个人留在这里什么意思' -> '你走了我一个人留在这里甚么意思'",
        "edit: SIMP[149] -> TRAD[149]: '你到那儿去？站住' -> '你到那儿去？站住。'",
        "edit: SIMP[154] -> TRAD[154]: '你看到什么啦？' -> '你看到甚么啦？'",
        "edit: SIMP[158] -> TRAD[158]: '她跟你说了什么？' -> '她跟你说了甚么？'",
        "edit: SIMP[186] -> TRAD[186]: '至尊宝？ 玉尊玉？ 想骗我啊？' -> '至尊宝？\\u3000至尊玉？\\u3000想骗我啊？'",
        "edit: SIMP[211] -> TRAD[211]: '干什么？' -> '干甚么？'",
        "edit: SIMP[219] -> TRAD[219]: '我们跟紧他不要打草惊蛇' -> '我们跟紧他，不要打草惊蛇'",
        "edit: SIMP[227] -> TRAD[227]: '这个猪头切不半给我，谢谢' -> '这个猪头切一半给我，谢谢'",
        "edit: SIMP[229] -> TRAD[229]: '干什么？' -> '干甚么？'",
        "edit: SIMP[240] -> TRAD[240]: '你怕什么？' -> '你怕甚么？'",
        "edit: SIMP[333] -> TRAD[333]: '干什么呀？' -> '干甚么呀？'",
        "edit: SIMP[339] -> TRAD[339]: '乱扔会染污环境！' -> '乱扔会污染环境！'",
        "edit: SIMP[343] -> TRAD[343]: '你干什么？' -> '你干甚么？'",
        "edit: SIMP[370] -> TRAD[370]: '我为什么要杀它了' -> '我为甚么要杀牠了'",
        "edit: SIMP[372] -> TRAD[372]: '诸多藉口' -> '诸多借口'",
        "edit: SIMP[382] -> TRAD[382]: '它又何罪之有呢？' -> '牠又何罪之有呢？'",
        "edit: SIMP[383] -> TRAD[383]: '不如等它吃了我之后' -> '不如等牠吃了我之后'",
        "edit: SIMP[384] -> TRAD[384]: '你有凭有据，再定它的罪也不迟' -> '你有凭有据，再定牠的罪也不迟'",
        "edit: SIMP[389] -> TRAD[389]: '那个金刚圈尺寸太差' -> '那个金刚圈尺吋太差'",
        "edit: SIMP[393] -> TRAD[393]: '它虽然是个猴子' -> '牠虽然是个猴子'",
        "edit: SIMP[394] -> TRAD[394]: '可是你也不能这样对它呀' -> '可是你也不能这样对牠呀'",
        "edit: SIMP[415] -> TRAD[415]: '请你放过悟空，不要伤害牠啦' -> '请你放过悟空，不要伤害他啦'",
        "edit: SIMP[420] -> TRAD[420]: '它总算是我的徒弟' -> '牠总算是我的徒弟'",
        "edit: SIMP[422] -> TRAD[422]: '求观音姐姐放它一条生路吧' -> '求观音姐姐放牠一条生路吧'",
        "edit: SIMP[423] -> TRAD[423]: '我不消灭它' -> '我不消灭牠'",
        "edit: SIMP[453] -> TRAD[453]: '都是你害的，尿什么尿嘛！' -> '都是你害的，尿甚么尿嘛！'",
        "edit: SIMP[470] -> TRAD[470]: '什么事呀？' -> '甚么事呀？'",
        "edit: SIMP[490] -> TRAD[490]: '为什么老是那么猴急呢？你看' -> '为甚么老是那么猴急呢？你看'",
        "edit: SIMP[491] -> TRAD[491]: '他在干什么？' -> '他在干甚么？'",
        "edit: SIMP[503] -> TRAD[503]: '我又不认识你们，拜托不要跟着我们' -> '我又不认识你们 拜托不要跟着我们'",
        "edit: SIMP[509] -> TRAD[509]: '结婚嘛，你哭什么哭？' -> '结婚嘛，你哭甚么哭？'",
        "edit: SIMP[512] -> TRAD[512]: '为什么？' -> '为甚么？'",
        "edit: SIMP[551] -> TRAD[551]: '我当着这么多兄弟的面前向你求婚' -> '我当着这么多兄弟面前向你求婚'",
        "edit: SIMP[556] -> TRAD[556]: '你说什么？' -> '你说甚么？'",
        "edit: SIMP[557] -> TRAD[557]: '让我来，说什么⋯' -> '让我来，说甚么⋯'",
        "edit: SIMP[563] -> TRAD[563]: '有什么规矩啊？' -> '有甚么规矩啊？'",
        "edit: SIMP[574] -> TRAD[574]: '你们这些混蛋在我地盘瞎搞啥？' -> '你们这些混蛋在我地盘瞎搞甚么？'",
        "edit: SIMP[621] -> TRAD[621]: '你们在这儿干什么？' -> '你们在这儿，你干甚么？'",
        "edit: SIMP[669] -> TRAD[669]: '我高你一点罢了没什么大不了的' -> '我高你一点点之嘛，没什么大不了的'",
        "edit: SIMP[682] -> TRAD[682]: '啊，是吗？为什么？\\u3000\\u3000不会走。' -> '啊，是吗？为甚么？\\u3000\\u3000不会走'",
        "edit: SIMP[688] -> TRAD[688]: '我在这监狱里跟在外面有什么分别呢' -> '我在这监狱里跟在外面有甚么分别呢'",
        "edit: SIMP[700] -> TRAD[700]: '师弟呀，收拾它一下' -> '师弟呀，收起它一下'",
        "edit: SIMP[701] -> TRAD[701]: '为什么要我收呀' -> '为甚么要我收呀'",
        "edit: SIMP[709] -> TRAD[709]: '你知不知道什么是当当⋯？' -> '你知不知道甚么是当当⋯？'",
        "edit: SIMP[710] -> TRAD[710]: '什么当当当呀？' -> '甚么当当当呀？'",
        "edit: SIMP[711] -> TRAD[711]: '只有你\\u3000\\u3000能伴我取西经' -> '只有你能伴我取西经'",
        "edit: SIMP[712] -> TRAD[712]: '只有你\\u3000\\u3000能杀妖和除魔' -> '只有你能杀妖和除魔'",
        "edit: SIMP[713] -> TRAD[713]: '只有你\\u3000\\u3000能保护我' -> '只有你能保护我'",
        "edit: SIMP[717] -> TRAD[717]: '戴上〝紧箍儿〞' -> '戴上「紧箍儿」'",
        "edit: SIMP[734] -> TRAD[734]: '师兄，你么带个女人走呀？' -> '师兄，你怎么带个女人走呀？'",
        "edit: SIMP[739] -> TRAD[739]: '干什么？' -> '干甚么？'",
        "edit: SIMP[741] -> TRAD[741]: '一眼就看出来啦，还听什么听？' -> '一眼就看出来啦，还听甚么听？'",
        "edit: SIMP[854] -> TRAD[854]: '闭咀！' -> '闭嘴！'",
        "edit: SIMP[929] -> TRAD[929]: '唉！为什么带我回这个洞来？' -> '唉！为甚么带我回这个洞来？'",
        "edit: SIMP[948] -> TRAD[948]: '什么？' -> '甚么？'",
        "edit: SIMP[959] -> TRAD[959]: '我千辛万苦回来和做的所有事情' -> '我千辛万苦回这里和做的所有事情'",
        "edit: SIMP[997] -> TRAD[997]: '为什么你会死的？' -> '为甚么你会死的？'",
        "edit: SIMP[1005] -> TRAD[1005]: '我〝啪〞的一声回到五百年前' -> '我「嗖」的一声回到五百年前'",
        "edit: SIMP[1024] -> TRAD[1024]: '别用想了，照旧' -> '别瞎用想了，照旧'",
        "edit: SIMP[1025] -> TRAD[1025]: '你搜下面！' -> '你搜下边！'",
        "edit: SIMP[1046] -> TRAD[1046]: '他有什么本事' -> '他有甚么本事'",
        "edit: SIMP[1131] -> TRAD[1131]: '亦传说中的缘份' -> '也许传说中的缘份'",
        "edit: SIMP[1156] -> TRAD[1156]: '他们不认识你师妹的' -> '他们不认识你师妹的。'",
        "edit: SIMP[1171] -> TRAD[1171]: '你说什么？' -> '你说甚么？'",
        "edit: SIMP[1174] -> TRAD[1174]: '我很想看看到底是什么？' -> '我很想看看到底是甚么？'",
        "edit: SIMP[1175] -> TRAD[1175]: '莫名奇妙' -> '莫名其妙'",
        "edit: SIMP[1191] -> TRAD[1191]: '我不想再逗了' -> '我不想再斗了'",
        "edit: SIMP[1193] -> TRAD[1193]: '我这一辈子就你这么一个姐姐' -> '我这辈子就你这么一个姐姐'",
        "edit: SIMP[1208] -> TRAD[1208]: '香香，你干什么？' -> '香香，你干甚么？'",
        "edit: SIMP[1250] -> TRAD[1250]: '为什么仇恨可以大到这种地步？' -> '为甚么仇恨可以大到这种地步？'",
        "edit: SIMP[1330] -> TRAD[1330]: '我的名字叫做齐天大圣' -> '我的名字叫做齐天大⋯圣'",
        "edit: SIMP[1343] -> TRAD[1343]: '为什么你老是⋯不说话呢？' -> '为甚么你老是⋯不说话呢？'",
        "edit: SIMP[1428] -> TRAD[1428]: '一定要靠月光宝盒才能离开这里⋯' -> '一定要靠月光宝盒才能离开这里⋯⋯'",
        "edit: SIMP[1438] -> TRAD[1438]: '发生什么事啊？' -> '发生甚么事啊？'",
        "edit: SIMP[1464] -> TRAD[1464]: '看什么看？' -> '看甚么看？'",
        "edit: SIMP[1477] -> TRAD[1477]: '大师兄啊，你在看什么？' -> '大师兄啊，你在看甚么？'",
        "edit: SIMP[1492] -> TRAD[1492]: '走开吧！三八你看什么？' -> '走开吧！三八你看甚么？'",
        "edit: SIMP[1498] -> TRAD[1498]: '磨豆腐有什么了不起，我也会呀' -> '磨豆腐有甚么了不起，我也会呀'",
        "edit: SIMP[1540] -> TRAD[1540]: '干什么？' -> '干甚么？'",
    ]
