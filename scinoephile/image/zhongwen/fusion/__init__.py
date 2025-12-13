#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 中文 fusion."""

from __future__ import annotations

from logging import warning
from typing import Any

from scinoephile.core import Series
from scinoephile.image.fusion import Fuser, FusionPrompt, FusionTestCase

from .prompt import ZhongwenSimpFusionPrompt, ZhongwenTradFusionPrompt

__all__ = [
    "ZhongwenSimpFusionPrompt",
    "ZhongwenTradFusionPrompt",
    "get_default_zho_fusion_test_cases",
    "get_zho_fuser",
    "get_zhongwen_ocr_fused",
]


# noinspection PyUnusedImports
def get_default_zho_fusion_test_cases(
    prompt_cls: type[FusionPrompt] = ZhongwenSimpFusionPrompt,
) -> list[FusionTestCase]:
    """Get default 中文 fusion test cases included with package.

    Arguments:
        prompt_cls: prompt class to use for test cases
    Returns:
        default test cases
    """
    try:
        from test.data.kob import get_kob_zho_fusion_test_cases
        from test.data.mlamd import get_mlamd_zho_fusion_test_cases
        from test.data.mnt import get_mnt_zho_fusion_test_cases
        from test.data.t import get_t_zho_fusion_test_cases

        return (
            get_kob_zho_fusion_test_cases(prompt_cls)
            + get_mlamd_zho_fusion_test_cases(prompt_cls)
            + get_mnt_zho_fusion_test_cases(prompt_cls)
            + get_t_zho_fusion_test_cases(prompt_cls)
        )
    except ImportError:
        warning("Default test cases not available for 中文 fusion:\n{exc}")
    return []


def get_zhongwen_ocr_fused(
    lens: Series,
    paddle: Series,
    fuser: Fuser | None = None,
    **kwargs: Any,
) -> Series:
    """Get 中文 series fused from Google Lens and PaddleOCR outputs.

    Arguments:
        lens: subtitles OCRed using Google Lens
        paddle: subtitles OCRed using PaddleOCR
        fuser: Fuser to use
        kwargs: additional keyword arguments for Fuser.fuse
    Returns:
        Fused series
    """
    if fuser is None:
        fuser = get_zho_fuser()
    return fuser.fuse(lens, paddle, **kwargs)


def get_zho_fuser(
    prompt_cls: type[ZhongwenSimpFusionPrompt] = ZhongwenSimpFusionPrompt,
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
        default_test_cases = get_default_zho_fusion_test_cases(prompt_cls)
    return Fuser(
        prompt_cls=prompt_cls,
        default_test_cases=default_test_cases,
        **kwargs,
    )
