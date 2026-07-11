#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for model configuration identity."""

from __future__ import annotations

from pydantic import JsonValue

from scinoephile.optimization.persistence.models.id import get_model_id


def test_model_id_is_content_addressed():
    """Provider, model, base URL, and settings should determine identity."""
    settings: dict[str, JsonValue] = {
        "reasoning": {"effort": "medium"},
        "temperature": 0.2,
    }
    model_id = get_model_id(
        "openai",
        "gpt-5.4-mini",
        "https://api.openai.com/v1",
        settings,
    )

    assert model_id == get_model_id(
        "openai",
        "gpt-5.4-mini",
        "https://api.openai.com/v1",
        {
            "temperature": 0.2,
            "reasoning": {"effort": "medium"},
        },
    )
    assert model_id != get_model_id(
        "deepseek",
        "gpt-5.4-mini",
        "https://api.openai.com/v1",
        settings,
    )
    assert model_id != get_model_id(
        "openai",
        "gpt-5.4",
        "https://api.openai.com/v1",
        settings,
    )
    assert model_id != get_model_id(
        "openai",
        "gpt-5.4-mini",
        None,
        settings,
    )
    assert model_id != get_model_id(
        "openai",
        "gpt-5.4-mini",
        "https://api.openai.com/v1",
        {"reasoning": {"effort": "high"}, "temperature": 0.2},
    )
