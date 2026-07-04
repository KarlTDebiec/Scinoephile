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
    """Expected differences for ACOPTC Yue Simplified vs Traditional subtitles."""
    return []


@fixture
def acoptc_zho_simplify_expected_series_diff() -> list[str]:
    """Expected differences for ACOPTC Zho Simplified vs Traditional subtitles."""
    return [
        "edit: SIMP[61] -> TRAD[61]: '这个山头所有东西都属于我的' -> '这个山头所有东西都属于我'",
        "edit: SIMP[71] -> TRAD[71]: '你没有变成孙悟空托生' -> '你没有变成孙悟空投世'",
        "edit: SIMP[107] -> TRAD[107]: '还有这个宝盒呢⋯' -> '还有这个宝盒呢⋯我的'",
        "edit: SIMP[186] -> TRAD[186]: '至尊宝？\\u3000玉尊玉？\\u3000想骗我啊？' -> '至尊宝？\\u3000至尊玉？\\u3000想骗我啊？'",
        "edit: SIMP[227] -> TRAD[227]: '这个猪头切不半给我，谢谢' -> '这个猪头切一半给我，谢谢'",
        "edit: SIMP[339] -> TRAD[339]: '乱扔会染污环境！' -> '乱扔会污染环境！'",
        "edit: SIMP[370] -> TRAD[370]: '我为什么要杀它了' -> '我为什么要杀牠了'",
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
        "edit: SIMP[431] -> TRAD[431]: '我这样做，\\u3000无非是想感化劣徒' -> '我这样做，无非是想感化劣徒'",
        "edit: SIMP[504] -> TRAD[504]: '师傅能够见到你真好了' -> '师父能够见到你真好了'",
        "edit: SIMP[551] -> TRAD[551]: '我当着这么多兄弟的面前向你求婚' -> '我当着这么多兄弟面前向你求婚'",
        "edit: SIMP[574] -> TRAD[574]: '你们这些混蛋在我地盘瞎搞啥？' -> '你们这些混蛋在我地盘瞎搞什么？'",
        "edit: SIMP[669] -> TRAD[669]: '我高你一点罢了没什么大不了的' -> '我高你一点之嘛没什么大不了的'",
        "edit: SIMP[700] -> TRAD[700]: '师弟呀，收拾它一下' -> '师弟呀，收起它一下'",
        "edit: SIMP[734] -> TRAD[734]: '师兄，你么带个女人走呀？' -> '师兄，你怎么带个女人走呀？'",
        "edit: SIMP[854] -> TRAD[854]: '闭咀！' -> '闭嘴！'",
        "edit: SIMP[959] -> TRAD[959]: '我千辛万苦回来和做的所有事情' -> '我千辛万苦回这里和做的所有事情'",
        "edit: SIMP[1005] -> TRAD[1005]: '我〝啪〞的一声回到五百年前' -> '我〝超〞的一声回到五百年前'",
        "edit: SIMP[1024] -> TRAD[1024]: '别用想了，照旧' -> '别瞎用想了，照旧'",
        "edit: SIMP[1025] -> TRAD[1025]: '你搜下面！' -> '你搜下边！'",
        "edit: SIMP[1131] -> TRAD[1131]: '亦传说中的缘份' -> '也许传说中的缘份'",
        "edit: SIMP[1175] -> TRAD[1175]: '莫名奇妙' -> '莫名其妙'",
        "edit: SIMP[1191] -> TRAD[1191]: '我不想再逗了' -> '我不想再斗了'",
        "edit: SIMP[1193] -> TRAD[1193]: '我这一辈子就你这么一个姐姐' -> '我这辈子就你这么一个姐姐'",
        "edit: SIMP[1330] -> TRAD[1330]: '我的名字叫做齐天大圣' -> '我的名字叫做齐天大⋯圣'",
        "edit: SIMP[1428] -> TRAD[1428]: '一定要靠月光宝盒才能离开这里． ．⋯' -> '一定要靠月光宝盒才能离开这里． ．⋯⋯'",
    ]
