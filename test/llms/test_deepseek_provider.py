#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Offline tests for DeepSeek provider construction defaults."""

from __future__ import annotations

from types import SimpleNamespace
from typing import cast

from scinoephile.core.llms import openai_provider_base
from scinoephile.llms.providers.deepseek import DeepSeekProvider


class _DummyOpenAI:
    """Dummy OpenAI client capturing constructor kwargs."""

    def __init__(self, **kwargs):
        """Initialize and capture kwargs."""
        self.kwargs = kwargs
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=None))
        self.beta = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(parse=None))
        )


def test_deepseek_constructs_client_with_base_url_and_env_api_key(monkeypatch):
    """Test DeepSeekProvider uses base_url and DEEPSEEK_API_KEY by default."""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "dummy")

    monkeypatch.setattr(openai_provider_base, "OpenAI", _DummyOpenAI)

    provider = DeepSeekProvider()
    client = cast(_DummyOpenAI, provider.sync_client)

    assert isinstance(client, _DummyOpenAI)
    assert client.kwargs["base_url"] == "https://api.deepseek.com"
    assert client.kwargs["api_key"] == "dummy"


def test_deepseek_api_key_override_wins_over_env(monkeypatch):
    """Test explicit api_key overrides the environment variable."""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "env")

    monkeypatch.setattr(openai_provider_base, "OpenAI", _DummyOpenAI)

    provider = DeepSeekProvider(api_key="explicit")
    client = cast(_DummyOpenAI, provider.sync_client)

    assert client.kwargs["api_key"] == "explicit"
