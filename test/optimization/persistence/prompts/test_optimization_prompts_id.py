#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for prompt identity."""

from __future__ import annotations

from scinoephile.core import Language
from scinoephile.optimization.persistence.prompts.id import get_prompt_id


def test_prompt_id_is_content_addressed():
    """Operation, language, and prompt text should determine identity."""
    attributes = {"base_system_prompt": "Review subtitles."}
    prompt_id = get_prompt_id(attributes, "review", Language.eng)

    assert prompt_id == get_prompt_id(attributes, "review", Language.eng)
    assert prompt_id != get_prompt_id(attributes, "translation", Language.eng)
    assert prompt_id != get_prompt_id(attributes, "review", Language.zho_hant)
    assert prompt_id != get_prompt_id(
        {"base_system_prompt": "Carefully review subtitles."},
        "review",
        Language.eng,
    )
