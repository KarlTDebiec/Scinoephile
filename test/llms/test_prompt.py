#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for immutable prompt values."""

from __future__ import annotations

from pytest import raises

from scinoephile.core import Language
from scinoephile.llms.review import ReviewPrompt


def test_prompt_values_are_hashable_and_content_addressed():
    """Equivalent prompt values should compare and hash by content."""
    prompt = ReviewPrompt(language=Language.eng, input_pfx="subtitle_")
    equivalent = ReviewPrompt(language=Language.eng, input_pfx="subtitle_")

    assert equivalent == prompt
    assert hash(equivalent) == hash(prompt)
    assert equivalent.name == prompt.name


def test_prompt_transformation_preserves_type_and_changes_language():
    """Transforming a prompt should return another value of the same operation type."""
    prompt = ReviewPrompt(
        language=Language.eng,
        base_system_prompt="Review subtitles.",
    )

    transformed = prompt.transformed(Language.zho_hant, str.upper)

    assert isinstance(transformed, ReviewPrompt)
    assert transformed.language == Language.zho_hant
    assert transformed.base_system_prompt == "REVIEW SUBTITLES."


def test_prompt_localization_kwargs_reuse_only_shared_fields():
    """Localization keywords should exclude operation-specific prompt fields."""
    base_prompt = ReviewPrompt(
        language=Language.zho_hant,
        base_system_prompt="Base operation instructions.",
        schema_intro="Localized schema introduction.",
        input_pfx="source_",
    )

    localized_prompt = ReviewPrompt(
        language=base_prompt.language,
        **base_prompt.localization_kwargs,
        base_system_prompt="Specialized operation instructions.",
        input_pfx="subtitle_",
    )

    assert localized_prompt.language == Language.zho_hant
    assert localized_prompt.schema_intro == "Localized schema introduction."
    assert localized_prompt.base_system_prompt == "Specialized operation instructions."
    assert localized_prompt.input_pfx == "subtitle_"


def test_prompt_values_are_immutable():
    """Prompt values should reject mutation."""
    prompt = ReviewPrompt(language=Language.eng)

    with raises((AttributeError, TypeError)):
        setattr(prompt, "base_system_prompt", "changed")
