#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for OpenAIProvider tool-calling behavior."""

from __future__ import annotations

import json
from typing import Any, cast

from scinoephile.open_ai import OpenAIProvider


class _FakeFunction:
    """Fake function payload for a tool call."""

    def __init__(self, name: str, arguments: str):
        """Initialize.

        Arguments:
            name: function name
            arguments: JSON arguments payload
        """
        self.name = name
        self.arguments = arguments


class _FakeToolCall:
    """Fake tool-call payload from an assistant message."""

    def __init__(self, tool_call_id: str, name: str, arguments: str):
        """Initialize.

        Arguments:
            tool_call_id: unique tool-call identifier
            name: function name
            arguments: JSON arguments payload
        """
        self.id = tool_call_id
        self.type = "function"
        self.function = _FakeFunction(name, arguments)


class _FakeMessage:
    """Fake assistant message payload."""

    def __init__(self, content: str | None, tool_calls: list[_FakeToolCall] | None):
        """Initialize.

        Arguments:
            content: assistant message content
            tool_calls: optional tool call list
        """
        self.content = content
        self.tool_calls = tool_calls


class _FakeChoice:
    """Fake completion choice payload."""

    def __init__(self, message: _FakeMessage):
        """Initialize.

        Arguments:
            message: assistant message payload
        """
        self.message = message


class _FakeCompletion:
    """Fake completion payload."""

    def __init__(self, message: _FakeMessage):
        """Initialize.

        Arguments:
            message: assistant message payload
        """
        self.choices = [_FakeChoice(message)]


class _FakeChatCompletionsApi:
    """Fake chat.completions API surface."""

    def __init__(self, responses: list[_FakeCompletion]):
        """Initialize.

        Arguments:
            responses: ordered responses returned by create calls
        """
        self._responses = responses
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs) -> _FakeCompletion:
        """Return next fake completion.

        Arguments:
            **kwargs: request arguments from provider
        Returns:
            next configured completion
        """
        self.calls.append(kwargs)
        return self._responses.pop(0)


class _FakeChatApi:
    """Fake chat API root with completions surface."""

    def __init__(self, responses: list[_FakeCompletion]):
        """Initialize.

        Arguments:
            responses: ordered responses returned by create calls
        """
        self.completions = _FakeChatCompletionsApi(responses)


class _FakeSyncClient:
    """Fake sync OpenAI client with chat API."""

    def __init__(self, responses: list[_FakeCompletion]):
        """Initialize.

        Arguments:
            responses: ordered responses returned by create calls
        """
        self.chat = _FakeChatApi(responses)


class _UnusedAsyncClient:
    """Placeholder async client for tests that only use sync provider calls."""


def test_chat_completion_runs_tool_and_returns_final_content():
    """Test provider executes tool call and returns follow-up assistant content."""
    first = _FakeCompletion(
        _FakeMessage(
            content=None,
            tool_calls=[
                _FakeToolCall(
                    tool_call_id="tool_1",
                    name="lookup_cuhk_dictionary",
                    arguments='{"query": "巴士", "limit": 2}',
                )
            ],
        )
    )
    second = _FakeCompletion(
        _FakeMessage(content='{"xiugai": "巴士", "beizhu": ""}', tool_calls=None)
    )
    sync_client = _FakeSyncClient([first, second])

    handler_calls: list[dict[str, object]] = []

    def _handler(arguments: dict[str, object]) -> dict[str, object]:
        """Record handler call and return deterministic response.

        Arguments:
            arguments: parsed JSON arguments
        Returns:
            deterministic tool response payload
        """
        handler_calls.append(arguments)
        return {
            "query": arguments["query"],
            "result_count": 1,
            "entries": [{"traditional": "巴士"}],
        }

    provider = OpenAIProvider(
        client=cast("Any", sync_client),
        aclient=cast("Any", _UnusedAsyncClient()),
    )
    content = provider.chat_completion(
        messages=[
            {"role": "system", "content": "system"},
            {"role": "user", "content": "user"},
        ],
        tools=[
            {
                "name": "lookup_cuhk_dictionary",
                "description": "Lookup CUHK dictionary entries.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                    },
                    "required": ["query"],
                },
            }
        ],
        tool_handlers={"lookup_cuhk_dictionary": _handler},
    )

    assert content == '{"xiugai": "巴士", "beizhu": ""}'
    assert handler_calls == [{"query": "巴士", "limit": 2}]
    assert len(sync_client.chat.completions.calls) == 2

    second_call_messages = cast(
        "list[dict[str, object]]",
        sync_client.chat.completions.calls[1]["messages"],
    )
    tool_messages = [
        message for message in second_call_messages if message["role"] == "tool"
    ]
    assert len(tool_messages) == 1
    tool_payload = json.loads(cast("str", tool_messages[0]["content"]))
    assert tool_payload["result_count"] == 1


def test_chat_completion_handles_unknown_tool_with_error_payload():
    """Test provider returns tool error payload for unsupported tools."""
    first = _FakeCompletion(
        _FakeMessage(
            content=None,
            tool_calls=[
                _FakeToolCall(
                    tool_call_id="tool_1",
                    name="unknown_tool",
                    arguments='{"query": "巴士"}',
                )
            ],
        )
    )
    second = _FakeCompletion(
        _FakeMessage(content='{"xiugai": "巴士", "beizhu": ""}', tool_calls=None)
    )
    sync_client = _FakeSyncClient([first, second])

    provider = OpenAIProvider(
        client=cast("Any", sync_client),
        aclient=cast("Any", _UnusedAsyncClient()),
    )
    content = provider.chat_completion(
        messages=[
            {"role": "system", "content": "system"},
            {"role": "user", "content": "user"},
        ],
        tools=[
            {
                "name": "lookup_cuhk_dictionary",
                "description": "Lookup CUHK dictionary entries.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                    },
                    "required": ["query"],
                },
            }
        ],
        tool_handlers={},
    )

    assert content == '{"xiugai": "巴士", "beizhu": ""}'

    second_call_messages = cast(
        "list[dict[str, object]]",
        sync_client.chat.completions.calls[1]["messages"],
    )
    tool_messages = [
        message for message in second_call_messages if message["role"] == "tool"
    ]
    assert len(tool_messages) == 1
    tool_payload = json.loads(cast("str", tool_messages[0]["content"]))
    assert "Unsupported tool" in tool_payload["error"]
