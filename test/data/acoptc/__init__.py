#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test data for ACOPTC."""

# ruff: noqa: E501

from __future__ import annotations

from functools import cache
from pathlib import Path
from typing import Any

import pytest

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
    "acoptc_zho_hant_ocr_lens",
    "acoptc_zho_hant_ocr_lens_clean",
    "acoptc_zho_hant_ocr_paddle",
    "acoptc_zho_hant_ocr_paddle_clean",
]

title_root = test_data_root / Path(__file__).parent.name
input_path = title_root / "input"
output_dir = title_root / "output"


@pytest.fixture
def acoptc_eng() -> Series:
    """ACOPTC English subtitles."""
    return Series.load(input_path / "eng.srt")


@pytest.fixture
def acoptc_zho_hans() -> Series:
    """ACOPTC 简体中文 subtitles."""
    return Series.load(input_path / "zho-Hans.srt")


@pytest.fixture
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


@pytest.fixture
def acoptc_eng_ocr_fuse() -> Series:
    """ACOPTC English fused subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse.srt")


@pytest.fixture
def acoptc_eng_ocr_fuse_clean() -> Series:
    """ACOPTC English fused and cleaned subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean.srt")


@pytest.fixture
def acoptc_eng_ocr_fuse_clean_validate() -> Series:
    """ACOPTC English fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate.srt")


@pytest.fixture
def acoptc_eng_ocr_fuse_clean_validate_review() -> Series:
    """ACOPTC English fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate_review.srt")


@pytest.fixture
def acoptc_eng_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPTC English fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(output_dir / "eng_ocr/fuse_clean_validate_review_flatten.srt")


@pytest.fixture
def acoptc_eng_ocr_lens() -> Series:
    """ACOPTC English subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "eng_ocr/lens.srt")


@pytest.fixture
def acoptc_eng_ocr_lens_clean() -> Series:
    """ACOPTC English Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "eng_ocr/lens_clean.srt")


@pytest.fixture
def acoptc_eng_ocr_tesseract() -> Series:
    """ACOPTC English subtitles OCRed using Tesseract."""
    return Series.load(output_dir / "eng_ocr/tesseract.srt")


@pytest.fixture
def acoptc_eng_ocr_tesseract_clean() -> Series:
    """ACOPTC English Tesseract OCR subtitles, cleaned."""
    return Series.load(output_dir / "eng_ocr/tesseract_clean.srt")


@pytest.fixture
def acoptc_yue_hans_eng() -> Series:
    """ACOPTC bilingual 简体粤文 and English subtitles."""
    return Series.load(output_dir / "yue-Hans_eng.srt")


@pytest.fixture
def acoptc_yue_hans_ocr_fuse() -> Series:
    """ACOPTC 简体粤文 fused subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse.srt")


@pytest.fixture
def acoptc_yue_hans_ocr_fuse_clean() -> Series:
    """ACOPTC 简体粤文 fused and cleaned subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean.srt")


@pytest.fixture
def acoptc_yue_hans_ocr_fuse_clean_validate() -> Series:
    """ACOPTC 简体粤文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean_validate.srt")


@pytest.fixture
def acoptc_yue_hans_ocr_fuse_clean_validate_review() -> Series:
    """ACOPTC 简体粤文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "yue-Hans_ocr/fuse_clean_validate_review.srt")


@pytest.fixture
def acoptc_yue_hans_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPTC 简体粤文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )


@pytest.fixture
def acoptc_yue_hans_ocr_fuse_clean_validate_review_flatten_romanize() -> Series:
    """ACOPTC 简体粤文 fused/cleaned/validated/reviewed/flattened romanized subtitles."""
    return Series.load(
        output_dir / "yue-Hans_ocr/fuse_clean_validate_review_flatten_romanize.srt"
    )


@pytest.fixture
def acoptc_yue_hans_ocr_lens() -> Series:
    """ACOPTC 简体粤文 subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "yue-Hans_ocr/lens.srt")


@pytest.fixture
def acoptc_yue_hans_ocr_lens_clean() -> Series:
    """ACOPTC 简体粤文 Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hans_ocr/lens_clean.srt")


@pytest.fixture
def acoptc_yue_hans_ocr_paddle() -> Series:
    """ACOPTC 简体粤文 subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "yue-Hans_ocr/paddle.srt")


@pytest.fixture
def acoptc_yue_hans_ocr_paddle_clean() -> Series:
    """ACOPTC 简体粤文 PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hans_ocr/paddle_clean.srt")


@pytest.fixture
def acoptc_yue_hant_ocr_fuse() -> Series:
    """ACOPTC 繁體粵文 fused subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse.srt")


@pytest.fixture
def acoptc_yue_hant_ocr_fuse_clean() -> Series:
    """ACOPTC 繁體粵文 fused and cleaned subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean.srt")


@pytest.fixture
def acoptc_yue_hant_ocr_fuse_clean_validate() -> Series:
    """ACOPTC 繁體粵文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean_validate.srt")


@pytest.fixture
def acoptc_yue_hant_ocr_fuse_clean_validate_review() -> Series:
    """ACOPTC 繁體粵文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "yue-Hant_ocr/fuse_clean_validate_review.srt")


@pytest.fixture
def acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPTC 繁體粵文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )


@pytest.fixture
def acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify() -> Series:
    """ACOPTC 繁體粵文 simplified fused/cleaned/validated/reviewed/flattened subtitles."""
    return Series.load(
        output_dir / "yue-Hant_ocr" / "fuse_clean_validate_review_flatten_simplify.srt"
    )


@pytest.fixture
def acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """ACOPTC 繁體粵文 simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "yue-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@pytest.fixture
def acoptc_yue_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize() -> (
    Series
):
    """ACOPTC 繁體粵文 simplified/reviewed fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir
        / "yue-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
    )


@pytest.fixture
def acoptc_yue_hant_ocr_lens() -> Series:
    """ACOPTC 繁體粵文 subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "yue-Hant_ocr/lens.srt")


@pytest.fixture
def acoptc_yue_hant_ocr_lens_clean() -> Series:
    """ACOPTC 繁體粵文 Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hant_ocr/lens_clean.srt")


@pytest.fixture
def acoptc_yue_hant_ocr_paddle() -> Series:
    """ACOPTC 繁體粵文 subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "yue-Hant_ocr/paddle.srt")


@pytest.fixture
def acoptc_yue_hant_ocr_paddle_clean() -> Series:
    """ACOPTC 繁體粵文 PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "yue-Hant_ocr/paddle_clean.srt")


@pytest.fixture
def acoptc_zho_hans_eng() -> Series:
    """ACOPTC bilingual 简体中文 and English subtitles."""
    return Series.load(output_dir / "zho-Hans_eng.srt")


@pytest.fixture
def acoptc_zho_hans_ocr_fuse() -> Series:
    """ACOPTC 简体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse.srt")


@pytest.fixture
def acoptc_zho_hans_ocr_fuse_clean() -> Series:
    """ACOPTC 简体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean.srt")


@pytest.fixture
def acoptc_zho_hans_ocr_fuse_clean_validate() -> Series:
    """ACOPTC 简体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate.srt")


@pytest.fixture
def acoptc_zho_hans_ocr_fuse_clean_validate_review() -> Series:
    """ACOPTC 简体中文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hans_ocr/fuse_clean_validate_review.srt")


@pytest.fixture
def acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPTC 简体中文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"
    )


@pytest.fixture
def acoptc_zho_hans_ocr_fuse_clean_validate_review_flatten_romanize() -> Series:
    """ACOPTC 简体中文 fused/cleaned/validated/reviewed/flattened romanized subtitles."""
    return Series.load(
        output_dir / "zho-Hans_ocr/fuse_clean_validate_review_flatten_romanize.srt"
    )


@pytest.fixture
def acoptc_zho_hans_ocr_lens() -> Series:
    """ACOPTC 简体中文 subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hans_ocr/lens.srt")


@pytest.fixture
def acoptc_zho_hans_ocr_lens_clean() -> Series:
    """ACOPTC 简体中文 Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/lens_clean.srt")


@pytest.fixture
def acoptc_zho_hans_ocr_paddle() -> Series:
    """ACOPTC 简体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle.srt")


@pytest.fixture
def acoptc_zho_hans_ocr_paddle_clean() -> Series:
    """ACOPTC 简体中文 PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hans_ocr/paddle_clean.srt")


@pytest.fixture
def acoptc_zho_hant_ocr_fuse() -> Series:
    """ACOPTC 繁体中文 fused subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse.srt")


@pytest.fixture
def acoptc_zho_hant_ocr_fuse_clean() -> Series:
    """ACOPTC 繁体中文 fused and cleaned subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean.srt")


@pytest.fixture
def acoptc_zho_hant_ocr_fuse_clean_validate() -> Series:
    """ACOPTC 繁体中文 fused, cleaned, and validated subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate.srt")


@pytest.fixture
def acoptc_zho_hant_ocr_fuse_clean_validate_review() -> Series:
    """ACOPTC 繁体中文 fused, cleaned, validated, and reviewed subtitles."""
    return Series.load(output_dir / "zho-Hant_ocr/fuse_clean_validate_review.srt")


@pytest.fixture
def acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten() -> Series:
    """ACOPTC 繁体中文 fused, cleaned, validated, reviewed, and flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )


@pytest.fixture
def acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify() -> Series:
    """ACOPTC 繁体中文 simplified fused/cleaned/validated/reviewed/flattened subtitles."""
    return Series.load(
        output_dir / "zho-Hant_ocr" / "fuse_clean_validate_review_flatten_simplify.srt"
    )


@pytest.fixture
def acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review() -> Series:
    """ACOPTC 繁体中文 simplified/reviewed fused/cleaned subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review.srt"
    )


@pytest.fixture
def acoptc_zho_hant_ocr_fuse_clean_validate_review_flatten_simplify_review_romanize() -> (
    Series
):
    """ACOPTC 繁体中文 simplified/reviewed fused/cleaned romanized subtitles."""
    return Series.load(
        output_dir
        / "zho-Hant_ocr"
        / "fuse_clean_validate_review_flatten_simplify_review_romanize.srt"
    )


@pytest.fixture
def acoptc_zho_hant_ocr_lens() -> Series:
    """ACOPTC 繁体中文 subtitles OCRed using Google Lens."""
    return Series.load(output_dir / "zho-Hant_ocr/lens.srt")


@pytest.fixture
def acoptc_zho_hant_ocr_lens_clean() -> Series:
    """ACOPTC 繁体中文 Google Lens OCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/lens_clean.srt")


@pytest.fixture
def acoptc_zho_hant_ocr_paddle() -> Series:
    """ACOPTC 繁体中文 subtitles OCRed using PaddleOCR."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle.srt")


@pytest.fixture
def acoptc_zho_hant_ocr_paddle_clean() -> Series:
    """ACOPTC 繁体中文 PaddleOCR subtitles, cleaned."""
    return Series.load(output_dir / "zho-Hant_ocr/paddle_clean.srt")
