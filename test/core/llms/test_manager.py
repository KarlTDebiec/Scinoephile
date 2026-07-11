#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for shared LLM manager class factories."""

from __future__ import annotations

from pytest import raises

from scinoephile.core.llms import TestCase
from scinoephile.llms.punctuation import PunctuationManager, PunctuationPrompt
from scinoephile.llms.review import ReviewManager, ReviewPrompt, ReviewTestCase

_LOCALIZED_REVIEW_PROMPT = ReviewPrompt(
    subtitles="zimu",
    revisions="xiugai",
    index="xuhao",
    text="wenben",
    note="beizhu",
)
"""Review prompt using localized correspondence field names."""

_ALTERNATIVE_REVIEW_PROMPT = ReviewPrompt(
    subtitles="sources",
    revisions="corrections",
    index="position",
    text="content",
    note="explanation",
)
"""Review prompt using alternative correspondence field names."""

_LOCALIZED_PUNCTUATION_PROMPT = PunctuationPrompt(
    src_1="source_one",
    src_2="source_two",
    output="result",
)
"""Punctuation prompt using non-default correspondence field names."""


class _LegacyPunctuationManager(PunctuationManager):
    """Legacy manager fixture with test-case callbacks."""

    @staticmethod
    def get_auto_verified(model: TestCase) -> bool:
        """Automatically verify test cases that include an answer.

        Arguments:
            model: test case to inspect
        Returns:
            whether the test case should be automatically verified
        """
        return model.answer is not None

    @staticmethod
    def get_min_difficulty(model: TestCase) -> int:
        """Require difficulty two for test cases that include an answer.

        Arguments:
            model: test case to inspect
        Returns:
            minimum difficulty
        """
        if model.answer is not None:
            return 2
        return 0

    @staticmethod
    def validate_test_case(model: TestCase) -> TestCase:
        """Reject the sentinel invalid output.

        Arguments:
            model: test case to validate
        Returns:
            validated test case
        """
        if model.answer is None:
            return model
        prompt: PunctuationPrompt = getattr(model, "prompt")
        if getattr(model.answer, prompt.output) == "invalid":
            raise ValueError("Legacy test-case validator was called.")
        return model


def test_static_shape_factory_caches_and_isolates_prompt_aliases():
    """Static-shape classes should be cached without sharing prompt aliases."""
    localized_cls = ReviewManager.get_test_case_cls(_LOCALIZED_REVIEW_PROMPT)
    alternative_cls = ReviewManager.get_test_case_cls(_ALTERNATIVE_REVIEW_PROMPT)

    assert ReviewManager.get_test_case_cls(_LOCALIZED_REVIEW_PROMPT) is localized_cls
    assert localized_cls is not alternative_cls
    assert issubclass(localized_cls, ReviewTestCase)
    assert localized_cls.query_cls.model_fields["subtitles"].alias == "zimu"
    assert alternative_cls.query_cls.model_fields["subtitles"].alias == "sources"

    test_case = localized_cls.model_validate(
        {
            "query": {"subtitles": [{"index": 1, "text": "original"}]},
            "answer": {
                "revisions": [{"index": 1, "text": "corrected", "note": "typo"}]
            },
        }
    )
    assert test_case.query.model_dump(by_alias=True) == {
        "zimu": [{"xuhao": 1, "wenben": "original"}]
    }
    assert test_case.answer is not None
    assert test_case.answer.model_dump(by_alias=True) == {
        "xiugai": [{"xuhao": 1, "wenben": "corrected", "beizhu": "typo"}]
    }


def test_legacy_factory_preserves_prompt_shaped_models():
    """Legacy managers should retain prompt-named Python model fields."""
    test_case_cls = PunctuationManager.get_test_case_cls(_LOCALIZED_PUNCTUATION_PROMPT)

    assert (
        PunctuationManager.get_test_case_cls(_LOCALIZED_PUNCTUATION_PROMPT)
        is test_case_cls
    )
    assert set(test_case_cls.query_cls.model_fields) == {"source_one", "source_two"}
    assert set(test_case_cls.answer_cls.model_fields) == {"result"}

    test_case = test_case_cls.model_validate(
        {
            "query": {"source_one": ["Hello"], "source_two": "Hello"},
            "answer": {"result": "Hello"},
        }
    )
    assert test_case.query.model_dump() == {
        "source_one": ["Hello"],
        "source_two": "Hello",
    }
    assert test_case.answer is not None
    assert test_case.answer.model_dump() == {"result": "Hello"}


def test_legacy_factory_preserves_manager_callbacks():
    """Legacy test-case classes should retain manager-defined behavior."""
    test_case_cls = _LegacyPunctuationManager.get_test_case_cls(
        _LOCALIZED_PUNCTUATION_PROMPT
    )

    test_case = test_case_cls.model_validate(
        {
            "query": {"source_one": ["Hello"], "source_two": "Hello"},
            "answer": {"result": "Hello"},
        }
    )

    assert test_case.difficulty == 2
    assert test_case.get_auto_verified()
    with raises(ValueError, match="Legacy test-case validator was called"):
        test_case_cls.model_validate(
            {
                "query": {"source_one": ["Hello"], "source_two": "Hello"},
                "answer": {"result": "invalid"},
            }
        )
