#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for persisted zero-shot prompt conversion."""

from __future__ import annotations

from dataclasses import replace
from typing import cast

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

_ALTERNATIVE_FEW_SHOT_REVIEW_PROMPT = ReviewPromptEng.with_attributes(
    {
        "difficulty_description": "Different difficulty description.",
        "few_shot_answer_intro": "Different example answer:",
        "few_shot_intro": "Different examples:",
        "few_shot_query_intro": "Different example query:",
        "prompt_description": "Different prompt flag description.",
        "verified_description": "Different verified description.",
    }
)
"""English review prompt with different few-shot-only text."""

_ALTERNATIVE_ZERO_SHOT_REVIEW_PROMPT = ReviewPromptEng.with_attributes(
    {"base_system_prompt": "Review every subtitle carefully."}
)
"""English review prompt with different zero-shot instructions."""


def test_conversion_excludes_few_shot_and_curation_attributes():
    """Few-shot-only and test-case curation text should not affect identity."""
    baseline = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)
    alternative = PersistedPrompt.from_prompt(
        _ALTERNATIVE_FEW_SHOT_REVIEW_PROMPT,
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
    baseline = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)
    alternative = PersistedPrompt.from_prompt(
        _ALTERNATIVE_ZERO_SHOT_REVIEW_PROMPT,
        ReviewManager,
    )

    assert baseline.prompt_id != alternative.prompt_id
    assert (
        baseline.attributes["base_system_prompt"]
        != alternative.attributes["base_system_prompt"]
    )


def test_conversion_rejects_incompatible_prompt():
    """A manager should reject a prompt from another operation."""
    with raises(ScinoephileError, match="not compatible with operation translation"):
        PersistedPrompt.from_prompt(ReviewPromptEng, TranslationManager)


def test_reconstruction_rejects_invalid_content_addressed_id():
    """Reconstruction should reject a prompt whose ID does not match its content."""
    prompt = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)

    with raises(ScinoephileError, match="content-addressed ID"):
        replace(prompt, prompt_id="incorrect").to_prompt(ReviewManager)


def test_reconstruction_round_trips_generated_and_tool_text():
    """Generated Hans and dictionary-tool text should survive reconstruction."""
    persisted = PersistedPrompt.from_prompt(
        YueEngTranslationPromptYueHans,
        TranslationManager,
    )
    prompt = persisted.to_prompt(TranslationManager)
    dictionary_prompt = cast(DictionaryToolPrompt, prompt)

    assert prompt.base_system_prompt == (
        YueEngTranslationPromptYueHans.base_system_prompt
    )
    assert prompt.language == Language.yue_hans
    assert dictionary_prompt.dictionary_tool_description == (
        YueEngTranslationPromptYueHans.dictionary_tool_description
    )
    assert "dictionary_tool_description" in persisted.attributes
    assert "language" not in persisted.attributes
    assert "opencc_config" not in persisted.attributes
