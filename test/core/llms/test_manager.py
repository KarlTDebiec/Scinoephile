#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for shared LLM manager class factories."""

from __future__ import annotations

from pytest import mark, raises

from scinoephile.core.llms import Manager
from scinoephile.llms.delineation import DelineationManager
from scinoephile.llms.gap_translation import GapTranslationManager
from scinoephile.llms.guided_review import GuidedReviewManager
from scinoephile.llms.guided_translation import (
    GuidedTranslationManager,
    GuidedTranslationPrompt,
)
from scinoephile.llms.ocr_fusion import OcrFusionManager
from scinoephile.llms.pairwise_review import PairwiseReviewManager
from scinoephile.llms.punctuation import (
    PunctuationManager,
    PunctuationPrompt,
    PunctuationTestCase,
)
from scinoephile.llms.review import ReviewManager, ReviewPrompt, ReviewTestCase
from scinoephile.llms.translation import TranslationManager, TranslationPrompt

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
    ref_sub="source_two",
    target_subs="source_one",
    target_sub_punctuated="result",
)
"""Punctuation prompt using non-default correspondence field names."""

_MANAGER_CLASSES: list[type[Manager]] = [
    DelineationManager,
    GapTranslationManager,
    GuidedReviewManager,
    GuidedTranslationManager,
    OcrFusionManager,
    PairwiseReviewManager,
    PunctuationManager,
    ReviewManager,
    TranslationManager,
]
"""Manager classes for every LLM correspondence shape."""


@mark.parametrize("manager_cls", _MANAGER_CLASSES)
def test_manager_reuses_static_test_case_prompt(manager_cls: type[Manager]):
    """Each manager should reuse its semantic test-case model's prompt."""
    assert manager_cls.base_prompt is manager_cls.test_case_base_cls.prompt


def test_manager_rejects_incompatible_prompt_type():
    """Managers should reject prompts belonging to another operation."""
    with raises(
        TypeError,
        match="ReviewManager requires ReviewPrompt; got TranslationPrompt",
    ):
        ReviewManager.get_test_case_cls(TranslationPrompt())


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


def test_prompt_specific_classes_revalidate_by_semantic_field_name():
    """Equivalent prompt classes should revalidate without positional mapping."""
    localized_cls = ReviewManager.get_test_case_cls(_LOCALIZED_REVIEW_PROMPT)
    alternative_cls = ReviewManager.get_test_case_cls(_ALTERNATIVE_REVIEW_PROMPT)
    localized = localized_cls.model_validate(
        {
            "query": {"zimu": [{"xuhao": 1, "wenben": "original"}]},
            "answer": {
                "xiugai": [
                    {
                        "xuhao": 1,
                        "wenben": "corrected",
                        "beizhu": "typo",
                    }
                ]
            },
        }
    )

    alternative = alternative_cls.model_validate(localized.model_dump(mode="json"))

    assert alternative.model_dump(mode="json") == localized.model_dump(mode="json")
    assert alternative.query.model_dump(by_alias=True) == {
        "sources": [{"position": 1, "content": "original"}]
    }
    assert alternative.answer is not None
    assert alternative.answer.model_dump(by_alias=True) == {
        "corrections": [
            {
                "position": 1,
                "content": "corrected",
                "explanation": "typo",
            }
        ]
    }


def test_punctuation_factory_uses_static_fields_with_prompt_aliases():
    """Punctuation models should use semantic fields and prompt aliases."""
    test_case_cls = PunctuationManager.get_test_case_cls(_LOCALIZED_PUNCTUATION_PROMPT)

    assert (
        PunctuationManager.get_test_case_cls(_LOCALIZED_PUNCTUATION_PROMPT)
        is test_case_cls
    )
    assert issubclass(test_case_cls, PunctuationTestCase)
    assert set(test_case_cls.query_cls.model_fields) == {"subtitles", "guide"}
    assert test_case_cls.query_cls.model_fields["subtitles"].alias == "source_one"
    assert test_case_cls.query_cls.model_fields["guide"].alias == "source_two"
    assert set(test_case_cls.answer_cls.model_fields) == {"output"}
    assert test_case_cls.answer_cls.model_fields["output"].alias == "result"

    test_case = test_case_cls.model_validate(
        {
            "query": {"subtitles": ["Hello"], "guide": "Hello"},
            "answer": {"output": "Hello"},
        }
    )
    assert test_case.query.model_dump() == {
        "subtitles": ["Hello"],
        "guide": "Hello",
    }
    assert test_case.answer is not None
    assert test_case.answer.model_dump() == {"output": "Hello"}
    assert test_case.query.model_dump(by_alias=True) == {
        "source_one": ["Hello"],
        "source_two": "Hello",
    }
    assert test_case.answer.model_dump(by_alias=True) == {"result": "Hello"}


def test_generated_test_case_inherits_stable_metadata_schema():
    """Generated test cases should preserve metadata order and field schemas."""
    test_case_cls = ReviewManager.get_test_case_cls(_LOCALIZED_REVIEW_PROMPT)
    schema = test_case_cls.model_json_schema(by_alias=True)

    assert list(schema["properties"]) == [
        "query",
        "answer",
        "difficulty",
        "few_shot",
        "verified",
    ]
    assert schema["properties"]["difficulty"] == {
        "default": 0,
        "description": "Difficulty level of the test case, used for filtering.",
        "title": "Difficulty",
        "type": "integer",
    }
    assert schema["properties"]["few_shot"] == {
        "default": False,
        "description": "Whether to include test case in few-shot examples.",
        "title": "Few Shot",
        "type": "boolean",
    }
    assert schema["properties"]["verified"] == {
        "default": False,
        "description": "Whether to include test case in the verified answers cache.",
        "title": "Verified",
        "type": "boolean",
    }


def test_prompt_specific_factory_allows_aliases_reused_across_objects():
    """Query and answer objects may independently use the same alias."""
    prompt = ReviewPrompt(subtitles="items", revisions="items")

    test_case_cls = ReviewManager.get_test_case_cls(prompt)

    assert test_case_cls.query_cls.model_fields["subtitles"].alias == "items"
    assert test_case_cls.answer_cls.model_fields["revisions"].alias == "items"


def test_prompt_specific_factory_rejects_blank_aliases():
    """Generated JSON object field aliases must not be blank."""
    prompt = ReviewPrompt(index=" ")

    with raises(ValueError, match="must have a nonblank alias"):
        ReviewManager.get_test_case_cls(prompt)


def test_prompt_specific_factory_rejects_duplicate_aliases():
    """Generated JSON object field aliases must be unique."""
    prompt = GuidedTranslationPrompt(subtitles="items", guides="items")

    with raises(ValueError, match="field aliases must be unique"):
        GuidedTranslationManager.get_test_case_cls(prompt)
