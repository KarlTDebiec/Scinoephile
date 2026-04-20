#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for LLM provider registry wiring."""

from __future__ import annotations

from typing import Any, Unpack
from unittest.mock import Mock

import pytest

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import Answer, LLMProvider
from scinoephile.core.llms.llm_provider import ChatCompletionKwargs
from scinoephile.core.llms.tools import LLMToolSpec, ToolHandler
from scinoephile.llms.providers.openai import OpenAIProvider
from scinoephile.llms.providers.registry import (
    get_default_provider,
    get_provider,
    register_provider_factory,
)


class _DummyProvider(LLMProvider):
    """Dummy provider fixture for registry tests."""

    def __init__(self, marker: str):
        """Initialize dummy provider.

        Arguments:
            marker: marker value for construction assertions
        """
        self.marker = marker

    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer] | None = None,
        model: str | None = None,
        tools: list[LLMToolSpec] | None = None,
        tool_handlers: dict[str, ToolHandler] | None = None,
        **kwargs: Unpack[ChatCompletionKwargs],
    ) -> str:
        """Return a fixed completion value."""
        _ = (messages, response_format, model, tools, tool_handlers, kwargs)
        return "{}"


def test_get_default_provider_returns_openai_provider():
    """Test default provider resolution returns an OpenAI provider."""
    provider = get_default_provider()

    assert isinstance(provider, OpenAIProvider)


def test_get_provider_constructs_openai_provider_with_kwargs():
    """Test explicit provider construction forwards kwargs to the factory."""
    client = Mock()
    provider = get_provider("openai", client=client)

    assert isinstance(provider, OpenAIProvider)
    assert provider.sync_client is client


def test_register_provider_factory_supports_custom_providers():
    """Test registry can resolve explicitly registered provider factories."""
    register_provider_factory("test-dummy", _DummyProvider)
    provider = get_provider("test-dummy", marker="dummy")

    assert isinstance(provider, _DummyProvider)
    assert provider.marker == "dummy"


def test_get_provider_raises_for_unknown_provider():
    """Test provider lookup fails for unknown provider names."""
    with pytest.raises(ScinoephileError):
        get_provider("missing-provider")
