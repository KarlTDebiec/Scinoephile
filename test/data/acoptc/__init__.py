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
    "acoptc_eng",
    "acoptc_zho_hans",
    "acoptc_zho_hant",
    "get_acoptc_eng_ocr_fusion_test_cases",
    "get_acoptc_eng_review_test_cases",
    "get_acoptc_yue_hans_ocr_fusion_test_cases",
    "get_acoptc_yue_hans_review_test_cases",
    "get_acoptc_yue_hant_ocr_fusion_test_cases",
    "get_acoptc_yue_hant_review_test_cases",
    "get_acoptc_yue_hant_simplify_review_test_cases",
    "get_acoptc_zho_hans_ocr_fusion_test_cases",
    "get_acoptc_zho_hans_review_test_cases",
    "get_acoptc_zho_hant_ocr_fusion_test_cases",
    "get_acoptc_zho_hant_review_test_cases",
    "get_acoptc_zho_hant_simplify_review_test_cases",
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
def get_acoptc_eng_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptEng,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC English OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "eng_ocr/lang/eng/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_acoptc_eng_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptEng, **kwargs: Any
) -> list[TestCase]:
    """Get ACOPTC English review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "eng_ocr/lang/eng/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_acoptc_yue_hans_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptYueHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC yue-Hans OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hans_ocr/lang/yue/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_acoptc_yue_hans_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptYueHans, **kwargs: Any
) -> list[TestCase]:
    """Get ACOPTC yue-Hans review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hans_ocr/lang/yue/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_acoptc_yue_hant_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptYueHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC yue-Hant OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hant_ocr/lang/yue/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_acoptc_yue_hant_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptYueHant, **kwargs: Any
) -> list[TestCase]:
    """Get ACOPTC yue-Hant review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hant_ocr/lang/yue/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_acoptc_yue_hant_simplify_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptYueHans, **kwargs: Any
) -> list[TestCase]:
    """Get ACOPTC yue-Hant simplification review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "yue-Hant_ocr/lang/yue/simplify_review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_acoptc_zho_hans_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptZhoHans,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC zho-Hans OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hans_ocr/lang/zho/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_acoptc_zho_hans_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptZhoHans, **kwargs: Any
) -> list[TestCase]:
    """Get ACOPTC zho-Hans review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hans_ocr/lang/zho/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_acoptc_zho_hant_ocr_fusion_test_cases(
    prompt: OcrFusionPrompt = OcrFusionPromptZhoHant,
    **kwargs: Any,
) -> list[TestCase]:
    """Get ACOPTC zho-Hant OCR fusion test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/ocr_fusion.json"
    return load_test_cases_from_json(path, OcrFusionManager, prompt=prompt, **kwargs)


@cache
def get_acoptc_zho_hant_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptZhoHant, **kwargs: Any
) -> list[TestCase]:
    """Get ACOPTC zho-Hant review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


@cache
def get_acoptc_zho_hant_simplify_review_test_cases(
    prompt: ReviewPrompt = ReviewPromptZhoHans, **kwargs: Any
) -> list[TestCase]:
    """Get ACOPTC zho-Hant simplification review test cases.

    Arguments:
        prompt: text for LLM correspondence
        **kwargs: additional keyword arguments for load_test_cases_from_json
    Returns:
        test cases
    """
    path = output_dir / "zho-Hant_ocr/lang/zho/simplify_review.json"
    return load_test_cases_from_json(path, ReviewManager, prompt=prompt, **kwargs)


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
    return []
