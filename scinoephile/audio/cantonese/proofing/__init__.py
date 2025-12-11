#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Cantonese audio transcription proofing."""

from __future__ import annotations

from .answer import ProofingAnswer
from .answer2 import ProofingAnswer2
from .llm_queryer import ProofingLLMQueryer
from .prompt import ProofingPrompt
from .prompt2 import ProofingPrompt2
from .query import ProofingQuery
from .query2 import ProofingQuery2
from .test_case import ProofingTestCase
from .test_case2 import ProofingTestCase2

__all__ = [
    "ProofingAnswer",
    "ProofingLLMQueryer",
    "ProofingPrompt",
    "ProofingQuery",
    "ProofingTestCase",
    "ProofingAnswer2",
    "ProofingPrompt2",
    "ProofingQuery2",
    "ProofingTestCase2",
    "migrate_proofing_v1_to_v2",
]


def migrate_proofing_v1_to_v2(
    test_cases: list[ProofingTestCase],
) -> list[ProofingTestCase2]:
    """Migrate proofing test cases from v1 to v2.

    Arguments:
        test_cases: v1 proofing test cases
    Returns:
        v2 proofing test cases
    """
    test_case_2_cls = ProofingTestCase2.get_test_case_cls()
    query_2_cls = test_case_2_cls.query_cls
    answer_2_cls = test_case_2_cls.answer_cls

    test_case_2s: list[ProofingTestCase2] = []
    for test_case in test_cases:
        query_2 = query_2_cls(
            zhongwen=test_case.query.zhongwen,
            yuewen=test_case.query.yuewen,
        )
        answer_2 = answer_2_cls(
            yuewen_proofread=test_case.answer.yuewen_proofread,
            note=test_case.answer.note,
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
