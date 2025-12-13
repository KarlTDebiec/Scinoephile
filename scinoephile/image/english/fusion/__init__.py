#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English OCR fusion."""

from __future__ import annotations

from collections.abc import Sequence
from logging import warning
from pathlib import Path
from typing import Any

from scinoephile.core import Series
from scinoephile.image.fusion import FusionFuser, FusionPrompt, FusionTestCase

from .prompt import EnglishFusionPrompt

__all__ = [
    "EnglishFusionPrompt",
    "get_default_eng_fusion_test_cases",
    "get_english_fuser",
    "get_english_ocr_fused",
]


def get_default_eng_fusion_test_cases(
    prompt_cls: type[FusionPrompt] = EnglishFusionPrompt,
) -> list[FusionTestCase]:
    """Get default English fusion test cases included with package.

    Arguments:
        prompt_cls: prompt class to use for test cases
    Returns:
        Test cases configured with the English fusion prompt.
    """
    try:
        # noinspection PyUnusedImports
        from test.data.kob import get_kob_eng_fusion_test_cases

        # noinspection PyUnusedImports
        from test.data.mlamd import get_mlamd_eng_fusion_test_cases

        # noinspection PyUnusedImports
        from test.data.mnt import get_mnt_eng_fusion_test_cases

        # noinspection PyUnusedImports
        from test.data.t import get_t_eng_fusion_test_cases

        return (
            get_kob_eng_fusion_test_cases(prompt_cls=prompt_cls)
            + get_mlamd_eng_fusion_test_cases(prompt_cls=prompt_cls)
            + get_mnt_eng_fusion_test_cases(prompt_cls=prompt_cls)
            + get_t_eng_fusion_test_cases(prompt_cls=prompt_cls)
        )
    except ImportError as exc:
        warning(
            (
                "Default test cases not available for English fusion, encountered "
                "exception:\n%s"
            ),
            exc,
        )
    return []


def get_english_fuser(
    test_cases: Sequence[FusionTestCase] | None = None,
    test_case_path: Path | None = None,
    auto_verify: bool = False,
    prompt_cls: type[EnglishFusionPrompt] = EnglishFusionPrompt,
    default_test_cases: list[FusionTestCase] | None = None,
) -> FusionFuser:
    """Create a fusion fuser configured for English prompts."""
    if test_cases is None and default_test_cases is None:
        default_test_cases = get_default_eng_fusion_test_cases(prompt_cls=prompt_cls)

    return FusionFuser(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        test_case_path=test_case_path,
        auto_verify=auto_verify,
        default_test_cases=default_test_cases,
    )


def get_english_ocr_fused(
    lens: Series,
    tesseract: Series,
    fuser: FusionFuser | None = None,
    **kwargs: Any,
) -> Series:
    """Get OCRed English series fused from Google Lens and Tesseract outputs.

    Arguments:
        lens: subtitles OCRed using Google Lens
        tesseract: subtitles OCRed using Tesseract
        fuser: FusionFuser to use
        kwargs: additional keyword arguments for FusionFuser.fuse
    Returns:
        Fused series
    """
    if fuser is None:
        fuser = get_english_fuser()
    fused = fuser.fuse(lens, tesseract, **kwargs)
    return fused
