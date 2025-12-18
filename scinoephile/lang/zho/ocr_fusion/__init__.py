#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 中文 OCR fusion."""

from __future__ import annotations

from logging import warning
from typing import Any

from scinoephile.core.subtitles import Series
from scinoephile.llms.pairwise import (
    DualSinglePrompt,
    DualSingleReviewer,
    DualSingleTestCase,
)

from .prompts import ZhoHansOcrFusionPrompt, ZhoHantOcrFusionPrompt

__all__ = [
    "ZhoHansOcrFusionPrompt",
    "ZhoHantOcrFusionPrompt",
    "get_default_zho_ocr_fusion_test_cases",
    "get_zho_ocr_fuser",
    "get_zho_ocr_fused",
]


# noinspection PyUnusedImports
def get_default_zho_ocr_fusion_test_cases(
    prompt_cls: type[DualSinglePrompt] = ZhoHansOcrFusionPrompt,
) -> list[DualSingleTestCase]:
    """Get default 中文 OCR fusion test cases included with package.

    Arguments:
        prompt_cls: text for LLM correspondence
    Returns:
        default test cases
    """
    try:
        from test.data.kob import get_kob_zho_ocr_fusion_test_cases  # noqa: PLC0415
        from test.data.mlamd import get_mlamd_zho_ocr_fusion_test_cases  # noqa: PLC0415
        from test.data.mnt import get_mnt_zho_ocr_fusion_test_cases  # noqa: PLC0415
        from test.data.t import get_t_zho_ocr_fusion_test_cases  # noqa: PLC0415

        return (
            get_kob_zho_ocr_fusion_test_cases(prompt_cls)
            + get_mlamd_zho_ocr_fusion_test_cases(prompt_cls)
            + get_mnt_zho_ocr_fusion_test_cases(prompt_cls)
            + get_t_zho_ocr_fusion_test_cases(prompt_cls)
        )
    except ImportError as exc:
        warning(f"Default test cases not available for 中文 OCR fusion:\n{exc}")
    return []


def get_zho_ocr_fused(
    lens: Series,
    paddle: Series,
    reviewer: DualSingleReviewer | None = None,
    **kwargs: Any,
) -> Series:
    """Get 中文 series fused from Google Lens and PaddleOCR outputs.

    Arguments:
        lens: subtitles OCRed using Google Lens
        paddle: subtitles OCRed using PaddleOCR
        reviewer: DualSingleReviewer to use
        kwargs: additional keyword arguments for DualSingleReviewer.review
    Returns:
        Fused series
    """
    if reviewer is None:
        reviewer = get_zho_ocr_fuser()
    return reviewer.review(lens, paddle, **kwargs)


def get_zho_ocr_fuser(
    prompt_cls: type[ZhoHansOcrFusionPrompt] = ZhoHansOcrFusionPrompt,
    default_test_cases: list[DualSingleTestCase] | None = None,
    **kwargs: Any,
) -> DualSingleReviewer:
    """Get a DualSingleReviewer with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        default_test_cases: default test cases
        kwargs: additional keyword arguments for DualSingleReviewer
    Returns:
        DualSingleReviewer with provided configuration
    """
    if default_test_cases is None:
        default_test_cases = get_default_zho_ocr_fusion_test_cases(prompt_cls)
    return DualSingleReviewer(
        prompt_cls=prompt_cls,
        default_test_cases=default_test_cases,
        **kwargs,
    )
