#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for TMM."""

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
from scinoephile.llms.block_review import BlockReviewManager, BlockReviewPrompt
from scinoephile.llms.dual_1_to_1 import Dual1To1Prompt
from scinoephile.llms.dual_1_to_1.ocr_fusion import OcrFusionManager
from test.helpers import test_data_root

__all__ = [
    "get_tmm_eng_block_review_test_cases",
    "get_tmm_eng_ocr_fusion_test_cases",
    "get_tmm_yue_hans_block_review_test_cases",
    "get_tmm_yue_hans_ocr_fusion_test_cases",
    "get_tmm_yue_hant_block_review_test_cases",
    "get_tmm_yue_hant_ocr_fusion_test_cases",
    "get_tmm_yue_hant_simplify_block_review_test_cases",
    "get_tmm_zho_hans_block_review_test_cases",
    "get_tmm_zho_hans_ocr_fusion_test_cases",
    "get_tmm_zho_hant_block_review_test_cases",
    "get_tmm_zho_hant_ocr_fusion_test_cases",
    "get_tmm_zho_hant_simplify_block_review_test_cases",
    "tmm_eng_ocr_fuse",
    "tmm_eng_ocr_fuse_clean",
    "tmm_eng_ocr_fuse_clean_validate",
    "tmm_eng_ocr_fuse_clean_validate_review",
    "tmm_eng_ocr_fuse_clean_validate_review_flatten",
    "tmm_eng_ocr_lens",
    "tmm_eng_ocr_lens_clean",
    "tmm_eng_ocr_tesseract",
    "tmm_eng_ocr_tesseract_clean",
    "tmm_yue_hans_eng",
    "tmm_yue_hans_ocr_fuse",
    "tmm_yue_hans_ocr_fuse_clean",
    "tmm_yue_hans_ocr_fuse_clean_validate",
    "tmm_yue_hans_ocr_fuse_clean_validate_review",
    "tmm_yue_hans_ocr_fuse_clean_validate_review_flatten",
    "tmm_yue_hans_ocr_fuse_clean_validate_review_flatten_romanize",
    "tmm_yue_hans_ocr_lens",
    "tmm_yue_hans_ocr_lens_clean",
    "tmm_yue_hans_ocr_paddle",
    "tmm_yue_hans_ocr_paddle_clean",
    "tmm_yue_hant_ocr_fuse",
    "tmm_yue_hant_ocr_fuse_clean",
    "tmm_yue_hant_ocr_fuse_clean_validate",
    "tmm_yue_hant_ocr_fuse_clean_validate_review",
    "tmm_yue_hant_ocr_fuse_clean_validate_review_flatten",
    "tmm_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify",
    "tmm_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
    "tmm_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
    "tmm_yue_hant_ocr_lens",
    "tmm_yue_hant_ocr_lens_clean",
    "tmm_yue_hant_ocr_paddle",
    "tmm_yue_hant_ocr_paddle_clean",
    "tmm_zho_hans_eng",
    "tmm_zho_hans_ocr_fuse",
    "tmm_zho_hans_ocr_fuse_clean",
    "tmm_zho_hans_ocr_fuse_clean_validate",
    "tmm_zho_hans_ocr_fuse_clean_validate_review",
    "tmm_zho_hans_ocr_fuse_clean_validate_review_flatten",
    "tmm_zho_hans_ocr_fuse_clean_validate_review_flatten_romanize",
    "tmm_zho_hans_ocr_lens",
    "tmm_zho_hans_ocr_lens_clean",
    "tmm_zho_hans_ocr_paddle",
    "tmm_zho_hans_ocr_paddle_clean",
    "tmm_zho_hant_ocr_fuse",
    "tmm_zho_hant_ocr_fuse_clean",
    "tmm_zho_hant_ocr_fuse_clean_validate",
    "tmm_zho_hant_ocr_fuse_clean_validate_review",
    "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten",
    "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
    "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
    "tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
    "tmm_zho_simplify_expected_series_diff",
    "tmm_yue_simplify_expected_series_diff",
    "tmm_zho_hant_ocr_lens",
    "tmm_zho_hant_ocr_lens_clean",
    "tmm_zho_hant_ocr_paddle",
    "tmm_zho_hant_ocr_paddle_clean",
]

title_root = test_data_root / Path(__file__).parent.name
output_dir = title_root / "output"


@cache
def get_tmm_eng_block_review_test_cases(
    prompt_cls: type[BlockReviewPrompt] = BlockReviewPromptEng,
    **kwargs: Any,
) -> list[TestCase]:
    """Get TMM English block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "eng_ocr/lang/eng/block_review.json"
    return load_test_cases_from_json(
        path, BlockReviewManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_tmm_eng_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptEng,
    **kwargs: Any,
) -> list[TestCase]:
    """Get TMM English OCR fusion test cases.

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
def get_tmm_yue_hans_block_review_test_cases(
    prompt_cls: type[BlockReviewPrompt] = BlockReviewPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get TMM yue-Hans block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hans_ocr/lang/yue/block_review.json"
    return load_test_cases_from_json(
        path, BlockReviewManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_tmm_yue_hans_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get TMM yue-Hans OCR fusion test cases.

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
def get_tmm_yue_hant_block_review_test_cases(
    prompt_cls: type[BlockReviewPrompt] = BlockReviewPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get TMM yue-Hant block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hant_ocr/lang/yue/block_review.json"
    return load_test_cases_from_json(
        path, BlockReviewManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_tmm_yue_hant_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get TMM yue-Hant OCR fusion test cases.

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
def get_tmm_yue_hant_simplify_block_review_test_cases(
    prompt_cls: type[BlockReviewPrompt] = BlockReviewPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get TMM yue-Hant simplification block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hant_ocr/lang/yue/simplify_block_review.json"
    return load_test_cases_from_json(
        path, BlockReviewManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_tmm_zho_hans_block_review_test_cases(
    prompt_cls: type[BlockReviewPrompt] = BlockReviewPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get TMM zho-Hans block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hans_ocr/lang/zho/block_review.json"
    return load_test_cases_from_json(
        path, BlockReviewManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_tmm_zho_hans_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get TMM zho-Hans OCR fusion test cases.

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
def get_tmm_zho_hant_block_review_test_cases(
    prompt_cls: type[BlockReviewPrompt] = BlockReviewPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get TMM zho-Hant block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/block_review.json"
    return load_test_cases_from_json(
        path, BlockReviewManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_tmm_zho_hant_ocr_fusion_test_cases(
    prompt_cls: type[Dual1To1Prompt] = OcrFusionPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get TMM zho-Hant OCR fusion test cases.

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
def get_tmm_zho_hant_simplify_block_review_test_cases(
    prompt_cls: type[BlockReviewPrompt] = BlockReviewPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get TMM zho-Hant simplification block review test cases.

    Arguments:
        prompt_cls: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/simplify_block_review.json"
    return load_test_cases_from_json(
        path, BlockReviewManager, prompt_cls=prompt_cls, **kwargs
    )


@fixture
def tmm_eng_ocr_fuse() -> Series:
    """TMM English fused subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse.srt")


@fixture
def tmm_eng_ocr_fuse_clean() -> Series:
    """TMM English fused and cleaned subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean.srt")


@fixture
def tmm_eng_ocr_fuse_clean_validate() -> Series:
    """TMM English fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate.srt")


@fixture
def tmm_eng_ocr_fuse_clean_validate_review() -> Series:
    """TMM English fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate_review.srt")


@fixture
def tmm_eng_ocr_fuse_clean_validate_review_flatten() -> Series:
    """TMM English fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate_review_flatten.srt")


@fixture
def tmm_eng_ocr_lens() -> Series:
    """TMM English subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "eng_ocr/lens.srt")


@fixture
def tmm_eng_ocr_lens_clean() -> Series:
    """TMM English Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "eng_ocr/lens_clean.srt")


@fixture
def tmm_eng_ocr_tesseract() -> Series:
    """TMM English subtitles OCRed using Tesseract."""
    return Series.load(output_dir / "eng_ocr/tesseract.srt")


@fixture
def tmm_eng_ocr_tesseract_clean() -> Series:
    """TMM English Tesseract OCR subtitles, cleaned."""
    return Series.load(output_dir / "eng_ocr/tesseract_clean.srt")


@fixture
def tmm_yue_hans_eng() -> Series:
    """TMM bilingual yue-Hans and English subtitles."""
    return Series.load(output_dir / "yue-Hans_eng.srt")


@fixture
def tmm_yue_hans_ocr_fuse() -> Series:
    """TMM yue-Hans fused subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse.srt")


@fixture
def tmm_yue_hans_ocr_fuse_clean() -> Series:
    """TMM yue-Hans fused and cleaned subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean.srt")


@fixture
def tmm_yue_hans_ocr_fuse_clean_validate() -> Series:
    """TMM yue-Hans fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean_validate.srt")


@fixture
def tmm_yue_hans_ocr_fuse_clean_validate_review() -> Series:
    """TMM yue-Hans fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean_validate_review.srt")


@fixture
def tmm_yue_hans_ocr_fuse_clean_validate_review_flatten() -> Series:
    """TMM yue-Hans fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def tmm_yue_hans_ocr_fuse_clean_validate_review_flatten_romanize() -> Series:
    """TMM yue-Hans fused/cleaned/validated/reviewed/flattened romanized subtitles."""
    return Series.load(
        output_dir / "yue-Hans_ocr/fuse_clean_validate_review_flatten_romanize.srt"
    )


@fixture
def tmm_yue_hans_ocr_lens() -> Series:
    """TMM yue-Hans subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "yue-Hans_ocr/lens.srt")


@fixture
def tmm_yue_hans_ocr_lens_clean() -> Series:
    """TMM yue-Hans Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hans_ocr/lens_clean.srt")


@fixture
def tmm_yue_hans_ocr_paddle() -> Series:
    """TMM yue-Hans subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "yue-Hans_ocr/paddle.srt")


@fixture
def tmm_yue_hans_ocr_paddle_clean() -> Series:
    """TMM yue-Hans PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hans_ocr/paddle_clean.srt")


@fixture
def tmm_yue_hant_ocr_fuse() -> Series:
    """TMM yue-Hant fused subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse.srt")


@fixture
def tmm_yue_hant_ocr_fuse_clean() -> Series:
    """TMM yue-Hant fused and cleaned subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean.srt")


@fixture
def tmm_yue_hant_ocr_fuse_clean_validate() -> Series:
    """TMM yue-Hant fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean_validate.srt")


@fixture
def tmm_yue_hant_ocr_fuse_clean_validate_review() -> Series:
    """TMM yue-Hant fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean_validate_review.srt")


@fixture
def tmm_yue_hant_ocr_fuse_clean_validate_review_flatten() -> Series:
    """TMM yue-Hant fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def tmm_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify() -> Series:
    """TMM yue-Hant simplified fused/cleaned/validated/reviewed/flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hant_ocr" / "fuse_clean_validate_review_flatten_simplify.srt"
    )


@fixture
def tmm_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """TMM yue-Hant simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "yue-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@fixture
def tmm_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize() -> (
    Series
):
    """TMM yue-Hant simplified/reviewed fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir
        / "yue-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
    )


@fixture
def tmm_yue_hant_ocr_lens() -> Series:
    """TMM yue-Hant subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "yue-Hant_ocr/lens.srt")


@fixture
def tmm_yue_hant_ocr_lens_clean() -> Series:
    """TMM yue-Hant Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hant_ocr/lens_clean.srt")


@fixture
def tmm_yue_hant_ocr_paddle() -> Series:
    """TMM yue-Hant subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "yue-Hant_ocr/paddle.srt")


@fixture
def tmm_yue_hant_ocr_paddle_clean() -> Series:
    """TMM yue-Hant PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hant_ocr/paddle_clean.srt")


@fixture
def tmm_zho_hans_eng() -> Series:
    """TMM bilingual zho-Hans and English subtitles."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


@fixture
def tmm_zho_hans_ocr_fuse() -> Series:
    """TMM zho-Hans fused subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse.srt")


@fixture
def tmm_zho_hans_ocr_fuse_clean() -> Series:
    """TMM zho-Hans fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean.srt")


@fixture
def tmm_zho_hans_ocr_fuse_clean_validate() -> Series:
    """TMM zho-Hans fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate.srt")


@fixture
def tmm_zho_hans_ocr_fuse_clean_validate_review() -> Series:
    """TMM zho-Hans fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate_review.srt")


@fixture
def tmm_zho_hans_ocr_fuse_clean_validate_review_flatten() -> Series:
    """TMM zho-Hans fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def tmm_zho_hans_ocr_fuse_clean_validate_review_flatten_romanize() -> Series:
    """TMM zho-Hans fused/cleaned/validated/reviewed/flattened romanized subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten_romanize.srt"
    )


@fixture
def tmm_zho_hans_ocr_lens() -> Series:
    """TMM zho-Hans subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hans_ocr/lens.srt")


@fixture
def tmm_zho_hans_ocr_lens_clean() -> Series:
    """TMM zho-Hans Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/lens_clean.srt")


@fixture
def tmm_zho_hans_ocr_paddle() -> Series:
    """TMM zho-Hans subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle.srt")


@fixture
def tmm_zho_hans_ocr_paddle_clean() -> Series:
    """TMM zho-Hans PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle_clean.srt")


@fixture
def tmm_zho_hant_ocr_fuse() -> Series:
    """TMM zho-Hant fused subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse.srt")


@fixture
def tmm_zho_hant_ocr_fuse_clean() -> Series:
    """TMM zho-Hant fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean.srt")


@fixture
def tmm_zho_hant_ocr_fuse_clean_validate() -> Series:
    """TMM zho-Hant fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate.srt")


@fixture
def tmm_zho_hant_ocr_fuse_clean_validate_review() -> Series:
    """TMM zho-Hant fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate_review.srt")


@fixture
def tmm_zho_hant_ocr_fuse_clean_validate_review_flatten() -> Series:
    """TMM zho-Hant fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify() -> Series:
    """TMM zho-Hant simplified fused/cleaned/validated/reviewed/flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr" / "fuse_clean_validate_review_flatten_simplify.srt"
    )


@fixture
def tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """TMM zho-Hant simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@fixture
def tmm_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize() -> (
    Series
):
    """TMM zho-Hant simplified/reviewed fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
    )


@fixture
def tmm_zho_hant_ocr_lens() -> Series:
    """TMM zho-Hant subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hant_ocr/lens.srt")


@fixture
def tmm_zho_hant_ocr_lens_clean() -> Series:
    """TMM zho-Hant Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/lens_clean.srt")


@fixture
def tmm_zho_hant_ocr_paddle() -> Series:
    """TMM zho-Hant subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle.srt")


@fixture
def tmm_zho_hant_ocr_paddle_clean() -> Series:
    """TMM zho-Hant PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle_clean.srt")


@fixture
def tmm_yue_simplify_expected_series_diff() -> list[str]:
    """Expected differences for TMM Yue Simplified vs Traditional subtitles."""
    return []


@fixture
def tmm_zho_simplify_expected_series_diff() -> list[str]:
    """Expected differences for TMM Zho Simplified vs Traditional subtitles."""
    return [
        "edit: SIMP[15] -> TRAD[15]: '搞得皇帝要去追〝野鸡〞' -> '搞得皇帝要去追「野鸡」'",
        "edit: SIMP[175] -> TRAD[175]: '一个做九世〝野鸡〞' -> '一个做九世「野鸡」'",
        "edit: SIMP[378] -> TRAD[378]: '我没有〝摸摸〞嘛' -> '我没有「摸摸」嘛'",
        "edit: SIMP[383] -> TRAD[383]: '哎⋯〝摸摸〞在那个姐姐身上\\u3000快过去拿' -> '哎⋯「摸摸」在那个姐姐身上\\u3000快过去拿'",
        "edit: SIMP[384] -> TRAD[384]: '嘿\\u3000我看你还能〝盯〞到什么时候\\u3000嗨' -> '嘿\\u3000我看你还能「盯」到什么时候\\u3000嗨'",
        "edit: SIMP[386] -> TRAD[386]: '没有\\u3000没有〝摸摸〞' -> '没有\\u3000没有「摸摸」'",
        "edit: SIMP[401] -> TRAD[401]: '〝鲍鱼〞' -> '「鲍鱼」'",
        "edit: SIMP[402] -> TRAD[402]: '哎呀〝鲍鱼〞是一片一片的\\u3000叫我哥哥' -> '哎呀「鲍鱼」是一片一片的\\u3000叫我哥哥'",
        "edit: SIMP[404] -> TRAD[404]: '〝知知〞' -> '「知知」'",
        "edit: SIMP[405] -> TRAD[405]: '傻冒货〝知知〞是一条一条的' -> '傻冒货「知知」是一条一条的'",
        "edit: SIMP[408] -> TRAD[408]: '〝爸爸〞' -> '「爸爸」'",
        "edit: SIMP[478] -> TRAD[478]: '九世〝野鸡〞' -> '九世「野鸡」'",
        "edit: SIMP[480] -> TRAD[480]: '她是〝野鸡〞啊' -> '她是「野鸡」啊'",
        "edit: SIMP[481] -> TRAD[481]: '〝鸡〞都有爱国的嘛' -> '「鸡」都有爱国的嘛'",
        "edit: SIMP[825] -> TRAD[825]: '你再〝盯〞啊\\u3000把你屁股变到嘴巴上去' -> '你再「盯」啊\\u3000把你屁股变到嘴巴上去'",
        "edit: SIMP[903] -> TRAD[903]: '〝离〞你⋯我〝离〞你' -> '「离」你⋯我「离」你'",
        "edit: SIMP[938] -> TRAD[938]: '哎\\u3000不要\\u3000你真是〝鸡〞性难改耶' -> '哎\\u3000不要\\u3000你真是「鸡」性难改耶'",
        "edit: SIMP[1024] -> TRAD[1024]: '那么〝鸡〞一样可以变凤凰啊' -> '那么「鸡」一样可以变凤凰啊'",
        "edit: SIMP[1125] -> TRAD[1125]: '好〝黄〞啊' -> '好「黄」啊'",
        "edit: SIMP[1348] -> TRAD[1348]: '就不再做〝野鸡〞了' -> '就不再做「野鸡」了'",
        "edit: SIMP[1544] -> TRAD[1544]: '他害得那个〝野鸡〞刮破了脸\\u3000好可怜呢' -> '他害得那个「野鸡」刮破了脸\\u3000好可怜呢'",
        "edit: SIMP[1560] -> TRAD[1560]: '但是她再也不做〝野鸡〞' -> '但是她再也不做「野鸡」'",
    ]
