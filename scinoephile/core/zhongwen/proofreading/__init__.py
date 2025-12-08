#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 中文 proofreading."""

from __future__ import annotations

from typing import Any

from scinoephile.core.series import Series

from .answer import ZhongwenProofreadingAnswer
from .answer2 import ZhongwenProofreadingAnswer2
from .llm_queryer import ZhongwenProofreadingLLMQueryer
from .prompt import ZhongwenProofreadingPrompt
from .prompt2 import ZhongwenProofreadingPrompt2
from .proofreader import ZhongwenProofreader
from .proofreader2 import ZhongwenProofreader2
from .query import ZhongwenProofreadingQuery
from .query2 import ZhongwenProofreadingQuery2
from .test_case import ZhongwenProofreadingTestCase
from .test_case2 import ZhongwenProofreadingTestCase2

__all__ = [
    "ZhongwenProofreader",
    "ZhongwenProofreader2",
    "ZhongwenProofreadingAnswer",
    "ZhongwenProofreadingAnswer2",
    "ZhongwenProofreadingLLMQueryer",
    "ZhongwenProofreadingPrompt",
    "ZhongwenProofreadingPrompt2",
    "ZhongwenProofreadingQuery",
    "ZhongwenProofreadingQuery2",
    "ZhongwenProofreadingTestCase",
    "ZhongwenProofreadingTestCase2",
    "get_zhongwen_proofread",
    "get_zhongwen_proofread2",
    "migrate_zhongwen_proofreading_v1_to_v2",
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


def get_zhongwen_proofread2(
    series: Series, proofreader: ZhongwenProofreader2 | None = None, **kwargs: Any
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
        proofreader = ZhongwenProofreader2()

    proofread = proofreader.proofread(series, **kwargs)

    return proofread


def migrate_zhongwen_proofreading_v1_to_v2(
    test_cases: list[ZhongwenProofreadingTestCase],
) -> list[ZhongwenProofreadingTestCase2]:
    """Migrate 中文 proofreading from v1 to v2.

    Arguments:
        test_cases: list of ZhongwenProofreadingTestCase to migrate
    Returns:
        list of ZhongwenProofreadingTestCase2
    """
    test_case_2s: list[ZhongwenProofreadingTestCase2] = []

    for test_case in test_cases:
        test_case_2_cls = ZhongwenProofreadingTestCase2.get_test_case_cls(
            size=test_case.size,
            prompt_cls=ZhongwenProofreadingPrompt2,
        )
        query_2_cls = test_case_2_cls.query_cls
        answer_2_cls = test_case_2_cls.answer_cls
        query_attrs: dict[str, str] = {}
        answer_attrs: dict[str, str] = {}
        for idx in range(test_case.size):
            i = idx + 1

            query_attrs[f"zimu_{i}"] = getattr(test_case.query, f"zimu_{i}")
            answer_attrs[f"xiugai_{i}"] = getattr(test_case.answer, f"xiugai_{i}")
            answer_attrs[f"beizhu_{i}"] = getattr(test_case.answer, f"beizhu_{i}")

        query_2 = query_2_cls(**query_attrs)
        answer_2 = answer_2_cls(**answer_attrs)
        test_case_2 = test_case_2_cls(
            query=query_2,
            answer=answer_2,
            difficulty=test_case.difficulty,
            prompt=test_case.prompt,
            verified=test_case.verified,
        )
        test_case_2s.append(test_case_2)

    return test_case_2s
