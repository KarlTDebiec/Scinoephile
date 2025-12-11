#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Cantonese audio transcription shifting."""

from __future__ import annotations

from .answer import ShiftingAnswer
from .answer2 import ShiftingAnswer2
from .llm_queryer import ShiftingLLMQueryer
from .prompt import ShiftingPrompt
from .prompt2 import ShiftingPrompt2
from .query import ShiftingQuery
from .query2 import ShiftingQuery2
from .test_case import ShiftingTestCase
from .test_case2 import ShiftingTestCase2

__all__ = [
    "ShiftingAnswer",
    "ShiftingLLMQueryer",
    "ShiftingPrompt",
    "ShiftingQuery",
    "ShiftingTestCase",
    "ShiftingAnswer2",
    "ShiftingPrompt2",
    "ShiftingQuery2",
    "ShiftingTestCase2",
    "migrate_shifting_v1_to_v2",
]


def migrate_shifting_v1_to_v2(
    test_cases: list[ShiftingTestCase],
) -> list[ShiftingTestCase2]:
    """Migrate shifting test cases from v1 to v2.

    Arguments:
        test_cases: v1 shifting test cases
    Returns:
        v2 shifting test cases
    """
    test_case_2_cls = ShiftingTestCase2.get_test_case_cls()
    query_2_cls = test_case_2_cls.query_cls
    answer_2_cls = test_case_2_cls.answer_cls

    test_case_2s: list[ShiftingTestCase2] = []
    for test_case in test_cases:
        query_2 = query_2_cls(
            zhongwen_1=test_case.query.zhongwen_1,
            zhongwen_2=test_case.query.zhongwen_2,
            yuewen_1=test_case.query.yuewen_1,
            yuewen_2=test_case.query.yuewen_2,
        )
        answer_2 = answer_2_cls(
            yuewen_1_shifted=test_case.answer.yuewen_1_shifted,
            yuewen_2_shifted=test_case.answer.yuewen_2_shifted,
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
