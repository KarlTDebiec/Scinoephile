#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Cantonese audio transcription merging."""

from __future__ import annotations

from .answer import MergingAnswer
from .answer2 import MergingAnswer2
from .llm_queryer import MergingLLMQueryer
from .prompt import MergingPrompt
from .prompt2 import MergingPrompt2
from .query import MergingQuery
from .query2 import MergingQuery2
from .test_case import MergingTestCase
from .test_case2 import MergingTestCase2

__all__ = [
    "MergingAnswer",
    "MergingLLMQueryer",
    "MergingPrompt",
    "MergingQuery",
    "MergingTestCase",
    "MergingAnswer2",
    "MergingPrompt2",
    "MergingQuery2",
    "MergingTestCase2",
    "migrate_merging_v1_to_v2",
]


def migrate_merging_v1_to_v2(
    test_cases: list[MergingTestCase],
) -> list[MergingTestCase2]:
    """Migrate merging test cases from v1 to v2.

    Arguments:
        test_cases: v1 merging test cases
    Returns:
        v2 merging test cases
    """
    test_case_2_cls = MergingTestCase2.get_test_case_cls()
    query_2_cls = test_case_2_cls.query_cls
    answer_2_cls = test_case_2_cls.answer_cls

    test_case_2s: list[MergingTestCase2] = []
    for test_case in test_cases:
        query_2 = query_2_cls(
            zhongwen=test_case.query.zhongwen,
            yuewen_to_merge=test_case.query.yuewen_to_merge,
        )
        answer_2 = answer_2_cls(
            yuewen_merged=test_case.answer.yuewen_merged,
        )
        test_case_2 = test_case_2_cls(
            query=query_2,
            answer=answer_2,
            difficulty=test_case.difficulty,
            prompt=test_case.prompt,
            verified=test_case.verified,
        )
        test_case_2s.append(test_case_2)

    return test_case_2s
