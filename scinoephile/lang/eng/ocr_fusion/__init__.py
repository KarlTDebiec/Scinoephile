#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English OCR fusion."""

from __future__ import annotations

from logging import warning
from typing import Any

from scinoephile.core import Series
from scinoephile.core.pairwise import PairwisePrompt, PairwiseReviewer, PairwiseTestCase

from .prompts import EngOcrFusionPrompt

__all__ = [
    "EngOcrFusionPrompt",
    "get_default_eng_ocr_fusion_test_cases",
    "get_eng_ocr_fuser",
    "get_eng_ocr_fused",
]


# noinspection PyUnusedImports
def get_default_eng_ocr_fusion_test_cases(
    prompt_cls: type[PairwisePrompt] = EngOcrFusionPrompt,
) -> list[PairwiseTestCase]:
    """Get default English OCR fusion test cases included with package.

    Arguments:
        prompt_cls: text for LLM correspondence
    Returns:
        default test cases
    """
    try:
        from test.data.kob import get_kob_eng_ocr_fusion_test_cases  # noqa: PLC0415
        from test.data.mlamd import get_mlamd_eng_ocr_fusion_test_cases  # noqa: PLC0415
        from test.data.mnt import get_mnt_eng_ocr_fusion_test_cases  # noqa: PLC0415
        from test.data.t import get_t_eng_ocr_fusion_test_cases  # noqa: PLC0415

        return (
            get_kob_eng_ocr_fusion_test_cases(prompt_cls)
            + get_mlamd_eng_ocr_fusion_test_cases(prompt_cls)
            + get_mnt_eng_ocr_fusion_test_cases(prompt_cls)
            + get_t_eng_ocr_fusion_test_cases(prompt_cls)
        )
    except ImportError as exc:
        warning(f"Default test cases not available for English OCR fusion:\n{exc}")
    return []


def get_eng_ocr_fused(
    lens: Series,
    tesseract: Series,
    reviewer: PairwiseReviewer | None = None,
    **kwargs: Any,
) -> Series:
    """Get English series fused from Google Lens and Tesseract OCR outputs.

    Arguments:
        lens: subtitles OCRed using Google Lens
        tesseract: subtitles OCRed using Tesseract
        reviewer: PairwiseReviewer to use
        kwargs: additional keyword arguments for PairwiseReviewer.review
    Returns:
        fused series
    """
    if reviewer is None:
        reviewer = get_eng_ocr_fuser()
    return reviewer.review(lens, tesseract, **kwargs)


def get_eng_ocr_fuser(
    prompt_cls: type[EngOcrFusionPrompt] = EngOcrFusionPrompt,
    default_test_cases: list[PairwiseTestCase] | None = None,
    **kwargs: Any,
) -> PairwiseReviewer:
    """Get a PairwiseReviewer with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        default_test_cases: default test cases
        kwargs: additional keyword arguments for PairwiseReviewer
    Returns:
        PairwiseReviewer with provided configuration
    """
    if default_test_cases is None:
        default_test_cases = get_default_eng_ocr_fusion_test_cases(prompt_cls)
    return PairwiseReviewer(
        prompt_cls=prompt_cls,
        default_test_cases=default_test_cases,
        **kwargs,
    )
