#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for immutable prompt values."""

from __future__ import annotations

from pytest import raises

from scinoephile.core import Language
from scinoephile.lang.eng.review import ReviewPromptEng
from scinoephile.llms.review import ReviewPrompt


def test_prompt_values_are_hashable_and_content_addressed():
    """Equivalent prompt values should compare and hash by content."""
    equivalent = ReviewPrompt.from_attributes(
        ReviewPromptEng.language,
        dict(ReviewPromptEng.attributes),
    )

    assert equivalent == ReviewPromptEng
    assert hash(equivalent) == hash(ReviewPromptEng)
    assert equivalent.name == ReviewPromptEng.name


def test_prompt_transformation_preserves_type_and_changes_language():
    """Transforming a prompt should return another value of the same operation type."""
    transformed = ReviewPromptEng.transformed(Language.zho_hant, str.upper)

    assert isinstance(transformed, ReviewPrompt)
    assert transformed.language == Language.zho_hant
    assert transformed.base_system_prompt == ReviewPromptEng.base_system_prompt.upper()


def test_prompt_values_are_immutable():
    """Prompt values should reject mutation."""
    with raises((AttributeError, TypeError)):
        setattr(ReviewPromptEng, "base_system_prompt", "changed")
