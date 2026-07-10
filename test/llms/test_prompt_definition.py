#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for declarative prompt definition and materialization."""

from __future__ import annotations

from scinoephile.core import Language
from scinoephile.lang.eng.review import ReviewPromptEng
from scinoephile.llms import PromptDefinition
from scinoephile.llms.review import ReviewPrompt


def test_definition_materializes_cached_language_aware_prompt_class():
    """Equivalent definitions should reuse one language-aware runtime class."""
    definition = PromptDefinition.from_prompt_cls(ReviewPromptEng)

    first_prompt_cls = definition.get_prompt_cls(ReviewPrompt)
    second_prompt_cls = definition.get_prompt_cls(ReviewPrompt)

    assert first_prompt_cls is second_prompt_cls
    assert first_prompt_cls.language == Language.eng
    assert first_prompt_cls.base_system_prompt == ReviewPromptEng.base_system_prompt


def test_definition_language_changes_runtime_class_identity():
    """The declared language should participate in runtime class identity."""
    definition = PromptDefinition.from_prompt_cls(ReviewPromptEng)
    translated_definition = PromptDefinition.from_attributes(
        Language.zho_hant,
        dict(definition.attributes),
    )

    translated_prompt_cls = translated_definition.get_prompt_cls(ReviewPrompt)

    assert translated_prompt_cls is not ReviewPromptEng
    assert translated_prompt_cls.language == Language.zho_hant
    assert (
        translated_prompt_cls.base_system_prompt == ReviewPromptEng.base_system_prompt
    )
