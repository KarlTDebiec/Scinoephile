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
    """Expected differences for TMM subtitles."""
    return [
        "edit: SIMP[5] -> TRAD[5]: '冚唪呤偷晒去俾牛郎嗰啲牛食呀' -> '冚嗪呤偷晒去俾牛郎嗰啲牛食呀'",
        "edit: SIMP[8] -> TRAD[8]: '仆街喇，已经疯咗成窦仔女出嚟啦' -> '仆街喇，已经痾咗成窦仔女出嚟啦'",
        "edit: SIMP[43] -> TRAD[43]: '我咪代表降龙嚟同大家道个歉罗' -> '我咪代表降龙嚟同大家道个歉啰'",
        "edit: SIMP[54] -> TRAD[54]: '求其认句错咪撑罗' -> '求其认句错咪撑啰'",
        "edit: SIMP[57] -> TRAD[57]: '你个灶君，逢年尾喺下面揾着数' -> '你个灶君，逢年尾喺下面搵著数'",
        "edit: SIMP[60] -> TRAD[60]: '喂，喏喏插完仲好痛喎，又插？' -> '喂，啱啱插完仲好痛喎，又插？'",
        "edit: SIMP[62] -> TRAD[62]: '乜嘢事都要你理罗喎' -> '乜嘢事都要你理啰喎'",
        "edit: SIMP[64] -> TRAD[64]: '你好赔罗喎幡' -> '你好赔啰喎幡'",
        "edit: SIMP[73] -> TRAD[73]: '唔好揾只狗吠吠拱' -> '唔好搵只狗吠吠拱'",
        "edit: SIMP[133] -> TRAD[133]: '我话做就做罗' -> '我话做就做啰'",
        "edit: SIMP[139] -> TRAD[139]: '玉帝，我们每一位成仙至今' -> '玉帝，我哋每一位成仙至今'",
        "edit: SIMP[141] -> TRAD[141]: '世情种种，凡间一切，在我哋讲' -> '世情种种，凡间一切，在我哋嚟讲'",
        "edit: SIMP[142] -> TRAD[142]: '系遥远而微不足道㗎' -> '系遥远而微不足道架'",
        "edit: SIMP[151] -> TRAD[151]: '呢个小子借住为人间抱不平为借口' -> '呢个小子借住为人间抱不平为藉口'",
        "edit: SIMP[156] -> TRAD[156]: '我祇系想呢班自以为高高在上嘅神仙' -> '我祗系想呢班自以为高高在上嘅神仙'",
        "edit: SIMP[158] -> TRAD[158]: '因为佢哋一世人祇得区区几廿年命' -> '因为佢哋一世人祗得区区几廿年命'",
        "edit: SIMP[213] -> TRAD[213]: '祇要你揾到金身合二为一' -> '祗要你搵到金身合二为一'",
        "edit: SIMP[220] -> TRAD[220]: '呢把扇每日祇可以用三次' -> '呢把扇每日祗可以用三次'",
        "edit: SIMP[248] -> TRAD[248]: '咁所以咪要你同我一齐落去罗' -> '咁所以咪要你同我一齐落去啰'",
        "edit: SIMP[295] -> TRAD[295]: '喺边度摘架？\\u3000\\u3000呢⋯嗰度啰' -> '喺边度摘啊？\\u3000\\u3000呢⋯嗰度啰'",
        "edit: SIMP[296] -> TRAD[296]: '老爷呀，点解会咁架？\\u3000\\u3000老爷，夫人' -> '老爷呀，点解会咁啊？\\u3000\\u3000老爷，夫人'",
        "edit: SIMP[310] -> TRAD[310]: '街佬' -> '街啰'",
        "edit: SIMP[313] -> TRAD[313]: '行过几条咪系囉' -> '行过几条咪系啰'",
        "edit: SIMP[315] -> TRAD[315]: '鬼叫你正话郁来郁去咩' -> '鬼叫你正话郁嚟郁去咩'",
        "edit: SIMP[319] -> TRAD[319]: '冚家富贵，嗰间死人铺头' -> '冚家富贵，嗰间死人舖头'",
        "edit: SIMP[323] -> TRAD[323]: '十万火急\\u3000\\u3000系呀⋯' -> '十万火急⋯系呀⋯'",
        "edit: SIMP[327] -> TRAD[327]: '咁冇风度架\\u3000\\u3000咁就走咗去' -> '咁冇风度架⋯咁就走咗去'",
        "edit: SIMP[333] -> TRAD[333]: '骑呢怪罗，带住我左兜右兜咁' -> '骑呢怪啰，带住我左兜右兜咁'",
        "edit: SIMP[335] -> TRAD[335]: '快啲攞嚟啦\\u3000\\u3000喂⋯龙⋯' -> '快啲攞嚟啦⋯喂⋯龙⋯'",
        "edit: SIMP[349] -> TRAD[349]: '咁咪系罗，变咗白痴' -> '咁咪系啰，变咗白痴'",
        "edit: SIMP[353] -> TRAD[353]: '到时呀，你静静鸡攞番啲法力呀嘛' -> '到时呀，你静静鸡攞番啲法力吖嘛'",
        "edit: SIMP[388] -> TRAD[388]: '老爷，不如报官罗？' -> '老爷，不如报官啰？'",
        "edit: SIMP[389] -> TRAD[389]: '报咩官啫，我咪官罗' -> '报咩官啫，我咪官啰'",
        "edit: SIMP[395] -> TRAD[395]: '究竟你系何方神圣，好讲罗喎' -> '究竟你系何方神圣，好讲啰喎'",
        "edit: SIMP[396] -> TRAD[396]: '一定系识变戏法嘅，好教我罗喎' -> '一定系识变戏法嘅，好教我啰喎'",
        "edit: SIMP[400] -> TRAD[400]: '睇你撑到几时，扮蒙吖啦' -> '睇你撑到几时，扮懵吖啦'",
        "edit: SIMP[401] -> TRAD[401]: '蒙蒙⋯冇⋯冇蒙蒙' -> '懵懵⋯冇⋯冇懵懵'",
        "edit: SIMP[402] -> TRAD[402]: '佢真低，唔系假低架喎' -> '佢真低，唔系假低家喎'",
        "edit: SIMP[409] -> TRAD[409]: '睇怕都要揾份兼职啦' -> '睇怕都要搵份兼职啦'",
        "edit: SIMP[434] -> TRAD[434]: '你听着呀，你系神仙嚟㗎' -> '你听着呀，你系神仙嚟架'",
        "edit: SIMP[439] -> TRAD[439]: '咁你就记得番晒㗎喇' -> '咁你就记得番晒架喇'",
        "edit: SIMP[441] -> TRAD[441]: '搞到我笃尿病到窒吓窒吓？' -> '搞到我笃尿痾到窒吓窒吓？'",
        "edit: SIMP[451] -> TRAD[451]: '大夫呀，唔该帮我睇睇呢坛嘢' -> '大夫呀，不该帮我看看呢坛嘢'",
        "edit: SIMP[462] -> TRAD[462]: '哎呀！撞鬼你罗' -> '哎呀！撞鬼你啰'",
        "edit: SIMP[475] -> TRAD[475]: '咪有你着数罗' -> '咪有你着数啰'",
        "edit: SIMP[512] -> TRAD[512]: '我好快去会返嚟揾你' -> '我好快就会返嚟搵你'",
        "edit: SIMP[514] -> TRAD[514]: '姓名祇系代号，点叫都系一样㗎啫' -> '姓名祗系代号，点叫都系一样㗎啫'",
        "edit: SIMP[531] -> TRAD[531]: '皇气黑气都及住晒架' -> '皇气黑气都及住晒㗎'",
        "edit: SIMP[532] -> TRAD[532]: '上个月嗰剂，就至跌友嘞' -> '上个月嗰剂，就至叠友嘞'",
        "edit: SIMP[533] -> TRAD[533]: '你系土地，定陀哋呀？' -> '你系土地，定陀地呀？'",
        "edit: SIMP[563] -> TRAD[563]: '仲唔攞件衫俾我换' -> '仲唔摆件衫俾我换'",
        "edit: SIMP[568] -> TRAD[568]: '抵锡' -> '抵食'",
        "edit: SIMP[571] -> TRAD[571]: '呢辘嘢系铁嚟架，唔食得架' -> '呢辘嘢系铁嚟架，唔食得㗎'",
        "edit: SIMP[572] -> TRAD[572]: '吔后面嗰鼓啦' -> '吔后面嗰旧啦'",
        "edit: SIMP[582] -> TRAD[582]: '吓？袁霸天呀？' -> '吓？袁霸天呀'",
        "edit: SIMP[583] -> TRAD[583]: '哎呀⋯快啲喱埋先嘞' -> '哎呀⋯快啲躲埋先嘞'",
        "edit: SIMP[588] -> TRAD[588]: '揾都悭番' -> '搵都省番'",
        "edit: SIMP[602] -> TRAD[602]: '家吓你了解到，俾人欺负嘅痛苦呢？' -> '家下你了解到，俾人欺负嘅痛苦呢？'",
        "edit: SIMP[609] -> TRAD[609]: '我好快会再揾你' -> '我好快会再搵你'",
        "edit: SIMP[644] -> TRAD[644]: '系罗，若然你无做错事' -> '系啰，若然你无做错事'",
        "edit: SIMP[656] -> TRAD[656]: '仲有你，揾个忤怍佬返嚟送佢哋一程' -> '仲有你，搵个忤怍佬返嚟送佢哋一程'",
        "edit: SIMP[693] -> TRAD[693]: '大种，你老豆揾你呀' -> '大佬，你老豆搵你呀'",
        "edit: SIMP[694] -> TRAD[694]: '你阿妈揾你呀，我老豆死咗好耐啦' -> '你阿妈搵你呀，我老豆死咗好耐啦'",
        "edit: SIMP[704] -> TRAD[704]: '正话我死鬼老逗返嚟揾我⋯' -> '正话我死鬼老逗返嚟搵我⋯'",
        "edit: SIMP[722] -> TRAD[722]: '唏⋯你做人连些少自信都右' -> '唏⋯你做人连些少自信都冇'",
        "edit: SIMP[793] -> TRAD[793]: '我俾你吓到濑尿呀' -> '我俾你吓到尿尿呀'",
        "edit: SIMP[794] -> TRAD[794]: '骑呢怪，做咩搞到咁乌 where ？' -> '骑呢怪，做咩搞到咁乌where？'",
        "edit: SIMP[795] -> TRAD[795]: '我扮到咁乌 where 都系为咗掩人耳目' -> '我扮到咁乌where都系为咗掩人耳目'",
        "edit: SIMP[814] -> TRAD[814]: '上头罗' -> '上头啰'",
        "edit: SIMP[822] -> TRAD[822]: '会计部出粮嘅啫\\u3000\\u3000系罗' -> '会计部出粮嘅啫\\u3000\\u3000系啰'",
        "edit: SIMP[823] -> TRAD[823]: '咁就系罗' -> '咁就系啰'",
        "edit: SIMP[842] -> TRAD[842]: '哎呀⋯币啦⋯' -> '哎呀⋯弊啦⋯'",
        "edit: SIMP[844] -> TRAD[844]: '我有大孖疮呀⋯死啦⋯' -> '我有大疤疮呀⋯死啦⋯'",
        "edit: SIMP[852] -> TRAD[852]: '咁就会消灾解难架嘞' -> '咁就会消灾解难㗎嘞'",
        "edit: SIMP[854] -> TRAD[854]: '可能要我减寿十年架幡' -> '可能要我减寿十年㗎幡'",
        "edit: SIMP[855] -> TRAD[855]: '又系啲妖言惑众，阻着瞓觉' -> '又系啲妖言惑众，阻著瞓觉'",
        "edit: SIMP[867] -> TRAD[867]: '即刻去揾个人嚟祭神' -> '即刻去搵个人嚟祭神'",
        "edit: SIMP[868] -> TRAD[868]: '揾咩人呀⋯' -> '搵咩人呀⋯'",
        "edit: SIMP[870] -> TRAD[870]: '咁去边度揾呀⋯' -> '咁去边度搵呀⋯'",
        "edit: SIMP[871] -> TRAD[871]: '怡香院咪大把罗' -> '怡香院咪大把啰'",
        "edit: SIMP[873] -> TRAD[873]: '行啦⋯去罗⋯' -> '行啦⋯去啰⋯'",
        "edit: SIMP[883] -> TRAD[883]: '佢哋话呢叫你揾几个姑娘去祭神喎' -> '佢哋话呢叫你搵几个姑娘去祭神喎'",
        "edit: SIMP[899] -> TRAD[899]: '转啦⋯转呀转⋯\\u3000\\u3000好惊呀⋯' -> '转啦⋯转呀转⋯好惊呀⋯'",
        "edit: SIMP[900] -> TRAD[900]: '哦⋯你奸茅' -> '哦⋯你奸猾'",
        "edit: SIMP[906] -> TRAD[906]: '话你收得贵咯，行啦' -> '话你收得贵啰，行啦'",
        "edit: SIMP[920] -> TRAD[920]: '你⋯你把扇真系要等天光先有法力呀？' -> '你⋯你把伞真系要等天光先有法力呀？'",
        "edit: SIMP[924] -> TRAD[924]: '嗱我解释你听你就明架嘞' -> '嗱，我解你听你就明架嘞'",
        "edit: SIMP[942] -> TRAD[942]: '以后唔会再有瘟疫架喇' -> '以后唔会再有瘟疫架嘞'",
        "edit: SIMP[953] -> TRAD[953]: '揾水嚟淋熄佢啦嘛' -> '搵水嚟淋熄佢啦嘛'",
        "edit: SIMP[964] -> TRAD[964]: '放心啦，嗰啲人唔会再嚟烧你㗎嘞' -> '放心啦，嗰啲人唔会再来烧你架嘞'",
        "edit: SIMP[967] -> TRAD[967]: '个原因系咁嘅，啲人嚟搵你' -> '个原因系咁嘅，啲人来搵你'",
        "edit: SIMP[970] -> TRAD[970]: '但系段唔会对个马桶产生感情' -> '但系甚至唔会对个马桶产生感情'",
        "edit: SIMP[975] -> TRAD[975]: '我报答你罗' -> '我报答你啰'",
        "edit: SIMP[984] -> TRAD[984]: '我系话，你可唔可以，揾过第二份嘢做' -> '我系话，你可唔可以，搵过第二份嘢做'",
        "edit: SIMP[1022] -> TRAD[1022]: '唔做吖？攞番钱嚟罗⋯' -> '唔做吖？攞番钱嚟啰⋯'",
        "edit: SIMP[1027] -> TRAD[1027]: '大种，跟我来' -> '大聪，跟我来'",
        "edit: SIMP[1078] -> TRAD[1078]: '若然唔系，黄金会变番狗屎' -> '若然唔系，黄金会变返狗屎'",
        "edit: SIMP[1079] -> TRAD[1079]: '大孖疮都会标番晒出嚟' -> '大疴疮都会标番晒出嚟'",
        "edit: SIMP[1103] -> TRAD[1103]: '呀边个叫我嚟揾你' -> '呀边个叫我嚟搵你'",
        "edit: SIMP[1104] -> TRAD[1104]: '呀边个叫你嚟揾我做咩事呀？' -> '呀边个叫你嚟搵我做咩事呀？'",
        "edit: SIMP[1105] -> TRAD[1105]: '呀边个叫我嚟揾你⋯' -> '呀边个叫我嚟搵你⋯'",
        "edit: SIMP[1114] -> TRAD[1114]: '咩事呀⋯ ，睇吓⋯咩事呀⋯' -> '咩事呀⋯，睇吓⋯咩事呀⋯'",
        "edit: SIMP[1126] -> TRAD[1126]: '唉⋯好饿' -> '唉⋯好攰'",
        "edit: SIMP[1157] -> TRAD[1157]: '算嘞⋯，唔做和尚就罢就嘞' -> '算嘞⋯，唔做和尚就罢咯'",
        "edit: SIMP[1163] -> TRAD[1163]: '今世，我一定要嫁给呀边个先甘心嘅' -> '今世，我一定要嫁给阿边个先甘心嘅'",
        "edit: SIMP[1166] -> TRAD[1166]: '今晚当我买你怕' -> '今晚当我买，你怕'",
        "edit: SIMP[1167] -> TRAD[1167]: '嗱一人行一步吖嗱' -> '嗱，一人行一步吖，嗱'",
        "edit: SIMP[1168] -> TRAD[1168]: '只要你今日唔上去搅亚玉' -> '只要你今日唔上去搅亚运'",
        "edit: SIMP[1170] -> TRAD[1170]: '哗⋯如果我唔系变咗身咪俾你对死咗' -> '哗⋯如果我唔系变咗身，咪俾你对死咗'",
        "edit: SIMP[1199] -> TRAD[1199]: '你唔好打佢啦，佢唔是叫霸王鸡呀' -> '你唔好打佢啦，佢唔系叫霸王鸡呀'",
        "edit: SIMP[1200] -> TRAD[1200]: '佢是我条仔嚟架' -> '佢系我条仔嚟架'",
        "edit: SIMP[1203] -> TRAD[1203]: '喂大佬呀，都话唔系我罗' -> '喂大佬呀，都话唔系我啰'",
        "edit: SIMP[1211] -> TRAD[1211]: '我讲道理咋幡' -> '我讲道理咋嘛'",
        "edit: SIMP[1213] -> TRAD[1213]: '嗱⋯是咪呢，而家打亲人嘞' -> '哼⋯系咪呢，而家打亲人嘞'",
        "edit: SIMP[1230] -> TRAD[1230]: '对唔住揾错' -> '对唔住，搵错'",
        "edit: SIMP[1231] -> TRAD[1231]: '顺手闩门呀' -> '顺手闩门呀。'",
        "edit: SIMP[1232] -> TRAD[1232]: '食蕉呀' -> '食蕉呀。'",
        "edit: SIMP[1236] -> TRAD[1236]: '打回原形嘞，嗱嗱声走啦' -> '打回原形嘞，哼哼声走啦。'",
        "edit: SIMP[1237] -> TRAD[1237]: '师父，我走唔到呀' -> '师父，我走唔到呀。'",
        "edit: SIMP[1244] -> TRAD[1244]: '大种⋯你唔好死住呀大种' -> '大种⋯你唔好死住呀，大种'",
        "edit: SIMP[1245] -> TRAD[1245]: '你顶多阵呀' -> '你顶多阵呀！'",
        "edit: SIMP[1246] -> TRAD[1246]: '大种⋯你唔死得架，大种' -> '大种⋯你唔死得㗎，大种'",
        "edit: SIMP[1247] -> TRAD[1247]: '你冇晒法术呢' -> '你冇晒法术呢？'",
        "edit: SIMP[1248] -> TRAD[1248]: '听日有，听日你就知死' -> '听日有，听日你就知死！'",
        "edit: SIMP[1250] -> TRAD[1250]: '拧佢块面过嚟\\u3000\\u3000拧番块面呀' -> '拧佢块面过嚟\\u3000拧翻块面呀'",
        "edit: SIMP[1256] -> TRAD[1256]: '系罗' -> '系啰'",
        "edit: SIMP[1260] -> TRAD[1260]: '喂⋯咪嚟咗罗，咁大声做咩呀？' -> '喂⋯咪嚟咗啰，咁大声做咩呀？'",
        "edit: SIMP[1262] -> TRAD[1262]: '人嘅生死早有定数天条规矩冇得变' -> '人嘅生死早有定数，天条规矩冇得变'",
        "edit: SIMP[1264] -> TRAD[1264]: '无论如何都要猛番佢上嚟' -> '无论如何都要掹番佢上嚟'",
        "edit: SIMP[1271] -> TRAD[1271]: '有一段系邪神黑罗刹嘅地头' -> '有一段系邪神黑罗剎嘅地头'",
        "edit: SIMP[1276] -> TRAD[1276]: '喂⋯我系普通料嚟咋仲未有资格落去' -> '喂⋯我系普通料嚟咋，仲未有资格落去'",
        "edit: SIMP[1289] -> TRAD[1289]: '唔得\\u3000一晚咁多呢' -> '唔得\\u3000\\u3000咁就大字形架啦喎'",
        "edit: SIMP[1290] -> TRAD[1290]: '唔得\\u3000咩大字形？' -> '唔得\\u3000咩「大字型」？'",
        "edit: SIMP[1306] -> TRAD[1306]: '其实，我同阿佛祖都唔系好熟架啫' -> '其实，我同阿佛祖都唔系好熟㗎啫'",
        "edit: SIMP[1307] -> TRAD[1307]: '我又唔知你同佢有牙齿痕架嘛' -> '我又唔知你同佢有牙齿痕㗎嘛'",
        "edit: SIMP[1309] -> TRAD[1309]: '你横是咁多靓，多件唔多，少件唔少' -> '你横系咁多靓，多件唔多，少件唔少'",
        "edit: SIMP[1310] -> TRAD[1310]: '嗰件⋯当醒俾我呢' -> '嗰件⋯当醒俾我啲呢'",
        "edit: SIMP[1311] -> TRAD[1311]: '我醒俾你有咩着数呀？' -> '我醒俾你有咩著数呀？'",
        "edit: SIMP[1312] -> TRAD[1312]: '着数？' -> '著数？'",
        "edit: SIMP[1313] -> TRAD[1313]: '一系⋯我帮你修修啲脚甲佢呀咁长' -> '一系⋯我帮你修修啲脚甲，佢都咁长'",
        "edit: SIMP[1316] -> TRAD[1316]: '金身？我个金身唔俾得你架喎' -> '金身？我个金身唔俾得你㗎喎'",
        "edit: SIMP[1317] -> TRAD[1317]: '况且你要嚟都冇用架' -> '况且你要嚟都冇用㗎'",
        "edit: SIMP[1318] -> TRAD[1318]: '摆吓都好架' -> '摆吓都好㗎'",
        "edit: SIMP[1329] -> TRAD[1329]: '你唔钟意呀，咪返番落去罗' -> '你唔钟意呀，咪返番落去啰'",
        "edit: SIMP[1341] -> TRAD[1341]: '我话晒都系嚟度嘅陀哋喎' -> '我话晒都系嚟度嘅佗哋喎'",
        "edit: SIMP[1342] -> TRAD[1342]: '我都话咗呢单嘢济唔过架啦' -> '我都话咗呢单嘢济唔过㗎啦'",
        "edit: SIMP[1343] -> TRAD[1343]: '咩事啫究竟？' -> '咩事啫，究竟？'",
        "edit: SIMP[1347] -> TRAD[1347]: '冚唪呤走晒，呢班友返嚟执行李架咋' -> '冚掂凧走晒，呢班友返嚟执行李㗎咋'",
        "edit: SIMP[1370] -> TRAD[1370]: '都残晒啦，揾小红好过啦' -> '都残晒啦，搵小红好过啦'",
        "edit: SIMP[1373] -> TRAD[1373]: '我不收钱，你济？' -> '我唔收钱，你济？'",
        "edit: SIMP[1374] -> TRAD[1374]: '济，喂，咁即刻嚟罗' -> '济，喂，咁即刻嚟啰'",
        "edit: SIMP[1452] -> TRAD[1452]: '佢揾到嚟都废咗武功啦' -> '佢搵到嚟都废咗武功啦'",
        "edit: SIMP[1457] -> TRAD[1457]: '天将帮扶' -> '天将帮他'",
        "edit: SIMP[1470] -> TRAD[1470]: '死仆街，我一早杀咗你，就唔洗死咁多人' -> '死仆街，我一早杀咗你'",
        "edit: SIMP[1471] -> TRAD[1471]: '就唔洗死咁多人' -> '就唔使死咁多人'",
        "edit: SIMP[1473] -> TRAD[1473]: '主宫同我换了个千年不死嘅心' -> '主宫同我换咗个千年不死嘅心'",
        "edit: SIMP[1479] -> TRAD[1479]: '佢要你帮佢做到塔哋咋' -> '佢要你帮佢做到塔底咋'",
        "edit: SIMP[1481] -> TRAD[1481]: '呃你咪呃你罗' -> '呃你咪呃你啰'",
        "edit: SIMP[1483] -> TRAD[1483]: '黑罗刹有咩阴谋，讲' -> '黑罗剎有咩阴谋，讲'",
        "edit: SIMP[1487] -> TRAD[1487]: '当年佛祖为咗唔俾黑罗刹上凡间' -> '当年佛祖为咗唔俾黑罗剎上凡间'",
        "edit: SIMP[1489] -> TRAD[1489]: '呃你个金身，搅到啲神仙走晒' -> '呃你个金身，搅到啲神仙走哂'",
        "edit: SIMP[1495] -> TRAD[1495]: '吓？降龙，我哋冇时间架啦' -> '吓？降龙，我哋冇时间㗎啦'",
        "edit: SIMP[1497] -> TRAD[1497]: '我哋三个都要留番喺凡间度卖蕉架啦' -> '我哋三个都要留番喺凡间度卖蕉㗎啦'",
        "edit: SIMP[1499] -> TRAD[1499]: '好辛苦呀，俾番个心我呀' -> '好辛苦呀，畀番个心我呀'",
        "edit: SIMP[1506] -> TRAD[1506]: '都祇系继续做黑罗刹嘅傀儡' -> '都祗系继续做黑罗剎嘅傀儡'",
        "edit: SIMP[1508] -> TRAD[1508]: '系嘅话，咁你摆番佢，摆呀' -> '系嘅话，咁你摆番但，摆呀'",
        "edit: SIMP[1510] -> TRAD[1510]: '搅掂晒啦，走啦' -> '搞掂晒啦，走啦'",
        "edit: SIMP[1514] -> TRAD[1514]: '而家唔走冇机会走架啦' -> '而家唔走冇机会走㗎啦'",
        "edit: SIMP[1516] -> TRAD[1516]: '我点都要搅掂埋佢' -> '我点都要搞掂埋佢'",
        "edit: SIMP[1540] -> TRAD[1540]: '将净番呢啲打落黑罗刹嘅身体里面' -> '将净番呢啲打落黑罗剎嘅身体里面'",
        "edit: SIMP[1544] -> TRAD[1544]: '系咁你点打入佢体内吖？' -> '系咁你点打入我体内吖？'",
        "edit: SIMP[1545] -> TRAD[1545]: '我想劳烦你帮我撑大佢个口' -> '我想劳烦你帮我猛张大但个口'",
        "edit: SIMP[1558] -> TRAD[1558]: '痾番啲金粉出嚟吖' -> '痾返啲金粉出嚟吖'",
        "edit: SIMP[1559] -> TRAD[1559]: '我长期便秘架' -> '我长期便秘㗎'",
        "edit: SIMP[1563] -> TRAD[1563]: '嘘⋯我冇牙借来用住先咋' -> '嘘⋯我冇牙，借嚟用住先咋'",
        "edit: SIMP[1565] -> TRAD[1565]: '咩呀？\\u3000\\u3000谂办法塞大佢个口' -> '咩呀？\\u3000\\u3000谂办法撬大它个口'",
        "edit: SIMP[1615] -> TRAD[1615]: '你点会喺度架⋯' -> '你点会喺度㗎⋯'",
        "edit: SIMP[1616] -> TRAD[1616]: '哗⋯仲做埋尊者添吖\\u3000佢都可以做尊者？' -> '哗⋯仲做埋尊者添吖\\u3000但都可以做尊者？'",
        "edit: SIMP[1618] -> TRAD[1618]: '轻轻升咗几级啫' -> '轻轻升了几级啫'",
        "edit: SIMP[1623] -> TRAD[1623]: '有咩志愿吖？' -> '有咩志愿呀？'",
        "edit: SIMP[1624] -> TRAD[1624]: '我想成为一个和平使者向凡间宣扬爱心' -> '我想成为一个和平使者，向凡间宣扬爱心'",
    ]


@fixture
def tmm_zho_simplify_expected_series_diff() -> list[str]:
    """Expected differences for TMM subtitles."""
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
        "edit: SIMP[378] -> TRAD[378]: '我没有“摸摸”嘛' -> '我没有「摸摸」嘛'",
        "edit: SIMP[383] -> TRAD[383]: '哎⋯“摸摸”在那个姐姐身上 快过去拿' -> '哎⋯ 「摸摸」在那个姐姐身上\\u3000快过去拿'",
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
        "edit: SIMP[1544] -> TRAD[1544]: '他害得那个“野鸡”刮破了脸，好可怜呢' -> '他害得那个「野鸡」刮破了脸\\u3000好可怜呢'",
        "edit: SIMP[1546] -> TRAD[1546]: '临死之前呢，还多伤了几十条人命' -> '临死之前呢\\u3000还多伤了几十条人命'",
        "edit: SIMP[1552] -> TRAD[1552]: '你算了吧，整天都说单挑' -> '你算了吧\\u3000整天都说单挑'",
        "edit: SIMP[1560] -> TRAD[1560]: '但是她再也不做“野鸡”' -> '但是她再也不做「野鸡」'",
    ]
