#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for persisted zero-shot prompt conversion."""

from __future__ import annotations

from dataclasses import replace

from pytest import raises

from scinoephile.core import Language, ScinoephileError
from scinoephile.lang.eng.review import ReviewPromptEng
from scinoephile.llms.review import ReviewManager
from scinoephile.llms.translation import TranslationManager
from scinoephile.multilang.yue_eng.translation import (
    YueEngTranslationPromptYueHans,
)
from scinoephile.optimization.persistence.prompts import PersistedPrompt

_ALTERNATIVE_FEW_SHOT_REVIEW_PROMPT = replace(
    ReviewPromptEng,
    difficulty_description="Different difficulty description.",
    few_shot_answer_intro="Different example answer:",
    few_shot_description="Different few-shot flag description.",
    few_shot_intro="Different examples:",
    few_shot_query_intro="Different example query:",
    verified_description="Different verified description.",
)
"""English review prompt with different few-shot-only text."""


def test_conversion_excludes_few_shot_and_curation_attributes():
    """Few-shot-only and test-case curation text should not affect identity."""
    baseline = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)
    alternative = PersistedPrompt.from_prompt(
        _ALTERNATIVE_FEW_SHOT_REVIEW_PROMPT,
        ReviewManager,
    )

    assert baseline == alternative
    assert baseline.language == Language.eng
    assert all("few_shot" not in name for name, _ in baseline.attributes)
    assert "difficulty_description" not in dict(baseline.attributes)
    assert "verified_description" not in dict(baseline.attributes)


def test_conversion_includes_zero_shot_and_tool_attributes():
    """Zero-shot instructions and dictionary tool text should be persisted."""
    baseline = PersistedPrompt.from_prompt(ReviewPromptEng, ReviewManager)
    alternative = PersistedPrompt.from_prompt(
        replace(
            ReviewPromptEng,
            base_system_prompt="Review every subtitle carefully.",
        ),
        ReviewManager,
    )
    translation = PersistedPrompt.from_prompt(
        YueEngTranslationPromptYueHans,
        TranslationManager,
    )
    translation_attributes = dict(translation.attributes)

    assert baseline.prompt_id != alternative.prompt_id
    assert "dictionary_tool_description" in translation_attributes
    assert "language" not in translation_attributes
    assert "opencc_config" not in translation_attributes


def test_conversion_rejects_incompatible_prompt():
    """A manager should reject a prompt from another operation."""
    with raises(ScinoephileError, match="not compatible with operation translation"):
        PersistedPrompt.from_prompt(ReviewPromptEng, TranslationManager)
