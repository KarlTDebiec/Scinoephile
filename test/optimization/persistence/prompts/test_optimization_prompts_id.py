#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for zero-shot prompt identity helpers."""

from __future__ import annotations

from scinoephile.core import Language
from scinoephile.optimization.persistence.prompts.id import get_prompt_id


def test_get_prompt_id_is_stable_for_same_attributes():
    """Identical canonical prompt data should produce the same ID."""
    attributes = {"base_system_prompt": "Review subtitles."}

    assert get_prompt_id(attributes, "review", Language.eng) == get_prompt_id(
        attributes,
        "review",
        Language.eng,
    )


def test_get_prompt_id_changes_with_operation():
    """The operation should contribute to prompt identity."""
    attributes = {"base_system_prompt": "Review subtitles."}

    assert get_prompt_id(attributes, "review", Language.eng) != get_prompt_id(
        attributes,
        "translation",
        Language.eng,
    )


def test_get_prompt_id_changes_with_language():
    """The correspondence language should contribute to prompt identity."""
    attributes = {"base_system_prompt": "Review subtitles."}

    assert get_prompt_id(
        attributes,
        "review",
        Language.eng,
    ) != get_prompt_id(
        attributes,
        "review",
        Language.zho_hant,
    )


def test_get_prompt_id_changes_with_zero_shot_text():
    """Changing zero-shot prompt text should change the prompt ID."""
    assert get_prompt_id(
        {"base_system_prompt": "Review subtitles."},
        "review",
        Language.eng,
    ) != get_prompt_id(
        {"base_system_prompt": "Carefully review subtitles."},
        "review",
        Language.eng,
    )
