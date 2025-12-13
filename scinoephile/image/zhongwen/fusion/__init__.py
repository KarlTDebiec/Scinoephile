#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Zhongwen OCR fusion."""

from __future__ import annotations

from collections.abc import Sequence
from logging import warning
from pathlib import Path
from typing import Any

from scinoephile.core import Series
from scinoephile.image.fusion import FusionFuser, FusionPrompt, FusionTestCase

from .prompt import ZhongwenFusionPrompt

__all__ = [
    "ZhongwenFusionPrompt",
    "get_default_zho_fusion_test_cases",
    "get_zhongwen_fuser",
    "get_zhongwen_ocr_fused",
]


def get_default_zho_fusion_test_cases(
    prompt_cls: type[FusionPrompt] = ZhongwenFusionPrompt,
) -> list[FusionTestCase]:
    """Get default Zhongwen fusion test cases included with package.

    Arguments:
        prompt_cls: prompt class to use for test cases
    Returns:
        Test cases configured with the Zhongwen fusion prompt.
    """
    try:
        # noinspection PyUnusedImports
        from test.data.kob import get_kob_zho_fusion_test_cases

        # noinspection PyUnusedImports
        from test.data.mlamd import get_mlamd_zho_fusion_test_cases

        # noinspection PyUnusedImports
        from test.data.mnt import get_mnt_zho_fusion_test_cases

        # noinspection PyUnusedImports
        from test.data.t import get_t_zho_fusion_test_cases

        return (
            get_kob_zho_fusion_test_cases(prompt_cls=prompt_cls)
            + get_mlamd_zho_fusion_test_cases(prompt_cls=prompt_cls)
            + get_mnt_zho_fusion_test_cases(prompt_cls=prompt_cls)
            + get_t_zho_fusion_test_cases(prompt_cls=prompt_cls)
        )
    except ImportError as exc:
        warning(
            (
                "Default test cases not available for Zhongwen fusion, encountered "
                "exception:\n%s"
            ),
            exc,
        )
    return []


def get_zhongwen_fuser(
    test_cases: Sequence[FusionTestCase] | None = None,
    test_case_path: Path | None = None,
    auto_verify: bool = False,
    prompt_cls: type[ZhongwenFusionPrompt] = ZhongwenFusionPrompt,
    default_test_cases: list[FusionTestCase] | None = None,
) -> FusionFuser:
    """Create a fusion fuser configured for Zhongwen prompts."""
    if test_cases is None and default_test_cases is None:
        default_test_cases = get_default_zho_fusion_test_cases(prompt_cls=prompt_cls)

    return FusionFuser(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        test_case_path=test_case_path,
        auto_verify=auto_verify,
        default_test_cases=default_test_cases,
    )


def get_zhongwen_ocr_fused(
    lens: Series,
    paddle: Series,
    fuser: FusionFuser | None = None,
    **kwargs: Any,
) -> Series:
    """Get OCRed Zhongwen series fused from Google Lens and PaddleOCR outputs.

    Arguments:
        lens: subtitles OCRed using Google Lens
        paddle: subtitles OCRed using PaddleOCR
        fuser: FusionFuser to use
        kwargs: additional keyword arguments for FusionFuser.fuse
    Returns:
        Fused series
    """
    if fuser is None:
        fuser = get_zhongwen_fuser()
    fused = fuser.fuse(lens, paddle, **kwargs)
    return fused
