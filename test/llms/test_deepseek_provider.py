#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Offline tests for DeepSeek provider construction defaults."""

from __future__ import annotations

from types import SimpleNamespace
from typing import cast

from scinoephile.core.llms import openai_provider_base
from scinoephile.core.llms.tools import LLMTool, ToolBox
from scinoephile.llms.providers.deepseek_provider import DeepSeekProvider


class _DummyOpenAI:
    """Dummy OpenAI client capturing constructor kwargs."""

    def __init__(self, **kwargs):
        """Initialize and capture kwargs."""
        self.kwargs = kwargs
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=None))
        self.beta = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(parse=None))
        )


def _get_tool_box() -> ToolBox:
    """Build a tool box for one lookup tool."""
    return ToolBox(
        [
            LLMTool(
                spec={
                    "name": "lookup",
                    "description": "Lookup something",
                    "parameters": {"type": "object", "properties": {}},
                },
                handler=lambda args: args,
            )
        ]
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


def test_deepseek_default_base_url_disables_strict_tools():
    """Test DeepSeek default endpoint does not enable strict tool schemas."""
    provider = DeepSeekProvider()

    tools = provider._build_openai_tools(_get_tool_box())

    function = cast(dict[str, object], tools[0]["function"])
    assert function["strict"] is False


def test_deepseek_beta_base_url_enables_strict_tools():
    """Test DeepSeek beta endpoint enables strict tool schemas."""
    provider = DeepSeekProvider(base_url="https://api.deepseek.com/beta")

    tools = provider._build_openai_tools(_get_tool_box())

    function = cast(dict[str, object], tools[0]["function"])
    assert function["strict"] is True
