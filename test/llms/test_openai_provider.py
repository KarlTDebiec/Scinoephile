#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Offline tests for OpenAI provider construction defaults."""

from __future__ import annotations

from types import SimpleNamespace
from typing import cast

from scinoephile.core.llms import openai_provider_base
from scinoephile.llms.providers.openai_provider import OpenAIProvider


class _DummyOpenAI:
    """Dummy OpenAI client capturing constructor kwargs."""

    def __init__(self, **kwargs):
        """Initialize and capture kwargs."""
        self.kwargs = kwargs
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=None))
        self.beta = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(parse=None))
        )


def test_openai_constructs_client_with_explicit_api_key_and_base_url(monkeypatch):
    """Test OpenAIProvider forwards explicit client overrides to OpenAI."""
    monkeypatch.setattr(openai_provider_base, "OpenAI", _DummyOpenAI)

    provider = OpenAIProvider(
        api_key="explicit",
        base_url="https://example.invalid/v1",
    )
    client = cast(_DummyOpenAI, provider.sync_client)

    assert isinstance(client, _DummyOpenAI)
    assert client.kwargs["api_key"] == "explicit"
    assert client.kwargs["base_url"] == "https://example.invalid/v1"


def test_openai_constructs_client_without_overrides(monkeypatch):
    """Test OpenAIProvider uses SDK defaults when no overrides are supplied."""
    monkeypatch.setattr(openai_provider_base, "OpenAI", _DummyOpenAI)

    provider = OpenAIProvider()
    client = cast(_DummyOpenAI, provider.sync_client)

    assert isinstance(client, _DummyOpenAI)
    assert client.kwargs["api_key"] is None
    assert client.kwargs["base_url"] is None
