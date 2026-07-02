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
from scinoephile.llms.dual_1_to_1 import Dual1To1Prompt
from scinoephile.llms.dual_1_to_1.ocr_fusion import OcrFusionManager
from scinoephile.llms.mono_n import MonoNManager, MonoNPrompt
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
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptEng,
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
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
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
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHans,
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
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
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
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHant,
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
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
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
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHans,
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
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
    )


@cache
def get_tmm_zho_hans_block_review_test_cases(
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHans,
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
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
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
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHant,
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
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
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
    prompt_cls: type[MonoNPrompt] = BlockReviewPromptZhoHans,
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
        path, MonoNManager, prompt_cls=prompt_cls, **kwargs
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
    return [
        "edit: SIMP[920] -> TRAD[920]: '你⋯你把扇真系要等天光先有法力呀？' -> '你⋯你把伞真系要等天光先有法力呀？'",
        "edit: SIMP[924] -> TRAD[924]: '嗱我解释你听你就明㗎嘞' -> '嗱我解你听你就明㗎嘞'",
        "edit: SIMP[942] -> TRAD[942]: '以后唔会再有瘟疫㗎喇' -> '以后唔会再有瘟疫㗎嘞'",
        "edit: SIMP[949] -> TRAD[949]: '但之系咁喎，若然烧死佢都仲有瘟疫' -> '但只系咁喎，若然烧死佢都仲有瘟疫'",
        "edit: SIMP[964] -> TRAD[964]: '放心啦，嗰啲人唔会再嚟烧你㗎嘞' -> '放心啦，嗰啲人唔会再嚟烧你㗎喇'",
        "edit: SIMP[970] -> TRAD[970]: '但系段唔会对个马桶产生感情' -> '但系并唔会对个马桶产生感情'",
        "edit: SIMP[976] -> TRAD[976]: '咪啦你，真是鸡性难改' -> '咪啦你，真系鸡性难改'",
        "edit: SIMP[1027] -> TRAD[1027]: '大种，跟我来' -> '大聪，跟我来'",
        "edit: SIMP[1078] -> TRAD[1078]: '若然唔系，黄金会变番狗屎' -> '若然唔系，黄金会变返狗屎'",
        "edit: SIMP[1079] -> TRAD[1079]: '大孖疮都会标番晒出嚟' -> '大疴疮都会标番晒出嚟'",
        "edit: SIMP[1126] -> TRAD[1126]: '唉⋯好边' -> '唉⋯好攰'",
        "edit: SIMP[1163] -> TRAD[1163]: '今世，我一定要嫁俾呀边个先甘心嘅' -> '今世，我一定要嫁俾阿边个先甘心嘅'",
        "edit: SIMP[1211] -> TRAD[1211]: '我讲道理咋幡' -> '我讲道理咋嘛'",
        "edit: SIMP[1213] -> TRAD[1213]: '嗱⋯系咪呢，而家打亲人嘞' -> '哼⋯系咪呢，而家打亲人嘞'",
        "edit: SIMP[1236] -> TRAD[1236]: '打回原形嘞，嗱嗱声走啦' -> '打回原形嘞，哼哼声走啦'",
        "edit: SIMP[1250] -> TRAD[1250]: '拧佢块面过嚟\\u3000\\u3000拧番块面呀' -> '拧佢块面过嚟\\u3000\\u3000拧翻块面呀'",
        "edit: SIMP[1264] -> TRAD[1264]: '无论如何都要猛番佢上嚟' -> '无论如何都要掹番佢上嚟'",
        "edit: SIMP[1290] -> TRAD[1290]: '唔得\\u3000咩大字形？' -> '唔得\\u3000咩大字型？'",
        "edit: SIMP[1309] -> TRAD[1309]: '你横是咁多靓，多件唔多，少件唔少' -> '你横系咁多靓，多件唔多，少件唔少'",
        "edit: SIMP[1310] -> TRAD[1310]: '嗰件⋯当醒俾我呢' -> '嗰件⋯当醒俾我啲呢'",
        "edit: SIMP[1313] -> TRAD[1313]: '一系⋯我帮你修修啲脚甲佢呀咁长' -> '一系⋯我帮你修修啲脚甲佢都咁长'",
        "edit: SIMP[1341] -> TRAD[1341]: '我话晒都系嚟度嘅陀哋喎' -> '我话晒都系嚟度嘅佗哋喎'",
        "edit: SIMP[1347] -> TRAD[1347]: '冚唪呤走晒，呢班友返嚟执行李㗎咋' -> '冚掂凧走晒，呢班友返嚟执行李㗎咋'",
        "edit: SIMP[1470] -> TRAD[1470]: '死仆街，我一早杀咗你，就唔洗死咁多人' -> '死仆街，我一早杀咗你'",
        "edit: SIMP[1471] -> TRAD[1471]: '就唔洗死咁多人' -> '就唔使死咁多人'",
        "edit: SIMP[1477] -> TRAD[1477]: '主公⋯' -> '主宫⋯'",
        "edit: SIMP[1480] -> TRAD[1480]: '主公⋯你呃我⋯呀⋯' -> '主宫⋯你呃我⋯呀⋯'",
        "edit: SIMP[1508] -> TRAD[1508]: '系嘅话，咁你摆番佢，摆呀' -> '系嘅话，咁你摆番但，摆呀'",
        "edit: SIMP[1544] -> TRAD[1544]: '系咁你点打入佢体内吖？' -> '系咁你点打入但体内吖？'",
        "edit: SIMP[1545] -> TRAD[1545]: '我想劳烦你帮我撑大佢个口' -> '我想劳烦你帮我猛大但个口'",
        "edit: SIMP[1558] -> TRAD[1558]: '痾番啲金粉出嚟吖' -> '痾返啲金粉出嚟吖'",
        "edit: SIMP[1565] -> TRAD[1565]: '咩呀？\\u3000\\u3000谂办法塞大佢个口' -> '咩呀？\\u3000\\u3000谂办法撬大佢个口'",
        "edit: SIMP[1616] -> TRAD[1616]: '哗⋯仲做埋尊者添吖\\u3000佢都可以做尊者？' -> '哗⋯仲做埋尊者添吖\\u3000但都可以做尊者？'",
        "edit: SIMP[1623] -> TRAD[1623]: '有咩志愿吖？' -> '有咩志愿呀？'",
    ]


@fixture
def tmm_zho_simplify_expected_series_diff() -> list[str]:
    """Expected differences for TMM Zho Simplified vs Traditional subtitles."""
    return [
        "edit: SIMP[2] -> TRAD[2]: '众卿家大发雷霆\\u3000所为何事' -> '众卿家大发雷霆，所为何事'",
        "edit: SIMP[3] -> TRAD[3]: '王母\\u3000你先讲' -> '王母，你先讲'",
        "edit: SIMP[4] -> TRAD[4]: '玉帝啊\\u3000降龙罗汉' -> '玉帝啊，降龙罗汉'",
        "edit: SIMP[9] -> TRAD[9]: '让牛郎织女幽会\\u3000丑大了' -> '让牛郎织女幽会，丑大了'",
        "edit: SIMP[12] -> TRAD[12]: '玉帝啊\\u3000向来凡间男女关系' -> '玉帝啊，向来凡间男女关系'",
        "edit: SIMP[15] -> TRAD[15]: '搞得皇帝要去追〝野鸡〞' -> '搞得皇帝要去追「野鸡」'",
        "edit: SIMP[48] -> TRAD[48]: '哎\\u3000神仙就大了' -> '哎，神仙就大了'",
        "edit: SIMP[49] -> TRAD[49]: '伏虎，你真是个管家婆' -> '伏虎\\u3000你真是个管家婆'",
        "edit: SIMP[50] -> TRAD[50]: '不过你还挺讲义气，我心领了' -> '不过你还挺讲义气\\u3000我心领了'",
        "edit: SIMP[51] -> TRAD[51]: '哎，谢谢⋯' -> '哎\\u3000谢谢⋯'",
        "edit: SIMP[52] -> TRAD[52]: '哎，照目前情形看起来' -> '哎\\u3000照目前情形看起来'",
        "edit: SIMP[55] -> TRAD[55]: '我们俩兄弟聊天，几时轮到你插嘴' -> '我们俩兄弟聊天\\u3000几时轮到你插嘴'",
        "edit: SIMP[56] -> TRAD[56]: '嘿呀，你这个灶君' -> '嘿呀\\u3000你这个灶君'",
        "edit: SIMP[59] -> TRAD[59]: '你就到上面来说人家不是，插他' -> '你就到上面来说人家不是\\u3000插他'",
        "edit: SIMP[61] -> TRAD[61]: '啊，刚才插完好痛，现在又要插' -> '啊\\u3000刚才插完好痛\\u3000现在又要插'",
        "edit: SIMP[62] -> TRAD[62]: '小小一个罗汉，什么事情你都要管' -> '小小一个罗汉\\u3000什么事情你都要管'",
        "edit: SIMP[63] -> TRAD[63]: '岂有此理，你偷吃我的蟠桃，赔来' -> '岂有此理\\u3000你偷吃我的蟠桃\\u3000赔来'",
        "edit: SIMP[64] -> TRAD[64]: '王母，吃一点人家也没说什么' -> '王母\\u3000吃一点人家也没说什么'",
        "edit: SIMP[70] -> TRAD[70]: '干吗，不服气就冲我来' -> '干吗\\u3000不服气就冲我来'",
        "edit: SIMP[73] -> TRAD[73]: '我照吃不误，到哪一个了' -> '我照吃不误\\u3000到哪一个了'",
        "edit: SIMP[74] -> TRAD[74]: '到哪一个了，就你好了' -> '到哪一个了\\u3000就你好了'",
        "edit: SIMP[81] -> TRAD[81]: '我说你老了，没事就退休吧' -> '我说你老了\\u3000没事就退休吧'",
        "edit: SIMP[83] -> TRAD[83]: '弄得男跟男，女跟女' -> '弄得男跟男\\u3000女跟女'",
        "edit: SIMP[84] -> TRAD[84]: '再弄下去，人跟猪，蟑螂配牛了' -> '再弄下去\\u3000人跟猪\\u3000蟑螂配牛了'",
        "edit: SIMP[86] -> TRAD[86]: '哎，插他' -> '哎\\u3000插他'",
        "edit: SIMP[87] -> TRAD[87]: '哎，人家年纪不小了，不要欺负他' -> '哎\\u3000人家年纪不小了\\u3000不要欺负他'",
        "edit: SIMP[88] -> TRAD[88]: '哎呀，你想管闲事吗，阎罗王' -> '哎呀\\u3000你想管闲事吗\\u3000阎罗王'",
        "edit: SIMP[90] -> TRAD[90]: '不要碰面就插，我们是讲道理的' -> '不要碰面就插\\u3000我们是讲道理的'",
        "edit: SIMP[93] -> TRAD[93]: '就不肯给她一个儿子，为什么' -> '就不肯给她一个儿子\\u3000为什么'",
        "edit: SIMP[94] -> TRAD[94]: '搞得那个女的终于想不开，跳海自尽' -> '搞得那个女的终于想不开\\u3000跳海自尽'",
        "edit: SIMP[96] -> TRAD[96]: '到了下面，他还说她是枉死的' -> '到了下面\\u3000他还说她是枉死的'",
        "edit: SIMP[101] -> TRAD[101]: '凡人的命运早已经成定数，并无不妥' -> '凡人的命运早已经成定数\\u3000并无不妥'",
        "edit: SIMP[104] -> TRAD[104]: '哎，我⋯' -> '哎\\u3000我⋯'",
        "edit: SIMP[105] -> TRAD[105]: '谁说照例执行，谁订的令' -> '谁说照例执行\\u3000谁订的令'",
        "edit: SIMP[108] -> TRAD[108]: '玉帝，你定的例' -> '玉帝\\u3000你定的例'",
        "edit: SIMP[112] -> TRAD[112]: '玉帝，各位仙友' -> '玉帝\\u3000各位僊友'",
        "edit: SIMP[134] -> TRAD[134]: '玉帝\\u3000我们每一位成仙至今' -> '玉帝，我们每一位成仙至今'",
        "edit: SIMP[136] -> TRAD[136]: '世情种种\\u3000凡间一切在我们来说' -> '世情种种，凡间一切在我们来说'",
        "edit: SIMP[144] -> TRAD[144]: '啊\\u3000听观音大士说话真是好听啊' -> '啊，听观音大士说话真是好听啊'",
        "edit: SIMP[145] -> TRAD[145]: '哎\\u3000舒服\\u3000舒服' -> '哎，舒服，舒服'",
        "edit: SIMP[149] -> TRAD[149]: '你不要乱说话\\u3000阎罗王' -> '你不要乱说话，阎罗王'",
        "edit: SIMP[150] -> TRAD[150]: '慢点\\u3000大士自有分寸' -> '慢点，大士自有分寸'",
        "edit: SIMP[151] -> TRAD[151]: '降龙\\u3000你做了这么多的事情' -> '降龙，你做了这么多的事情'",
        "edit: SIMP[158] -> TRAD[158]: '无论他们是多么的笨\\u3000多么的无知' -> '无论他们是多么的笨，多么的无知'",
        "edit: SIMP[159] -> TRAD[159]: '怎么凶\\u3000怎么该死也好' -> '怎么凶，怎么该死也好'",
        "edit: SIMP[165] -> TRAD[165]: '是不是\\u3000降龙' -> '是不是，降龙'",
        "edit: SIMP[170] -> TRAD[170]: '哟\\u3000我怕你啊\\u3000我正有此意' -> '哟，我怕你啊，我正有此意'",
        "edit: SIMP[175] -> TRAD[175]: '一个做九世〝野鸡〞' -> '一个做九世「野鸡」'",
        "edit: SIMP[180] -> TRAD[180]: '好\\u3000你就用凡人的身份下去' -> '好，你就用凡人的身份下去'",
        "edit: SIMP[184] -> TRAD[184]: '降龙\\u3000就用你的诚意去感化他们' -> '降龙，就用你的诚意去感化他们'",
        "edit: SIMP[353] -> TRAD[353]: '啊⋯哎⋯老婆，是男的还是女的' -> '啊⋯哎⋯老婆 是男的还是女的'",
        "edit: SIMP[354] -> TRAD[354]: '生把扇子' -> '生拔扇子'",
        "edit: SIMP[378] -> TRAD[378]: '我没有〝摸摸〞嘛' -> '我没有「摸摸」嘛'",
        "edit: SIMP[383] -> TRAD[383]: '哎⋯〝摸摸〞在那个姐姐身上 快过去拿' -> '哎⋯「摸摸」在那个姐姐身上\\u3000快过去拿'",
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
        "edit: SIMP[484] -> TRAD[484]: '哎 你叫什么名字' -> '哎\\u3000你叫什么名字？'",
        "edit: SIMP[492] -> TRAD[492]: '走嘞' -> '走勒'",
        "edit: SIMP[574] -> TRAD[574]: '不可能 我的娘哎' -> '不可能，我的娘哎'",
        "edit: SIMP[586] -> TRAD[586]: '嚯\\u3000我换了发型\\u3000不错吧' -> '霍\\u3000我换了发型\\u3000不错吧'",
        "edit: SIMP[668] -> TRAD[668]: '你妈才来找你呢，我老爸早死了' -> '你妈才来找你呢 我老爸早死了'",
        "edit: SIMP[825] -> TRAD[825]: '你再〝盯〞啊\\u3000把你屁股变到嘴巴上去' -> '你再「盯」啊\\u3000把你屁股变到嘴巴上去'",
        "edit: SIMP[844] -> TRAD[844]: '天爷\\u3000你也知道' -> '天爷，你也知道'",
        "edit: SIMP[852] -> TRAD[852]: '哎\\u3000天爷\\u3000你很为难\\u3000嚯' -> '哎\\u3000天爷\\u3000你很为难\\u3000呵'",
        "edit: SIMP[873] -> TRAD[873]: '怎么祭祀' -> '怎么祭'",
        "edit: SIMP[880] -> TRAD[880]: '哇\\u3000好漂亮\\u3000烧死了多可惜' -> '哇，好漂亮，烧死了多可惜'",
        "edit: SIMP[903] -> TRAD[903]: '〝离〞你⋯我〝离〞你' -> '「离」你⋯我「离」你'",
        "edit: SIMP[905] -> TRAD[905]: '你们看他的脸\\u3000比神仙还要灵验' -> '你们看他的脸\\u3000比神僊还要灵验'",
        "edit: SIMP[938] -> TRAD[938]: '哎\\u3000不要\\u3000你真是〝鸡〞性难改耶' -> '哎\\u3000不要\\u3000你真是「鸡」性难改耶'",
        "edit: SIMP[1024] -> TRAD[1024]: '那么〝鸡〞一样可以变凤凰啊' -> '那么「鸡」一样可以变凤凰啊'",
        "edit: SIMP[1027] -> TRAD[1027]: '主公 你真有先见之明' -> '主公，你真有先见之明'",
        "edit: SIMP[1042] -> TRAD[1042]: '大种\\u3000你要切记' -> '大爷，你要切记'",
        "edit: SIMP[1045] -> TRAD[1045]: '所有的大疱都会冒出来' -> '所有的大疮都会冒出来'",
        "edit: SIMP[1092] -> TRAD[1092]: '妈的 好累呀' -> '妈的，好累呀'",
        "edit: SIMP[1121] -> TRAD[1121]: '算了\\u3000不做和尚好了' -> '算了，不做和尚好了'",
        "edit: SIMP[1122] -> TRAD[1122]: '总之不能杀人\\u3000行不行' -> '总之不能杀人，行不行'",
        "edit: SIMP[1125] -> TRAD[1125]: '好〝黄〞啊' -> '好「黄」啊'",
        "edit: SIMP[1136] -> TRAD[1136]: '啊\\u3000丑了\\u3000大种\\u3000时辰到了' -> '啊\\u3000丑了\\u3000大钟\\u3000时辰到了'",
        "edit: SIMP[1194] -> TRAD[1194]: '师傅\\u3000我⋯' -> '师傅，我⋯'",
        "edit: SIMP[1195] -> TRAD[1195]: '这么久也不下来\\u3000找死' -> '这么久也不下来，找死'",
        "edit: SIMP[1196] -> TRAD[1196]: '都变回乞丐了\\u3000快点走啊' -> '都变回乞丐了，快点走啊'",
        "edit: SIMP[1200] -> TRAD[1200]: '不要叫我大种 叫我朱大常' -> '不要叫我大种，叫我朱大常'",
        "edit: SIMP[1281] -> TRAD[1281]: '大种，我再怎么样也要带你回去' -> '大爷 我再怎么样也要带你回去'",
        "edit: SIMP[1315] -> TRAD[1315]: '糟了\\u3000土地公也不见了' -> '糟了，土地公也不见了'",
        "edit: SIMP[1316] -> TRAD[1316]: '哎呀\\u3000这次祸闯大了' -> '哎呀，这次祸闯大了'",
        "edit: SIMP[1348] -> TRAD[1348]: '就不再做〝野鸡〞了' -> '就不再做「野鸡」了'",
        "edit: SIMP[1365] -> TRAD[1365]: '哎\\u3000是啊' -> '哎，是啊'",
        "edit: SIMP[1368] -> TRAD[1368]: '哦\\u3000我好怕' -> '哦，我好怕'",
        "edit: SIMP[1430] -> TRAD[1430]: '我打死你 打死你⋯' -> '我打死你，打死你⋯'",
        "edit: SIMP[1459] -> TRAD[1459]: '他就趁着今天晚上月蚀至阴的时候' -> '他就趁著今天晚上月蚀至阴的时候'",
        "edit: SIMP[1491] -> TRAD[1491]: '哎呀 糟了' -> '哎呀，糟了'",
        "edit: SIMP[1521] -> TRAD[1521]: '师傅 你快点想想办法 把金粉拉出来' -> '师傅，你快点想想办法，把金粉拉出来'",
        "edit: SIMP[1544] -> TRAD[1544]: '他害得那个〝野鸡〞刮破了脸，好可怜呢' -> '他害得那个「野鸡」刮破了脸\\u3000好可怜呢'",
        "edit: SIMP[1546] -> TRAD[1546]: '临死之前呢，还多伤了几十条人命' -> '临死之前呢\\u3000还多伤了几十条人命'",
        "edit: SIMP[1552] -> TRAD[1552]: '你算了吧，整天都说单挑' -> '你算了吧\\u3000整天都说单挑'",
        "edit: SIMP[1560] -> TRAD[1560]: '但是她再也不做〝野鸡〞' -> '但是她再也不做「野鸡」'",
    ]
