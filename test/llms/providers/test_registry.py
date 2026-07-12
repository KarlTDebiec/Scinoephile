#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for LLM provider registry wiring."""

from __future__ import annotations

from typing import Any, ClassVar, Unpack
from unittest.mock import Mock

from pytest import fixture, raises

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import Answer, LLMProvider, OpenAIProviderBase
from scinoephile.core.llms.llm_provider import ChatCompletionKwargs
from scinoephile.core.llms.tool_box import ToolBox
from scinoephile.llms.providers import registry as provider_registry
from scinoephile.llms.providers.deepseek_provider import DeepSeekProvider
from scinoephile.llms.providers.openai_provider import OpenAIProvider
from scinoephile.llms.providers.registry import (
    DEFAULT_PROVIDER_NAME,
    get_provider,
    get_provider_description,
    get_provider_names,
    register_provider_factory,
)


@fixture(autouse=True)
def restore_provider_registry():
    """Restore registered LLM providers after each test."""
    provider_factories = provider_registry._PROVIDER_FACTORIES.copy()
    yield
    provider_registry._PROVIDER_FACTORIES.clear()
    provider_registry._PROVIDER_FACTORIES.update(provider_factories)


def test_default_provider_name_is_openai():
    """Test default provider name is exposed for CLI defaults."""
    assert DEFAULT_PROVIDER_NAME == "openai"


def test_get_provider_without_name_returns_openai_provider():
    """Test default provider resolution returns an OpenAI provider."""
    provider = get_provider()

    assert isinstance(provider, OpenAIProvider)


def test_get_provider_constructs_openai_provider_with_kwargs():
    """Test explicit provider construction forwards kwargs to the factory."""
    client = Mock()
    provider = get_provider("openai", client=client)

    assert isinstance(provider, OpenAIProvider)
    assert provider.sync_client is client


def test_get_provider_preserves_default_model_with_none_override():
    """Test provider construction tolerates omitted CLI model overrides."""
    provider = get_provider("openai", model=None)

    assert isinstance(provider, OpenAIProvider)
    assert provider.model == "gpt-5.4-mini"


def test_get_provider_constructs_deepseek_provider_with_kwargs():
    """Test DeepSeek provider construction forwards kwargs to the factory."""
    client = Mock()
    provider = get_provider("deepseek", client=client)

    assert isinstance(provider, DeepSeekProvider)
    assert provider.sync_client is client


def test_get_provider_description_uses_provider_docstrings():
    """Test provider descriptions are exposed from registered provider classes."""
    assert "DeepSeek" in get_provider_description("deepseek")
    assert "OpenAI" in get_provider_description("openai")


def test_get_provider_description_uses_provider_localizations():
    """Test provider description localizations are exposed from provider classes."""
    assert "DeepSeek" in get_provider_description("deepseek", "zh-hans")
    assert "DeepSeek" in get_provider_description("deepseek", "zh-hant")
    assert "OpenAI" in get_provider_description("openai", "zh-hans")
    assert "OpenAI" in get_provider_description("openai", "zh-hant")


def test_register_provider_factory_supports_custom_providers():
    """Test registry can resolve explicitly registered provider factories."""
    register_provider_factory("test-dummy", _DummyProvider)
    provider = get_provider("test-dummy", marker="dummy")

    assert isinstance(provider, _DummyProvider)
    assert provider.marker == "dummy"


def test_get_provider_description_supports_registered_provider_factories():
    """Test provider descriptions can be read from registered custom providers."""
    register_provider_factory("test-described", _DummyProvider)

    assert (
        get_provider_description("test-described")
        == "Dummy provider fixture for registry tests."
    )


def test_get_provider_description_supports_registered_provider_localizations():
    """Test provider descriptions can be localized from custom providers."""
    register_provider_factory("test-localized", _LocalizedDummyProvider)

    assert get_provider_description("test-localized", "zh-hans") == (
        "本地化测试提供商。"
    )


def test_get_provider_names_returns_registered_provider_names():
    """Test registry exposes provider names for CLI validation and listing."""
    provider_names = get_provider_names()

    assert provider_names == tuple(sorted(provider_names))
    assert "deepseek" in provider_names
    assert "openai" in provider_names


def test_built_in_providers_use_structured_openai_base():
    """Test built-in providers share the structured completion implementation."""
    assert isinstance(get_provider("deepseek"), OpenAIProviderBase)
    assert isinstance(get_provider("openai"), OpenAIProviderBase)


def test_get_provider_raises_for_unknown_provider():
    """Test provider lookup fails for unknown provider names."""
    with raises(ScinoephileError):
        get_provider("missing-provider")


def test_get_provider_description_raises_for_unknown_provider():
    """Test provider description lookup fails for unknown provider names."""
    with raises(ScinoephileError):
        get_provider_description("missing-provider")


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
        response_format: type[Answer],
        tool_box: ToolBox | None = None,
        **kwargs: Unpack[ChatCompletionKwargs],
    ) -> str:
        """Return a fixed completion value."""
        _ = (messages, response_format, tool_box, kwargs)
        return "{}"


class _LocalizedDummyProvider(_DummyProvider):
    """Localized dummy provider fixture for registry tests."""

    description_localizations: ClassVar[dict[str, str]] = {
        "zh-hans": "本地化测试提供商。",
        "zh-hant": "本地化測試提供商。",
    }
    """Provider description translations keyed by locale."""
