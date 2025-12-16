#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English fusion."""

from __future__ import annotations

from logging import warning
from typing import Any

from scinoephile.core import Series
from scinoephile.core.fusion import Fuser, FusionPrompt, FusionTestCase

from .prompts import EngOcrFusionPrompt

__all__ = [
    "EngOcrFusionPrompt",
    "get_default_eng_ocr_fusion_test_cases",
    "get_eng_ocr_fuser",
    "get_eng_ocr_fused",
]


# noinspection PyUnusedImports
def get_default_eng_ocr_fusion_test_cases(
    prompt_cls: type[FusionPrompt] = EngOcrFusionPrompt,
) -> list[FusionTestCase]:
    """Get default English fusion test cases included with package.

    Arguments:
        prompt_cls: prompt class to use for test cases
    Returns:
        default test cases
    """
    try:
        from test.data.kob import get_kob_eng_fusion_test_cases
        from test.data.mlamd import get_mlamd_eng_fusion_test_cases
        from test.data.mnt import get_mnt_eng_fusion_test_cases
        from test.data.t import get_t_eng_fusion_test_cases

        return (
            get_kob_eng_fusion_test_cases(prompt_cls)
            + get_mlamd_eng_fusion_test_cases(prompt_cls)
            + get_mnt_eng_fusion_test_cases(prompt_cls)
            + get_t_eng_fusion_test_cases(prompt_cls)
        )
    except ImportError as exc:
        warning(f"Default test cases not available for English fusion:\n{exc}")
    return []


def get_eng_ocr_fused(
    lens: Series,
    tesseract: Series,
    fuser: Fuser | None = None,
    **kwargs: Any,
) -> Series:
    """Get English series fused from Google Lens and Tesseract OCR outputs.

    Arguments:
        lens: subtitles OCRed using Google Lens
        tesseract: subtitles OCRed using Tesseract
        fuser: Fuser to use
        kwargs: additional keyword arguments for Fuser.fuse
    Returns:
        fused series
    """
    if fuser is None:
        fuser = get_eng_ocr_fuser()
    return fuser.fuse(lens, tesseract, **kwargs)


def get_eng_ocr_fuser(
    prompt_cls: type[EngOcrFusionPrompt] = EngOcrFusionPrompt,
    default_test_cases: list[FusionTestCase] | None = None,
    **kwargs: Any,
) -> Fuser:
    """Get a Fuser with provided configuration.

    Arguments:
        prompt_cls: prompt
        default_test_cases: default test cases
        kwargs: additional keyword arguments for Fuser
    Returns:
        Fuser with provided configuration
    """
    if default_test_cases is None:
        default_test_cases = get_default_eng_ocr_fusion_test_cases(prompt_cls)
    return Fuser(
        prompt_cls=prompt_cls,
        default_test_cases=default_test_cases,
        **kwargs,
    )
