#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 中文 proofreading."""

from __future__ import annotations

from typing import Any

from scinoephile.core.series import Series

from .answer import ZhongwenProofreadingAnswer
from .prompt import ZhongwenProofreadingPrompt
from .proofreader import ZhongwenProofreader
from .query import ZhongwenProofreadingQuery
from .test_case import ZhongwenProofreadingTestCase

__all__ = [
    "ZhongwenProofreader",
    "ZhongwenProofreadingAnswer",
    "ZhongwenProofreadingPrompt",
    "ZhongwenProofreadingQuery",
    "ZhongwenProofreadingTestCase",
    "get_zhongwen_proofread",
]


def get_zhongwen_proofread(
    series: Series, proofreader: ZhongwenProofreader | None = None, **kwargs: Any
) -> Series:
    """Get 中文 series proofread.

    Arguments:
        series: Series to proofread
        proofreader: ZhongwenProofreader to use
        kwargs: additional keyword arguments for ZhongwenProofreader.proofread
    Returns:
        proofread Series
    """
    if proofreader is None:
        proofreader = ZhongwenProofreader()

    proofread = proofreader.proofread(series, **kwargs)

    return proofread
