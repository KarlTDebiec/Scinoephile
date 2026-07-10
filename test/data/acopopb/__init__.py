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
from scinoephile.lang.eng.ocr_fusion import OcrFusionPromptEng
from scinoephile.lang.eng.review import ReviewPromptEng
from scinoephile.lang.yue.ocr_fusion import (
    OcrFusionPromptYueHans,
    OcrFusionPromptYueHant,
)
from scinoephile.lang.yue.review import ReviewPromptYueHans, ReviewPromptYueHant
from scinoephile.lang.zho.ocr_fusion import (
    OcrFusionPromptZhoHans,
    OcrFusionPromptZhoHant,
)
from scinoephile.lang.zho.review import ReviewPromptZhoHans, ReviewPromptZhoHant
from scinoephile.llms.ocr_fusion import OcrFusionManager, OcrFusionPrompt
from scinoephile.llms.review import ReviewManager, ReviewPrompt
from test.helpers import test_data_root

__all__ = [
    "get_acopopb_eng_ocr_fusion_test_cases",
    "get_acopopb_eng_review_test_cases",
    "get_acopopb_yue_hans_ocr_fusion_test_cases",
    "get_acopopb_yue_hans_review_test_cases",
    "get_acopopb_yue_hant_ocr_fusion_test_cases",
    "get_acopopb_yue_hant_review_test_cases",
    "get_acopopb_yue_hant_simplify_review_test_cases",
    "get_acopopb_zho_hans_ocr_fusion_test_cases",
    "get_acopopb_zho_hans_review_test_cases",
    "get_acopopb_zho_hant_ocr_fusion_test_cases",
    "get_acopopb_zho_hant_review_test_cases",
    "get_acopopb_zho_hant_simplify_review_test_cases",
    "acopopb_eng",
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
    "acopopb_yue_simplify_expected_series_diff",
    "acopopb_zho_hans",
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
    "acopopb_zho_hant",
    "acopopb_zho_hant_ocr_fuse",
    "acopopb_zho_hant_ocr_fuse_clean",
    "acopopb_zho_hant_ocr_fuse_clean_validate",
    "acopopb_zho_hant_ocr_fuse_clean_validate_review",
    "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten",
    "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify",
    "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review",
    "acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize",
    "acopopb_zho_simplify_expected_series_diff",
    "acopopb_zho_hant_ocr_lens",
    "acopopb_zho_hant_ocr_lens_clean",
    "acopopb_zho_hant_ocr_paddle",
    "acopopb_zho_hant_ocr_paddle_clean",
]

title_root = test_data_root / Path(__file__).parent.name
input_dir = title_root / "input"
output_dir = title_root / "output"


@cache
def get_acopopb_eng_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptEng,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB English OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "eng_ocr/lang/eng/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_acopopb_eng_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptEng, **kwargs: Any
) -> list[TestCase]:
    """Get ACOPOPB English review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "eng_ocr/lang/eng/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_acopopb_yue_hans_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptYueHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB yue-Hans OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hans_ocr/lang/yue/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_acopopb_yue_hans_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptYueHans, **kwargs: Any
) -> list[TestCase]:
    """Get ACOPOPB yue-Hans review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hans_ocr/lang/yue/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_acopopb_yue_hant_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptYueHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB yue-Hant OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hant_ocr/lang/yue/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_acopopb_yue_hant_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptYueHant, **kwargs: Any
) -> list[TestCase]:
    """Get ACOPOPB yue-Hant review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hant_ocr/lang/yue/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_acopopb_yue_hant_simplify_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptYueHans, **kwargs: Any
) -> list[TestCase]:
    """Get ACOPOPB yue-Hant simplification review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hant_ocr/lang/yue/simplify_review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_acopopb_zho_hans_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB zho-Hans OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hans_ocr/lang/zho/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_acopopb_zho_hans_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptZhoHans, **kwargs: Any
) -> list[TestCase]:
    """Get ACOPOPB zho-Hans review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hans_ocr/lang/zho/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_acopopb_zho_hant_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPOPB zho-Hant OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_acopopb_zho_hant_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptZhoHant, **kwargs: Any
) -> list[TestCase]:
    """Get ACOPOPB zho-Hant review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_acopopb_zho_hant_simplify_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptZhoHans, **kwargs: Any
) -> list[TestCase]:
    """Get ACOPOPB zho-Hant simplification review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/simplify_review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@fixture
def acopopb_eng() -> Series:
    """ACOPOPB English subtitles."""
    return Series.load(input_dir / "eng.srt")


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
    """ACOPOPB bilingual yue-Hans and English subtitles."""
    return Series.load(output_dir / "yue-Hans_eng.srt")


@fixture
def acopopb_yue_hans_ocr_fuse() -> Series:
    """ACOPOPB yue-Hans fused subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse.srt")


@fixture
def acopopb_yue_hans_ocr_fuse_clean() -> Series:
    """ACOPOPB yue-Hans fused and cleaned subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean.srt")


@fixture
def acopopb_yue_hans_ocr_fuse_clean_validate() -> Series:
    """ACOPOPB yue-Hans fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean_validate.srt")


@fixture
def acopopb_yue_hans_ocr_fuse_clean_validate_review() -> Series:
    """ACOPOPB yue-Hans fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean_validate_review.srt")


@fixture
def acopopb_yue_hans_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPOPB yue-Hans fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acopopb_yue_hans_ocr_fuse_clean_validate_review_flatten_romanize() -> Series:
    """ACOPOPB yue-Hans fused/cleaned/validated/reviewed/flattened romanized subtitles."""
    return Series.load(
        output_dir / "yue-Hans_ocr/fuse_clean_validate_review_flatten_romanize.srt"
    )


@fixture
def acopopb_yue_hans_ocr_lens() -> Series:
    """ACOPOPB yue-Hans subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "yue-Hans_ocr/lens.srt")


@fixture
def acopopb_yue_hans_ocr_lens_clean() -> Series:
    """ACOPOPB yue-Hans Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hans_ocr/lens_clean.srt")


@fixture
def acopopb_yue_hans_ocr_paddle() -> Series:
    """ACOPOPB yue-Hans subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "yue-Hans_ocr/paddle.srt")


@fixture
def acopopb_yue_hans_ocr_paddle_clean() -> Series:
    """ACOPOPB yue-Hans PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hans_ocr/paddle_clean.srt")


@fixture
def acopopb_yue_hant_ocr_fuse() -> Series:
    """ACOPOPB yue-Hant fused subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse.srt")


@fixture
def acopopb_yue_hant_ocr_fuse_clean() -> Series:
    """ACOPOPB yue-Hant fused and cleaned subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean.srt")


@fixture
def acopopb_yue_hant_ocr_fuse_clean_validate() -> Series:
    """ACOPOPB yue-Hant fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean_validate.srt")


@fixture
def acopopb_yue_hant_ocr_fuse_clean_validate_review() -> Series:
    """ACOPOPB yue-Hant fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean_validate_review.srt")


@fixture
def acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPOPB yue-Hant fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify() -> Series:
    """ACOPOPB yue-Hant simplified fused/cleaned/validated/reviewed/flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hant_ocr" / "fuse_clean_validate_review_flatten_simplify.srt"
    )


@fixture
def acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """ACOPOPB yue-Hant simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "yue-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@fixture
def acopopb_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize() -> (
    Series
):
    """ACOPOPB yue-Hant simplified/reviewed fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir
        / "yue-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
    )


@fixture
def acopopb_yue_hant_ocr_lens() -> Series:
    """ACOPOPB yue-Hant subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "yue-Hant_ocr/lens.srt")


@fixture
def acopopb_yue_hant_ocr_lens_clean() -> Series:
    """ACOPOPB yue-Hant Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hant_ocr/lens_clean.srt")


@fixture
def acopopb_yue_hant_ocr_paddle() -> Series:
    """ACOPOPB yue-Hant subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "yue-Hant_ocr/paddle.srt")


@fixture
def acopopb_yue_hant_ocr_paddle_clean() -> Series:
    """ACOPOPB yue-Hant PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hant_ocr/paddle_clean.srt")


@fixture
def acopopb_zho_hans() -> Series:
    """ACOPOPB zho-Hans subtitles."""
    return Series.load(input_dir / "zho-Hans.srt")


@fixture
def acopopb_zho_hans_eng() -> Series:
    """ACOPOPB bilingual zho-Hans and English subtitles."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


@fixture
def acopopb_zho_hans_ocr_fuse() -> Series:
    """ACOPOPB zho-Hans fused subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse.srt")


@fixture
def acopopb_zho_hans_ocr_fuse_clean() -> Series:
    """ACOPOPB zho-Hans fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean.srt")


@fixture
def acopopb_zho_hans_ocr_fuse_clean_validate() -> Series:
    """ACOPOPB zho-Hans fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate.srt")


@fixture
def acopopb_zho_hans_ocr_fuse_clean_validate_review() -> Series:
    """ACOPOPB zho-Hans fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate_review.srt")


@fixture
def acopopb_zho_hans_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPOPB zho-Hans fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acopopb_zho_hans_ocr_fuse_clean_validate_review_flatten_romanize() -> Series:
    """ACOPOPB zho-Hans fused/cleaned/validated/reviewed/flattened romanized subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten_romanize.srt"
    )


@fixture
def acopopb_zho_hans_ocr_lens() -> Series:
    """ACOPOPB zho-Hans subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hans_ocr/lens.srt")


@fixture
def acopopb_zho_hans_ocr_lens_clean() -> Series:
    """ACOPOPB zho-Hans Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/lens_clean.srt")


@fixture
def acopopb_zho_hans_ocr_paddle() -> Series:
    """ACOPOPB zho-Hans subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle.srt")


@fixture
def acopopb_zho_hans_ocr_paddle_clean() -> Series:
    """ACOPOPB zho-Hans PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle_clean.srt")


@fixture
def acopopb_zho_hant() -> Series:
    """ACOPOPB zho-Hant subtitles."""
    return Series.load(input_dir / "zho-Hant.srt")


@fixture
def acopopb_zho_hant_ocr_fuse() -> Series:
    """ACOPOPB zho-Hant fused subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse.srt")


@fixture
def acopopb_zho_hant_ocr_fuse_clean() -> Series:
    """ACOPOPB zho-Hant fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean.srt")


@fixture
def acopopb_zho_hant_ocr_fuse_clean_validate() -> Series:
    """ACOPOPB zho-Hant fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate.srt")


@fixture
def acopopb_zho_hant_ocr_fuse_clean_validate_review() -> Series:
    """ACOPOPB zho-Hant fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate_review.srt")


@fixture
def acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPOPB zho-Hant fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )


@fixture
def acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify() -> Series:
    """ACOPOPB zho-Hant simplified fused/cleaned/validated/reviewed/flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr" / "fuse_clean_validate_review_flatten_simplify.srt"
    )


@fixture
def acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """ACOPOPB zho-Hant simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@fixture
def acopopb_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize() -> (
    Series
):
    """ACOPOPB zho-Hant simplified/reviewed fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
    )


@fixture
def acopopb_zho_hant_ocr_lens() -> Series:
    """ACOPOPB zho-Hant subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hant_ocr/lens.srt")


@fixture
def acopopb_zho_hant_ocr_lens_clean() -> Series:
    """ACOPOPB zho-Hant Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/lens_clean.srt")


@fixture
def acopopb_zho_hant_ocr_paddle() -> Series:
    """ACOPOPB zho-Hant subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle.srt")


@fixture
def acopopb_zho_hant_ocr_paddle_clean() -> Series:
    """ACOPOPB zho-Hant PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle_clean.srt")


@fixture
def acopopb_yue_simplify_expected_series_diff() -> list[str]:
    """Expected differences for ACOPOPB Yue Simplified vs Traditional subtitles."""
    return []


@fixture
def acopopb_zho_simplify_expected_series_diff() -> list[str]:
    """Expected differences for ACOPOPB Zho Simplified vs Traditional subtitles."""
    return []
