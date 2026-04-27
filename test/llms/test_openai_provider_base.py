#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Offline tests for OpenAIProviderBase tool-call loop behavior."""

from __future__ import annotations

from types import SimpleNamespace
from typing import cast

from openai import OpenAI

from scinoephile.core.llms import OpenAIProviderBase


class _DummyProvider(OpenAIProviderBase):
    """Concrete provider for exercising base logic."""

    default_model = "dummy-model"


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

    def __init__(self, content: str | None, tool_calls: list[_ToolCall] | None = None):
        self.content = content
        self.tool_calls = tool_calls


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
                    )
                )
            return _Completion(_Message(content="done", tool_calls=[]))

        self.chat = SimpleNamespace(completions=SimpleNamespace(create=create))
        self.beta = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(parse=None))
        )


def test_tool_call_loop_runs_handler_and_returns_final_text():
    """Test base loops over tool calls and returns a final completion string."""
    client = _DummyClient()
    provider = _DummyProvider(client=cast(OpenAI, client))

    def handler(args):
        return {"ok": True, "args": args}

    result = provider.chat_completion(
        messages=[{"role": "user", "content": "hi"}],
        tools=[
            {
                "name": "do",
                "description": "Do something",
                "parameters": {
                    "type": "object",
                    "properties": {"x": {"type": "number"}},
                },
            }
        ],
        tool_handlers={"do": handler},
    )

    assert result == "done"
    assert len(client.calls) == 2
