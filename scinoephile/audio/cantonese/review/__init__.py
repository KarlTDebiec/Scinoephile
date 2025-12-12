#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Cantonese audio transcription review."""

from __future__ import annotations

from .answer import ReviewAnswer
from .answer2 import ReviewAnswer2
from .llm_queryer import ReviewLLMQueryer
from .prompt import ReviewPrompt
from .prompt2 import ReviewPrompt2
from .query import ReviewQuery
from .query2 import ReviewQuery2
from .test_case import ReviewTestCase
from .test_case2 import ReviewTestCase2

__all__ = [
    "ReviewAnswer",
    "ReviewLLMQueryer",
    "ReviewPrompt",
    "ReviewQuery",
    "ReviewTestCase",
    "ReviewAnswer2",
    "ReviewPrompt2",
    "ReviewQuery2",
    "ReviewTestCase2",
    "migrate_review_v1_to_v2",
]


def migrate_review_v1_to_v2(test_cases: list[ReviewTestCase]) -> list[ReviewTestCase2]:
    """Migrate from v1 to v2.

    Arguments:
        test_cases: TestCases to migrate
    Returns:
        list of TestCase2s
    """
    test_case_2s: list[ReviewTestCase2] = []
    for test_case in test_cases:
        test_case_2_cls = ReviewTestCase2.get_test_case_cls(
            size=test_case.size,
            prompt_cls=ReviewPrompt2,
        )
        query_2_cls = test_case_2_cls.query_cls
        answer_2_cls = test_case_2_cls.answer_cls
        query_attrs: dict[str, str] = {}
        answer_attrs: dict[str, str] = {}
        for idx in range(test_case.size):
            i = idx + 1

            query_attrs[f"zhongwen_{i}"] = getattr(test_case.query, f"zhongwen_{i}")
            query_attrs[f"yuewen_{i}"] = getattr(test_case.query, f"yuewen_{i}")
            answer_attrs[f"yuewen_revised_{i}"] = getattr(
                test_case.answer,
                f"yuewen_revised_{i}",
            )
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
