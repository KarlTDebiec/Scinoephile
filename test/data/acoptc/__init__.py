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
    """ACOPTC zho-Hans subtitles."""
    return Series.load(input_path / "zho-Hans.srt")


@fixture
def acoptc_zho_hant() -> Series:
    """ACOPTC zho-Hant subtitles."""
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
    """Get ACOPTC yue-Hans block review test cases.

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
    """Get ACOPTC yue-Hans OCR fusion test cases.

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
    """Get ACOPTC yue-Hant block review test cases.

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
    """Get ACOPTC yue-Hant OCR fusion test cases.

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
    """Get ACOPTC yue-Hant simplification block review test cases.

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
    """Get ACOPTC zho-Hans block review test cases.

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
    """Get ACOPTC zho-Hans OCR fusion test cases.

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
    """Get ACOPTC zho-Hant block review test cases.

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
    """Get ACOPTC zho-Hant OCR fusion test cases.

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
    """Get ACOPTC zho-Hant simplification block review test cases.

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
    """ACOPTC bilingual yue-Hans and English subtitles."""
    return Series.load(output_dir / "yue-Hans_eng.srt")


@fixture
def acoptc_yue_hans_ocr_fuse() -> Series:
    """ACOPTC yue-Hans fused subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse.srt")


@fixture
def acoptc_yue_hans_ocr_fuse_clean() -> Series:
    """ACOPTC yue-Hans fused and cleaned subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean.srt")


@fixture
def acoptc_yue_hans_ocr_fuse_clean_validate() -> Series:
    """ACOPTC yue-Hans fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean_validate.srt")


@fixture
def acoptc_yue_hans_ocr_fuse_clean_validate_review() -> Series:
    """ACOPTC yue-Hans fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean_validate_review.srt")


@fixture
def acoptc_yue_hans_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPTC yue-Hans fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acoptc_yue_hans_ocr_fuse_clean_validate_review_flatten_romanize() -> Series:
    """ACOPTC yue-Hans fused/cleaned/validated/reviewed/flattened romanized subtitles."""
    return Series.load(
        output_dir / "yue-Hans_ocr/fuse_clean_validate_review_flatten_romanize.srt"
    )


@fixture
def acoptc_yue_hans_ocr_lens() -> Series:
    """ACOPTC yue-Hans subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "yue-Hans_ocr/lens.srt")


@fixture
def acoptc_yue_hans_ocr_lens_clean() -> Series:
    """ACOPTC yue-Hans Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hans_ocr/lens_clean.srt")


@fixture
def acoptc_yue_hans_ocr_paddle() -> Series:
    """ACOPTC yue-Hans subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "yue-Hans_ocr/paddle.srt")


@fixture
def acoptc_yue_hans_ocr_paddle_clean() -> Series:
    """ACOPTC yue-Hans PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hans_ocr/paddle_clean.srt")


@fixture
def acoptc_yue_hant_ocr_fuse() -> Series:
    """ACOPTC yue-Hant fused subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse.srt")


@fixture
def acoptc_yue_hant_ocr_fuse_clean() -> Series:
    """ACOPTC yue-Hant fused and cleaned subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean.srt")


@fixture
def acoptc_yue_hant_ocr_fuse_clean_validate() -> Series:
    """ACOPTC yue-Hant fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean_validate.srt")


@fixture
def acoptc_yue_hant_ocr_fuse_clean_validate_review() -> Series:
    """ACOPTC yue-Hant fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean_validate_review.srt")


@fixture
def acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPTC yue-Hant fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify() -> Series:
    """ACOPTC yue-Hant simplified fused/cleaned/validated/reviewed/flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hant_ocr" / "fuse_clean_validate_review_flatten_simplify.srt"
    )


@fixture
def acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """ACOPTC yue-Hant simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "yue-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@fixture
def acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize() -> (
    Series
):
    """ACOPTC yue-Hant simplified/reviewed fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir
        / "yue-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
    )


@fixture
def acoptc_yue_hant_ocr_lens() -> Series:
    """ACOPTC yue-Hant subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "yue-Hant_ocr/lens.srt")


@fixture
def acoptc_yue_hant_ocr_lens_clean() -> Series:
    """ACOPTC yue-Hant Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hant_ocr/lens_clean.srt")


@fixture
def acoptc_yue_hant_ocr_paddle() -> Series:
    """ACOPTC yue-Hant subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "yue-Hant_ocr/paddle.srt")


@fixture
def acoptc_yue_hant_ocr_paddle_clean() -> Series:
    """ACOPTC yue-Hant PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hant_ocr/paddle_clean.srt")


@fixture
def acoptc_zho_hans_eng() -> Series:
    """ACOPTC bilingual zho-Hans and English subtitles."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


@fixture
def acoptc_zho_hans_ocr_fuse() -> Series:
    """ACOPTC zho-Hans fused subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse.srt")


@fixture
def acoptc_zho_hans_ocr_fuse_clean() -> Series:
    """ACOPTC zho-Hans fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean.srt")


@fixture
def acoptc_zho_hans_ocr_fuse_clean_validate() -> Series:
    """ACOPTC zho-Hans fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate.srt")


@fixture
def acoptc_zho_hans_ocr_fuse_clean_validate_review() -> Series:
    """ACOPTC zho-Hans fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate_review.srt")


@fixture
def acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPTC zho-Hans fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten_romanize() -> Series:
    """ACOPTC zho-Hans fused/cleaned/validated/reviewed/flattened romanized subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten_romanize.srt"
    )


@fixture
def acoptc_zho_hans_ocr_lens() -> Series:
    """ACOPTC zho-Hans subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hans_ocr/lens.srt")


@fixture
def acoptc_zho_hans_ocr_lens_clean() -> Series:
    """ACOPTC zho-Hans Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/lens_clean.srt")


@fixture
def acoptc_zho_hans_ocr_paddle() -> Series:
    """ACOPTC zho-Hans subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle.srt")


@fixture
def acoptc_zho_hans_ocr_paddle_clean() -> Series:
    """ACOPTC zho-Hans PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle_clean.srt")


@fixture
def acoptc_zho_hant_ocr_fuse() -> Series:
    """ACOPTC zho-Hant fused subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse.srt")


@fixture
def acoptc_zho_hant_ocr_fuse_clean() -> Series:
    """ACOPTC zho-Hant fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean.srt")


@fixture
def acoptc_zho_hant_ocr_fuse_clean_validate() -> Series:
    """ACOPTC zho-Hant fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate.srt")


@fixture
def acoptc_zho_hant_ocr_fuse_clean_validate_review() -> Series:
    """ACOPTC zho-Hant fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate_review.srt")


@fixture
def acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPTC zho-Hant fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify() -> Series:
    """ACOPTC zho-Hant simplified fused/cleaned/validated/reviewed/flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr" / "fuse_clean_validate_review_flatten_simplify.srt"
    )


@fixture
def acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """ACOPTC zho-Hant simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@fixture
def acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize() -> (
    Series
):
    """ACOPTC zho-Hant simplified/reviewed fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
    )


@fixture
def acoptc_zho_hant_ocr_lens() -> Series:
    """ACOPTC zho-Hant subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hant_ocr/lens.srt")


@fixture
def acoptc_zho_hant_ocr_lens_clean() -> Series:
    """ACOPTC zho-Hant Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/lens_clean.srt")


@fixture
def acoptc_zho_hant_ocr_paddle() -> Series:
    """ACOPTC zho-Hant subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle.srt")


@fixture
def acoptc_zho_hant_ocr_paddle_clean() -> Series:
    """ACOPTC zho-Hant PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle_clean.srt")


@fixture
def acoptc_yue_simplify_expected_series_diff() -> list[str]:
    """Expected differences for ACOPTC subtitles."""
    return [
        "edit: SIMP[7] -> TRAD[7]: '净系得啲油，都冇灯芯' -> '净系得啲油，都有灯芯'",
        "edit: SIMP[54] -> TRAD[54]: '你〝虾〞我唔识字呀！' -> '你“虾”我唔识字呀！'",
        "edit: SIMP[87] -> TRAD[87]: '有了呢个月光宝盒呢' -> '有咗呢个月光宝盒呢'",
        "edit: SIMP[151] -> TRAD[151]: '坐低' -> '坐下'",
        "edit: SIMP[203] -> TRAD[203]: '你攞我嗰把紫青宝剑俾佢睇' -> '你摆我嗰把紫青宝剑俾佢睇'",
        "edit: SIMP[283] -> TRAD[283]: '你“抄”吓佢吖喂\\u3000\\u3000嚟呀' -> '你「锄」吓佢吖喂\\u3000\\u3000嚟呀'",
        "edit: SIMP[302] -> TRAD[302]: '天黑嘞，我避开家姐啊' -> '天黑了，我避开家姐呀'",
        "edit: SIMP[329] -> TRAD[329]: '我教你好多次唔好乱咁掟嘢' -> '我教你好多次唔好乱咁扔嘢'",
        "edit: SIMP[331] -> TRAD[331]: '话口未完，连支棍都揼埋' -> '话口未完，连支棍都扔埋'",
        "edit: SIMP[335] -> TRAD[335]: '好容易掟亲啲小朋友' -> '好容易扔亲啲小朋友'",
        "edit: SIMP[336] -> TRAD[336]: '就算冇小朋友，掟亲啲花花草草都唔好嘅' -> '就算冇小朋友，扔亲啲花花草草都唔好嘅'",
        "edit: SIMP[361] -> TRAD[361]: '〝必〞佢条肠出嚟' -> '〝劏〞佢条肠出嚟'",
        "edit: SIMP[380] -> TRAD[380]: '唐三藏，你烦我一早听讲过嘞' -> '唐三藏，你烦我一早听讲过啦'",
        "edit: SIMP[438] -> TRAD[438]: '你有冇“嬲”多件衫？！' -> '你有冇「嬲」多件衫？！'",
        "edit: SIMP[445] -> TRAD[445]: '一日最衰系你，痾咩嘢尿呢？' -> '一日最衰系你，屙咩嘢尿呢？'",
        "edit: SIMP[447] -> TRAD[447]: '病尿都叽拮' -> '屙尿都叽拮'",
        "edit: SIMP[452] -> TRAD[452]: '系你条木契' -> '系你条蠢契'",
        "edit: SIMP[551] -> TRAD[551]: '几时轮到你〝咋〞鸦乌嚟反对啫？' -> '几时轮到你〝咋〞鸦鸟嚟反对啫？'",
        "edit: SIMP[561] -> TRAD[561]: '呢个祗不过系我同大家开嘅一个玩笑' -> '呢个祇不过系我同大家开嘅一个玩笑'",
        "edit: SIMP[565] -> TRAD[565]: '你班冚家铲喺我地头搅搅阵⋯' -> '你班冚家铲喺我地头搅搅震⋯'",
        "edit: SIMP[575] -> TRAD[575]: '但系这一个，我认为是讲得最完美的！' -> '但系这一个，我认为系讲得最完美的！'",
        "edit: SIMP[578] -> TRAD[578]: '曾经有一份至真的爱情摆在我面前，我没珍惜' -> '曾经有一份至真的爱情摆在我面前，我冇珍惜'",
        "edit: SIMP[579] -> TRAD[579]: '到没了的时候，先至后悔莫及' -> '到冇了的时候，先至后悔莫及'",
        "edit: SIMP[581] -> TRAD[581]: '你把东西在我喉咙度拖落去啦，不需要犹疑啦！' -> '你把东西在我喉咙度拖落去啦，唔需要犹疑啦！'",
        "edit: SIMP[585] -> TRAD[585]: '如果是都要在呢份爱加上一个期限' -> '如果系都要在呢份爱加上一个期限'",
        "edit: SIMP[586] -> TRAD[586]: '我希望是一万年' -> '我希望系一万年'",
        "edit: SIMP[699] -> TRAD[699]: 'Only you， 能杀妖精鬼怪' -> 'Only you，能杀妖精鬼怪'",
        "edit: SIMP[700] -> TRAD[700]: 'Only you， 能保护我' -> 'Only you，能保护我'",
        "edit: SIMP[702] -> TRAD[702]: '只有你咁劲，就是 Only you' -> '只有你咁劲，就是Only you'",
        "edit: SIMP[705] -> TRAD[705]: '莫怕死，咪发 \"t i\" 藤' -> '莫怕死，咪发〞t i〞藤'",
        "edit: SIMP[706] -> TRAD[706]: '碰到钉咪惊，I under stand' -> '碰到钉咪惊，I understand'",
        "edit: SIMP[707] -> TRAD[707]: '要全力地去 do，要惊就两份惊' -> '要全力地去do，要惊就两份惊'",
        "edit: SIMP[723] -> TRAD[723]: '叫你们在三百里外大树林等佢' -> '叫你们在三百里外大树林等他'",
        "edit: SIMP[820] -> TRAD[820]: '你攞个月光宝盒做咩呀？' -> '你摆个月光宝盒做咩呀？'",
        "edit: SIMP[853] -> TRAD[853]: '你拿返都有用呀' -> '你攞返都冇用呀'",
        "edit: SIMP[885] -> TRAD[885]: '算啦，我都系返火焰山' -> '算啦，我都系返火燄山'",
        "edit: SIMP[921] -> TRAD[921]: '阿紫霞仅是挣你好多钱' -> '阿紫霞竟系赚你好多钱'",
        "edit: SIMP[928] -> TRAD[928]: '晶晶，见番你真系好！' -> '晶晶，见返你真系好！'",
        "edit: SIMP[961] -> TRAD[961]: '你仲要冲埋嚟系咁赵，系咁赵' -> '你仲要冲埋嚟系咁趟，系咁赵'",
        "edit: SIMP[962] -> TRAD[962]: '唔咪⋯咪咁赵，咁赵，赵呀⋯⋯' -> '唔咪⋯咪咁趟，咁赵，赵呀⋯⋯'",
        "edit: SIMP[975] -> TRAD[975]: '换来祗系无穷无尽嘅痛苦同埋唏嘘！' -> '换嚟只系无穷无尽嘅痛苦同埋唏嘘！'",
        "edit: SIMP[984] -> TRAD[984]: '我“卓”一声返番嚟五百年之前' -> '我‘卓’一声返番嚟五百年之前'",
        "edit: SIMP[1003] -> TRAD[1003]: '唔使谂啦，照旧呀' -> '唔驶谂啦，照旧呀'",
        "edit: SIMP[1004] -> TRAD[1004]: '你“抄”下面！' -> '你「抄」下面！'",
        "edit: SIMP[1005] -> TRAD[1005]: '多谢晒你呀椰青！' -> '多谢哂你呀椰青！'",
        "edit: SIMP[1008] -> TRAD[1008]: '一日到黑“裸”住要月光宝盒' -> '一日到黑「攞」住要月光宝盒'",
        "edit: SIMP[1020] -> TRAD[1020]: '我骗他吗' -> '我骗佢吗'",
        "edit: SIMP[1059] -> TRAD[1059]: '人与人之间嘅一些微妙感情啫' -> '人与人之间嘅一啲微妙感情啫'",
        "edit: SIMP[1063] -> TRAD[1063]: '省啲啦你！瞓啦！' -> '悭啲啦你！瞓啦！'",
        "edit: SIMP[1164] -> TRAD[1164]: '我唔想斗啦' -> '我唔想鬥啦'",
        "edit: SIMP[1166] -> TRAD[1166]: '呢世女我得你一个姐姐架啫' -> '呢世女我得你一个姐姐㗎啫'",
        "edit: SIMP[1271] -> TRAD[1271]: '呢个乞嚏一定令到大家好失望' -> '呢个乞丐一定令到大家好失望'",
        "edit: SIMP[1323] -> TRAD[1323]: '蚁多搂死象' -> '蚁多咬死象'",
        "edit: SIMP[1324] -> TRAD[1324]: '无敌牛虻' -> '无敌牛仔'",
        "edit: SIMP[1329] -> TRAD[1329]: '齐天大圣孙悟空啊？' -> '齐天大圣孙悟空啊，呵？'",
        "edit: SIMP[1359] -> TRAD[1359]: '舍得埋嚟啦吗？' -> '舍得埋嚟啦咩？'",
        "edit: SIMP[1392] -> TRAD[1392]: '我凄' -> '我妻'",
        "edit: SIMP[1424] -> TRAD[1424]: '相传五百年前呢度就系水濂洞' -> '相传五百年前呢度就系水帘洞'",
        "edit: SIMP[1440] -> TRAD[1440]: '〝队〞多我三嘢添' -> '“队”多我三嘢添'",
        "edit: SIMP[1443] -> TRAD[1443]: '条友叫我〝队〞佢三嘢系咪前世欠咗我㗎' -> '条友叫我“队”佢三嘢系咪前世欠咗我㗎'",
        "edit: SIMP[1447] -> TRAD[1447]: '俾两砖豆腐我呀' -> '畀两砖豆腐我呀'",
    ]


@fixture
def acoptc_zho_simplify_expected_series_diff() -> list[str]:
    """Expected differences for ACOPTC subtitles."""
    return [
        "edit: SIMP[3] -> TRAD[3]: '耽搁大家一会，很快就点着了' -> '担搁大家一会儿，很快就点着了'",
        "edit: SIMP[8] -> TRAD[8]: '可是灯芯不见了，有什么办法呢？' -> '可是灯芯不见了，有甚么办法呢？'",
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
        "edit: SIMP[343] -> TRAD[343]: '你干什么？' -> '你干甚么？'",
        "edit: SIMP[370] -> TRAD[370]: '我为什么要杀它了' -> '我为甚么要杀它了'",
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
        "edit: SIMP[504] -> TRAD[504]: '师傅能够见到你真好了' -> '师傅，能够见到你真好了'",
        "edit: SIMP[509] -> TRAD[509]: '结婚嘛，你哭什么哭？' -> '结婚嘛，你哭甚么哭？'",
        "edit: SIMP[512] -> TRAD[512]: '为什么？' -> '为甚么？'",
        "edit: SIMP[520] -> TRAD[520]: '牛大哥你能说你怎么认识' -> '牛大哥，你能说你怎么认识'",
        "edit: SIMP[529] -> TRAD[529]: '来⋯我来介绍我妹妹和妹夫给你认识' -> '来⋯我来介绍我妹妹和妹夫给你认识。'",
        "edit: SIMP[551] -> TRAD[551]: '我当着这么多兄弟的面前向你求婚' -> '我当着这么多兄弟面前向你求婚'",
        "edit: SIMP[556] -> TRAD[556]: '你说什么？' -> '你说甚么？'",
        "edit: SIMP[557] -> TRAD[557]: '让我来，说什么⋯' -> '让我来，说甚么⋯'",
        "edit: SIMP[563] -> TRAD[563]: '有什么规矩啊？' -> '有甚么规矩啊？'",
        "edit: SIMP[574] -> TRAD[574]: '你们这些混蛋在我地盘瞎搞啥？' -> '你们这些混蛋在我地盘瞎搞甚么？'",
        "edit: SIMP[621] -> TRAD[621]: '你们在这儿干什么？' -> '你们在这儿干甚么？'",
        "edit: SIMP[669] -> TRAD[669]: '我高你一点罢了没什么大不了的' -> '我高你一点点之嘛，没什么大不了的'",
        "edit: SIMP[682] -> TRAD[682]: '啊，是吗？为什么？\\u3000\\u3000不会走。' -> '啊，是吗？为甚么？\\u3000\\u3000不会走'",
        "edit: SIMP[688] -> TRAD[688]: '我在这监狱里跟在外面有什么分别呢' -> '我在这监狱里跟在外面有甚么分别呢'",
        "edit: SIMP[700] -> TRAD[700]: '师弟呀，收拾它一下' -> '师弟呀，收起它一下'",
        "edit: SIMP[701] -> TRAD[701]: '为什么要我收呀' -> '为甚么要我收呀'",
        "edit: SIMP[709] -> TRAD[709]: '你知不知道什么是当当⋯？' -> '你知不知道甚么是当当⋯？'",
        "edit: SIMP[710] -> TRAD[710]: '什么当当当呀？' -> '甚么当当当呀？'",
        "edit: SIMP[717] -> TRAD[717]: '戴上“紧箍儿”' -> '戴上「紧箍儿」'",
        "edit: SIMP[739] -> TRAD[739]: '干什么？' -> '干甚么？'",
        "edit: SIMP[741] -> TRAD[741]: '一眼就看出来啦，还听什么听？' -> '一眼就看出来啦，还听甚么听？'",
        "edit: SIMP[929] -> TRAD[929]: '唉！为什么带我回这个洞来？' -> '唉！为甚么带我回这个洞来？'",
        "edit: SIMP[948] -> TRAD[948]: '什么？' -> '甚么？'",
        "edit: SIMP[959] -> TRAD[959]: '我千辛万苦回来和做的所有事情' -> '我千辛万苦回这里做的所有事情'",
        "edit: SIMP[997] -> TRAD[997]: '为什么你会死的？' -> '为甚么你会死的？'",
        "edit: SIMP[1005] -> TRAD[1005]: '我〝啪〞的一声回到五百年前' -> '我『嗖』的一声回到五百年前'",
        "edit: SIMP[1024] -> TRAD[1024]: '别用想了，照旧' -> '别瞎用想了，照旧'",
        "edit: SIMP[1025] -> TRAD[1025]: '你搜下面！' -> '你搜下边！'",
        "edit: SIMP[1046] -> TRAD[1046]: '他有什么本事' -> '他有甚么本事'",
        "edit: SIMP[1127] -> TRAD[1127]: '当我见到她在你良心留下的东西之后' -> '当我见到她在你良心里留下的东西之后'",
        "edit: SIMP[1131] -> TRAD[1131]: '亦传说中的缘份' -> '也就是传说中的缘分'",
        "edit: SIMP[1171] -> TRAD[1171]: '你说什么？' -> '你说甚么？'",
        "edit: SIMP[1174] -> TRAD[1174]: '我很想看看到底是什么？' -> '我很想看看到底是甚么？'",
        "edit: SIMP[1175] -> TRAD[1175]: '莫名奇妙' -> '莫名其妙'",
        "edit: SIMP[1191] -> TRAD[1191]: '我不想再逗了' -> '我不想再斗了'",
        "edit: SIMP[1193] -> TRAD[1193]: '我这一辈子就你这么一个姐姐' -> '我这一世就你这么一个姐姐'",
        "edit: SIMP[1208] -> TRAD[1208]: '香香，你干什么？' -> '香香，你干甚么？'",
        "edit: SIMP[1250] -> TRAD[1250]: '为什么仇恨可以大到这种地步？' -> '为甚么仇恨可以大到这种地步？'",
        "edit: SIMP[1330] -> TRAD[1330]: '我的名字叫做齐天大圣' -> '我的名字叫做齐天大⋯⋯圣'",
        "edit: SIMP[1343] -> TRAD[1343]: '为什么你老是⋯不说话呢？' -> '为甚么你老是⋯不说话呢？'",
        "edit: SIMP[1428] -> TRAD[1428]: '一定要靠月光宝盒才能离开这里...' -> '一定要靠月光宝盒才能离开这里⋯⋯'",
        "edit: SIMP[1438] -> TRAD[1438]: '发生什么事啊？' -> '发生甚么事啊？'",
        "edit: SIMP[1443] -> TRAD[1443]: '上哪去师父？' -> '上那儿去，师父？'",
        "edit: SIMP[1464] -> TRAD[1464]: '看什么看？' -> '看甚么看？'",
        "edit: SIMP[1465] -> TRAD[1465]: '你的装是恶心嘛' -> '你的装扮恶心嘛'",
        "edit: SIMP[1477] -> TRAD[1477]: '大师兄啊，你在看什么？' -> '大师兄啊，你在看甚么？'",
        "edit: SIMP[1492] -> TRAD[1492]: '走开吧！三八你看什么？' -> '走开吧！三八你看甚么？'",
        "edit: SIMP[1498] -> TRAD[1498]: '磨豆腐有什么了不起，我也会呀' -> '磨豆腐有甚么了不起，我也会呀'",
        "edit: SIMP[1540] -> TRAD[1540]: '干什么？' -> '干甚么？'",
    ]
