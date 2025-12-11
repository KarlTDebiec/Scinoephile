#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Zhongwen OCR fusion."""

from __future__ import annotations

from typing import Any

from scinoephile.core import Series

from .answer import ZhongwenFusionAnswer
from .answer2 import ZhongwenFusionAnswer2
from .fuser import ZhongwenFuser
from .fuser2 import ZhongwenFuser2
from .llm_queryer import ZhongwenFusionLLMQueryer
from .prompt import ZhongwenFusionPrompt
from .prompt2 import ZhongwenFusionPrompt2
from .query import ZhongwenFusionQuery
from .query2 import ZhongwenFusionQuery2
from .test_case import ZhongwenFusionTestCase
from .test_case2 import ZhongwenFusionTestCase2

__all__ = [
    "ZhongwenFuser",
    "ZhongwenFuser2",
    "ZhongwenFusionAnswer",
    "ZhongwenFusionAnswer2",
    "ZhongwenFusionLLMQueryer",
    "ZhongwenFusionPrompt",
    "ZhongwenFusionPrompt2",
    "ZhongwenFusionQuery",
    "ZhongwenFusionQuery2",
    "ZhongwenFusionTestCase",
    "ZhongwenFusionTestCase2",
    "get_zhongwen_ocr_fused",
    "get_zhongwen_ocr_fused2",
    "migrate_zhongwen_ocr_fusion_v1_to_v2",
]


def get_zhongwen_ocr_fused(
    lens: Series,
    paddle: Series,
    fuser: ZhongwenFuser | None = None,
    **kwargs: Any,
) -> Series:
    """Get OCRed Zhongwen series fused from Google Lens and PaddleOCR outputs.

    Arguments:
        lens: subtitles OCRed using Google Lens
        paddle: subtitles OCRed using PaddleOCR
        fuser: ZhongwenFuser to use
        kwargs: additional keyword arguments for ZhongwenFuser.fuse
    Returns:
        Fused series
    """
    if fuser is None:
        fuser = ZhongwenFuser()
    fused = fuser.fuse(lens, paddle, **kwargs)
    return fused


def get_zhongwen_ocr_fused2(
    lens: Series,
    paddle: Series,
    fuser: ZhongwenFuser | None = None,
    **kwargs: Any,
) -> Series:
    """Get OCRed Zhongwen series fused from Google Lens and PaddleOCR outputs.

    Arguments:
        lens: subtitles OCRed using Google Lens
        paddle: subtitles OCRed using PaddleOCR
        fuser: ZhongwenFuser to use
        kwargs: additional keyword arguments for ZhongwenFuser.fuse
    Returns:
        Fused series
    """
    if fuser is None:
        fuser = ZhongwenFuser2()
    fused = fuser.fuse(lens, paddle, **kwargs)
    return fused


def migrate_zhongwen_ocr_fusion_v1_to_v2(
    test_cases: list[ZhongwenFusionTestCase],
) -> list[ZhongwenFusionTestCase2]:
    """Migrate Zhongwen OCR fusion from v1 to v2.

    Arguments:
        test_cases: list of ZhongwenFusionTestCase to migrate
    Returns:
        list of ZhongwenFusionTestCase2
    """
    test_case_2_cls = ZhongwenFusionTestCase2.get_test_case_cls()
    query_2_cls = test_case_2_cls.query_cls
    answer_2_cls = test_case_2_cls.answer_cls

    test_case_2s: list[ZhongwenFusionTestCase2] = []
    for test_case in test_cases:
        query_2 = query_2_cls(lens=test_case.lens, paddle=test_case.paddle)
        answer_2 = answer_2_cls(ronghe=test_case.ronghe, beizhu=test_case.beizhu)
        test_case_2 = test_case_2_cls(
            query=query_2,
            answer=answer_2,
            difficulty=test_case.difficulty,
            prompt=test_case.prompt,
            verified=test_case.verified,
        )
        test_case_2s.append(test_case_2)

    return test_case_2s
