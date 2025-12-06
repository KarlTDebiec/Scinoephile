#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English proofreading."""

from __future__ import annotations

from typing import Any

from scinoephile.core.series import Series

from .answer import EnglishProofreadingAnswer
from .llm_queryer import EnglishProofreadingLLMQueryer
from .prompt import EnglishProofreadingPrompt
from .prompt2 import EnglishProofreadingPrompt2
from .proofreader import EnglishProofreader
from .proofreader2 import EnglishProofreader2
from .query import EnglishProofreadingQuery
from .test_case import EnglishProofreadingTestCase
from .test_case2 import EnglishProofreadingTestCase2

__all__ = [
    "EnglishProofreader",
    "EnglishProofreadingAnswer",
    "EnglishProofreadingLLMQueryer",
    "EnglishProofreadingPrompt",
    "EnglishProofreadingQuery",
    "EnglishProofreadingTestCase",
    "get_english_proofread",
    "get_english_proofread2",
    "migrate_english_proofreading_v1_to_v2",
]


def get_english_proofread(
    series: Series, proofreader: EnglishProofreader | None = None, **kwargs: Any
) -> Series:
    """Get English series proofread.

    Arguments:
        series: Series to proofread
        proofreader: EnglishProofreader to use
        kwargs: additional keyword arguments for EnglishProofreader.proofread
    Returns:
        proofread Series
    """
    if proofreader is None:
        proofreader = EnglishProofreader()

    proofread = proofreader.proofread(series, **kwargs)

    return proofread


def get_english_proofread2(
    series: Series, proofreader: EnglishProofreader2 | None = None, **kwargs: Any
) -> Series:
    """Get English series proofread.

    Arguments:
        series: Series to proofread
        proofreader: EnglishProofreader to use
        kwargs: additional keyword arguments for EnglishProofreader.proofread
    Returns:
        proofread Series
    """
    if proofreader is None:
        proofreader = EnglishProofreader2()

    proofread = proofreader.proofread(series, **kwargs)

    return proofread


def migrate_english_proofreading_v1_to_v2(
    test_cases: list[EnglishProofreadingTestCase],
) -> list[EnglishProofreadingTestCase2]:
    """Migrate English proofreading from v1 to v2.

    Arguments:
        test_cases: list of EnglishProofreadingTestCase to migrate
    Returns:
        list of EnglishProofreadingTestCase2
    """
    test_case_2s: list[EnglishProofreadingTestCase2] = []

    for test_case in test_cases:
        test_case_2_cls = EnglishProofreadingTestCase2.get_test_case_cls(
            size=test_case.size,
            prompt_cls=EnglishProofreadingPrompt2,
        )
        query_2_cls = test_case_2_cls.query_cls
        answer_2_cls = test_case_2_cls.answer_cls
        query_attrs: dict[str, str] = {}
        answer_attrs: dict[str, str] = {}
        for idx in range(test_case.size):
            i = idx + 1

            query_attrs[f"subtitle_{i}"] = getattr(test_case.query, f"subtitle_{i}")
            answer_attrs[f"revised_{i}"] = getattr(test_case.answer, f"revised_{i}")
            answer_attrs[f"note_{i}"] = getattr(test_case.answer, f"note_{i}")

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
