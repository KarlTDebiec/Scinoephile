#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Offline tests for OpenAIProviderBase tool-call loop behavior."""

from __future__ import annotations

from types import SimpleNamespace
from typing import cast

import pytest
from openai import OpenAI

from scinoephile.core.llms import OpenAIProviderBase
from scinoephile.core.llms.tools import LLMTool, ToolBox


class _DummyProvider(OpenAIProviderBase):
    """Concrete provider for exercising base logic."""

    model = "dummy-model"


class _ToolCallFunction:
    """Tool call function payload fixture."""

    def __init__(self, name: str, arguments: str):
        self.name = name
        self.arguments = arguments


class _ToolCall:
    """Tool call fixture."""

    def __init__(self, tool_id: str, name: str, arguments: str):
        self.id = tool_id
        self.function = _ToolCallFunction(name=name, arguments=arguments)


class _Message:
    """Message fixture."""

    def __init__(
        self,
        content: str | None,
        tool_calls: list[_ToolCall] | None = None,
        reasoning_content: str | None = None,
    ):
        self.content = content
        self.tool_calls = tool_calls
        self.reasoning_content = reasoning_content


class _Completion:
    """Completion fixture matching the minimal OpenAI SDK surface."""

    def __init__(self, message: _Message):
        self.choices = [SimpleNamespace(message=message)]


class _DummyClient:
    """Dummy client that returns tool calls once then a final response."""

    def __init__(self):
        self.calls: list[dict[str, object]] = []
        self._round = 0

        def create(*, messages, model, **kwargs):
            self.calls.append({"messages": messages, "model": model, "kwargs": kwargs})
            if self._round == 0:
                self._round += 1
                return _Completion(
                    _Message(
                        content=None,
                        tool_calls=[_ToolCall("tool-1", "do", '{"x": 1}')],
                        reasoning_content="Need tool output before answering.",
                    )
                )
            return _Completion(_Message(content="done", tool_calls=[]))

        self.chat = SimpleNamespace(completions=SimpleNamespace(create=create))
        self.beta = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(parse=None))
        )


def _get_tool_box(handler) -> ToolBox:
    """Build a tool box for the shared dummy tool."""
    return ToolBox(
        [
            LLMTool(
                spec={
                    "name": "do",
                    "description": "Do something",
                    "parameters": {
                        "type": "object",
                        "properties": {"x": {"type": "number"}},
                    },
                },
                handler=handler,
            )
        ]
    )


def test_tool_call_loop_runs_handler_and_returns_final_text():
    """Test base loops over tool calls and returns a final completion string."""
    client = _DummyClient()
    provider = _DummyProvider(client=cast(OpenAI, client))

    def handler(args):
        return {"ok": True, "args": args}

    result = provider.chat_completion(
        messages=[{"role": "user", "content": "hi"}],
        tool_box=_get_tool_box(handler),
    )

    assert result == "done"
    assert len(client.calls) == 2
    second_call_messages = cast(list[dict[str, object]], client.calls[1]["messages"])
    assert second_call_messages[1]["reasoning_content"] == (
        "Need tool output before answering."
    )


def test_model_override_updates_provider_model():
    """Test provider instances may override the configured model."""
    client = _DummyClient()
    provider = _DummyProvider(client=cast(OpenAI, client), model="override-model")

    provider.chat_completion(
        messages=[{"role": "user", "content": "hi"}],
        tool_box=_get_tool_box(lambda args: args),
    )

    assert cast(str, client.calls[0]["model"]) == "override-model"


def test_build_openai_tools_enables_strict_tools_by_default():
    """Test base provider requests strict tool schemas by default."""
    provider = _DummyProvider(client=cast(OpenAI, _DummyClient()))

    tools = provider._build_openai_tools(
        ToolBox(
            [
                LLMTool(
                    spec={
                        "name": "do",
                        "description": "Do something",
                        "parameters": {"type": "object", "properties": {}},
                    },
                    handler=lambda args: args,
                )
            ]
        )
    )

    function = cast(dict[str, object], tools[0]["function"])
    assert function["strict"] is True


def test_run_tool_handler_returns_error_for_unsupported_tool():
    """Test unknown tool names produce an error payload."""
    provider = _DummyProvider(client=cast(OpenAI, _DummyClient()))

    result = provider._run_tool_handler(
        tool_name="missing",
        raw_arguments="{}",
        tool_box=ToolBox(),
    )

    assert result == {"error": "Unsupported tool 'missing'."}


def test_run_tool_handler_returns_error_for_invalid_json_arguments():
    """Test invalid tool-call JSON produces an error payload."""
    provider = _DummyProvider(client=cast(OpenAI, _DummyClient()))

    result = provider._run_tool_handler(
        tool_name="do",
        raw_arguments="{",
        tool_box=_get_tool_box(lambda args: args),
    )

    assert result == {"error": "Tool 'do' arguments are not valid JSON."}


def test_run_tool_handler_allows_handler_exceptions_to_propagate():
    """Test tool handler failures are not swallowed by the provider."""
    provider = _DummyProvider(client=cast(OpenAI, _DummyClient()))

    def handler(args):
        raise RuntimeError(f"bad args: {args}")

    with pytest.raises(RuntimeError, match=r"bad args: \{'x': 1\}"):
        provider._run_tool_handler(
            tool_name="do",
            raw_arguments='{"x": 1}',
            tool_box=_get_tool_box(handler),
        )
