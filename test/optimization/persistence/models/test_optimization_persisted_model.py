#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for persisted model configuration creation."""

from __future__ import annotations

from math import nan

from pytest import mark, raises

from scinoephile.core import ScinoephileError
from scinoephile.optimization.persistence.models import PersistedModel


def test_creation_normalizes_effective_configuration():
    """Model creation should preserve effective non-secret configuration."""
    model = PersistedModel.from_config(
        " openai ",
        " gpt-5.4-mini ",
        base_url=" https://api.openai.com/v1 ",
        settings={"reasoning": {"effort": "medium"}, "seed": 1},
    )

    assert model.provider_name == "openai"
    assert model.model_name == "gpt-5.4-mini"
    assert model.base_url == "https://api.openai.com/v1"
    assert model.settings == {
        "reasoning": {"effort": "medium"},
        "seed": 1,
    }


def test_creation_rejects_credentials_in_base_url():
    """Base URLs should not persist embedded credentials."""
    with raises(ScinoephileError, match="base URL must not contain credentials"):
        PersistedModel.from_config(
            "openai-compatible",
            "model",
            base_url="https://user:password@example.com/v1",
        )

    with raises(ScinoephileError, match="credential query parameters"):
        PersistedModel.from_config(
            "openai-compatible",
            "model",
            base_url="https://example.com/v1?apiKey=secret",
        )


@mark.parametrize(
    "credential_name",
    ["api_key", "Authorization", "apiKey", "clientSecret", "accessToken"],
)
def test_creation_rejects_credentials_in_nested_settings(credential_name: str):
    """Settings should not persist credential-bearing fields."""
    with raises(
        ScinoephileError,
        match=rf"settings.headers.{credential_name}",
    ):
        PersistedModel.from_config(
            "openai-compatible",
            "model",
            settings={"headers": {credential_name: "secret"}},
        )


def test_creation_rejects_non_json_settings():
    """Settings should be finite JSON values."""
    with raises(ScinoephileError, match="valid JSON"):
        PersistedModel.from_config(
            "openai",
            "gpt-5.4-mini",
            settings={"temperature": nan},
        )
