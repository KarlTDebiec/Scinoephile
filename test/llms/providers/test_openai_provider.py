#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Offline tests for OpenAI provider construction defaults."""

from __future__ import annotations

from typing import cast

from pytest import MonkeyPatch

from scinoephile.core.llms import openai_provider_base
from scinoephile.llms.providers.openai_provider import OpenAIProvider
from test.helpers.openai import DummyOpenAI


def test_openai_constructs_client_with_explicit_api_key_and_base_url(
    monkeypatch: MonkeyPatch,
):
    """Test OpenAIProvider forwards explicit client overrides to OpenAI."""
    monkeypatch.setattr(openai_provider_base, "OpenAI", DummyOpenAI)

    provider = OpenAIProvider(api_key="explicit", base_url="https://example.invalid/v1")
    client = cast(DummyOpenAI, provider.sync_client)

    assert isinstance(client, DummyOpenAI)
    assert client.kwargs["api_key"] == "explicit"
    assert client.kwargs["base_url"] == "https://example.invalid/v1"
    assert client.kwargs["timeout"] == 120.0


def test_openai_constructs_client_without_overrides(monkeypatch: MonkeyPatch):
    """Test OpenAIProvider uses SDK defaults when no overrides are supplied."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(openai_provider_base, "OpenAI", DummyOpenAI)

    provider = OpenAIProvider()
    client = cast(DummyOpenAI, provider.sync_client)

    assert isinstance(client, DummyOpenAI)
    assert client.kwargs["api_key"] is None
    assert client.kwargs["base_url"] is None
    assert client.kwargs["timeout"] == 120.0


def test_explicit_prompt_caching_requires_gpt_5_6_or_later():
    """Test explicit prompt caching is limited to supported OpenAI models."""
    assert OpenAIProvider(model="gpt-5.6-luna").use_explicit_prompt_caching is True
    assert OpenAIProvider(model="gpt-6").use_explicit_prompt_caching is True
    assert OpenAIProvider(model="gpt-5.4-nano").use_explicit_prompt_caching is False
