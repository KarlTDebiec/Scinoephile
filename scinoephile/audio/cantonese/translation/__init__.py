#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Cantonese audio transcription translation."""

from __future__ import annotations

from .answer import TranslationAnswer
from .answer2 import TranslationAnswer2
from .llm_queryer import TranslationLLMQueryer
from .prompt import TranslationPrompt
from .prompt2 import TranslationPrompt2
from .query import TranslationQuery
from .query2 import TranslationQuery2
from .test_case import TranslationTestCase
from .test_case2 import TranslationTestCase2

__all__ = [
    "TranslationAnswer",
    "TranslationLLMQueryer",
    "TranslationPrompt",
    "TranslationQuery",
    "TranslationTestCase",
    "TranslationAnswer2",
    "TranslationPrompt2",
    "TranslationQuery2",
    "TranslationTestCase2",
    "migrate_translation_v1_to_v2",
]


def migrate_translation_v1_to_v2(
    test_cases: list[TranslationTestCase],
) -> list[TranslationTestCase2]:
    """Migrate from v1 to v2.

    Arguments:
        test_cases: TestCases to migrate
    Returns:
        list of TestCase2s
    """
    test_case_2s: list[TranslationTestCase2] = []
    for test_case in test_cases:
        test_case_2_cls = TranslationTestCase2.get_test_case_cls(
            size=test_case.size,
            missing=test_case.missing,
            prompt_cls=TranslationPrompt2,
        )
        query_2_cls = test_case_2_cls.query_cls
        answer_2_cls = test_case_2_cls.answer_cls
        query_attrs: dict[str, str] = {}
        answer_attrs: dict[str, str] = {}
        for idx in range(test_case.size):
            i = idx + 1

            query_attrs[f"zhongwen_{i}"] = getattr(test_case.query, f"zhongwen_{i}")
            if yuewen := getattr(test_case.query, f"yuewen_{i}", None):
                query_attrs[f"yuewen_{i}"] = yuewen
            else:
                yuewen = getattr(test_case.answer, f"yuewen_{i}")
                answer_attrs[f"yuewen_{i}"] = yuewen

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
