#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for persisted zero-shot prompt conversion."""

from __future__ import annotations

from dataclasses import replace
from typing import ClassVar, cast

from pytest import raises

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.dictionaries import DictionaryToolPrompt
from scinoephile.lang.eng.review import ReviewPromptEng
from scinoephile.llms.review import ReviewManager
from scinoephile.llms.translation import TranslationManager
from scinoephile.multilang.yue_eng.translation import (
    YueEngTranslationPromptYueHans,
)
from scinoephile.optimization.persistence.prompts import PersistedPrompt


class _AlternativeFewShotReviewPrompt(ReviewPromptEng):
    """English review prompt with different few-shot-only text."""

    difficulty_description: ClassVar[str] = "Different difficulty description."
    """Description of test-case difficulty."""
    few_shot_answer_intro: ClassVar[str] = "Different example answer:"
    """Text preceding a few-shot answer."""
    few_shot_intro: ClassVar[str] = "Different examples:"
    """Text preceding few-shot examples."""
    few_shot_query_intro: ClassVar[str] = "Different example query:"
    """Text preceding a few-shot query."""
    prompt_description: ClassVar[str] = "Different prompt flag description."
    """Description of test-case prompt inclusion."""
    verified_description: ClassVar[str] = "Different verified description."
    """Description of test-case verification."""


class _AlternativeZeroShotReviewPrompt(ReviewPromptEng):
    """English review prompt with different zero-shot instructions."""

    base_system_prompt: ClassVar[str] = "Review every subtitle carefully."
    """Base system prompt."""


def test_conversion_excludes_few_shot_and_curation_attributes():
    """Few-shot-only and test-case curation text should not affect identity."""
    baseline = PersistedPrompt.from_prompt_cls(ReviewPromptEng, ReviewManager)
    alternative = PersistedPrompt.from_prompt_cls(
        _AlternativeFewShotReviewPrompt,
        ReviewManager,
    )

    assert baseline.prompt_id == alternative.prompt_id
    assert baseline.language == Language.eng
    assert baseline.attributes == alternative.attributes
    assert all("few_shot" not in name for name in baseline.attributes)
    assert "difficulty_description" not in baseline.attributes
    assert "prompt_description" not in baseline.attributes
    assert "verified_description" not in baseline.attributes


def test_conversion_includes_zero_shot_attributes():
    """Changing zero-shot instructions should change persisted content."""
    baseline = PersistedPrompt.from_prompt_cls(ReviewPromptEng, ReviewManager)
    alternative = PersistedPrompt.from_prompt_cls(
        _AlternativeZeroShotReviewPrompt,
        ReviewManager,
    )

    assert baseline.prompt_id != alternative.prompt_id
    assert (
        baseline.attributes["base_system_prompt"]
        != alternative.attributes["base_system_prompt"]
    )


def test_conversion_rejects_incompatible_prompt_class():
    """A manager should reject a prompt class from another operation."""
    with raises(ScinoephileError, match="not compatible with operation translation"):
        PersistedPrompt.from_prompt_cls(ReviewPromptEng, TranslationManager)


def test_reconstruction_rejects_invalid_content_addressed_id():
    """Reconstruction should reject a prompt whose ID does not match its content."""
    prompt = PersistedPrompt.from_prompt_cls(ReviewPromptEng, ReviewManager)

    with raises(ScinoephileError, match="content-addressed ID"):
        replace(prompt, prompt_id="incorrect").to_prompt_cls(ReviewManager)


def test_reconstruction_round_trips_generated_and_tool_text():
    """Generated Hans and dictionary-tool text should survive reconstruction."""
    persisted = PersistedPrompt.from_prompt_cls(
        YueEngTranslationPromptYueHans,
        TranslationManager,
    )
    prompt_cls = persisted.to_prompt_cls(TranslationManager)
    dictionary_prompt_cls = cast(type[DictionaryToolPrompt], prompt_cls)

    assert prompt_cls.base_system_prompt == (
        YueEngTranslationPromptYueHans.base_system_prompt
    )
    assert prompt_cls.language == Language.yue_hans
    assert dictionary_prompt_cls.dictionary_tool_description == (
        YueEngTranslationPromptYueHans.dictionary_tool_description
    )
    assert "dictionary_tool_description" in persisted.attributes
    assert "language" not in persisted.attributes
    assert "opencc_config" not in persisted.attributes
