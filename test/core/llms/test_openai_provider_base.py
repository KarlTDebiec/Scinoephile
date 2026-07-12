#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Offline tests for OpenAIProviderBase tool-call loop behavior."""

from __future__ import annotations

import json
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock

from openai import OpenAI
from pydantic import ValidationError
from pytest import raises

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import Answer, OpenAIProviderBase
from scinoephile.core.llms.tool import Tool
from scinoephile.core.llms.tool_box import ToolBox


class _DummyProvider(OpenAIProviderBase):
    """Concrete provider for exercising base logic."""

    model = "dummy-model"
    """Dummy model name."""


class _Answer(Answer):
    """Structured answer fixture."""

    output: str
    """Answer output."""


class _ToolCallFunction:
    """Tool call function payload fixture."""

    def __init__(self, name: str, arguments: str):
        """Initialize tool call function payload.

        Arguments:
            name: tool function name
            arguments: serialized tool arguments
        """
        self.name = name
        self.arguments = arguments


class _ToolCall:
    """Tool call fixture."""

    def __init__(self, tool_id: str, name: str, arguments: str):
        """Initialize tool call fixture.

        Arguments:
            tool_id: tool call identifier
            name: tool function name
            arguments: serialized tool arguments
        """
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
        """Initialize message fixture.

        Arguments:
            content: message content
            tool_calls: tool calls requested by the model
            reasoning_content: model reasoning content
        """
        self.content = content
        self.tool_calls = tool_calls
        self.reasoning_content = reasoning_content


class _Completion:
    """Completion fixture matching the minimal OpenAI SDK surface."""

    def __init__(self, message: _Message):
        """Initialize completion fixture.

        Arguments:
            message: completion message
        """
        self.choices = [SimpleNamespace(message=message)]


class _DummyClient:
    """Dummy client that returns tool calls once then a final response."""

    def __init__(self):
        """Initialize dummy client state and completion surface."""
        self.calls: list[dict[str, object]] = []
        self.parse_calls = 0
        self._round = 0

        def create(
            *,
            messages: list[dict[str, object]],
            model: str,
            **kwargs: Any,
        ) -> _Completion:
            """Create one dummy chat completion.

            Arguments:
                messages: OpenAI chat messages
                model: model name
                **kwargs: additional completion keyword arguments
            Returns:
                dummy completion
            """
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

        def parse(
            *,
            messages: list[dict[str, object]],
            model: str,
            **kwargs: Any,
        ) -> _Completion:
            """Parse one structured dummy chat completion.

            Arguments:
                messages: OpenAI chat messages
                model: model name
                **kwargs: additional completion keyword arguments
            Returns:
                dummy completion
            """
            self.parse_calls += 1
            return create(messages=messages, model=model, **kwargs)

        self.chat = SimpleNamespace(completions=SimpleNamespace(create=create))
        self.beta = SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(parse=parse))
        )


def _get_tool_box(handler: Callable[[dict[str, object]], object]) -> ToolBox:
    """Build a tool box for the shared dummy tool."""
    return ToolBox(
        [
            Tool(
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

    def handler(args: dict[str, object]) -> dict[str, object]:
        """Return a deterministic tool payload.

        Arguments:
            args: parsed tool arguments
        Returns:
            tool result payload
        """
        return {"ok": True, "args": args}

    result = provider.chat_completion(
        messages=[{"role": "user", "content": "hi"}],
        response_format=_Answer,
        tool_box=_get_tool_box(handler),
    )

    assert result == "done"
    assert client.parse_calls == 2
    assert len(client.calls) == 2
    first_call_kwargs = cast(dict[str, object], client.calls[0]["kwargs"])
    assert first_call_kwargs["response_format"] is _Answer
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
        response_format=_Answer,
        tool_box=_get_tool_box(lambda args: args),
    )

    assert cast(str, client.calls[0]["model"]) == "override-model"


def test_structured_response_validation_error_is_wrapped():
    """Test client-side structured validation failures become domain errors."""
    client = Mock()
    with raises(ValidationError) as exc_info:
        _Answer.model_validate({})
    client.beta.chat.completions.parse.side_effect = exc_info.value
    provider = _DummyProvider(client=cast(OpenAI, client))

    with raises(ScinoephileError, match="failed structured response validation"):
        provider.chat_completion(
            messages=[{"role": "user", "content": "hi"}],
            response_format=_Answer,
        )


def test_cache_identity_contains_nonsecret_effective_configuration():
    """Test cache identity captures behavior without exposing credentials."""
    provider = _DummyProvider(
        api_key="super-secret",
        base_url="https://example.invalid/v1/",
        model="override-model",
    )

    assert provider.cache_identity == {
        "implementation": f"{_DummyProvider.__module__}.{_DummyProvider.__qualname__}",
        "model": "override-model",
        "base_url": "https://example.invalid/v1",
        "use_strict_tools": True,
    }
    assert "super-secret" not in json.dumps(provider.cache_identity)


def test_cache_identity_uses_effective_sdk_base_url(monkeypatch):
    """Test cache identity honors the SDK's base URL environment override."""
    monkeypatch.setenv("OPENAI_BASE_URL", "https://environment.invalid/v1/")
    provider = _DummyProvider(api_key="super-secret")

    assert provider.cache_identity["base_url"] == ("https://environment.invalid/v1")


def test_build_openai_tools_enables_strict_tools_by_default():
    """Test base provider requests strict tool schemas by default."""
    provider = _DummyProvider(client=cast(OpenAI, _DummyClient()))

    tools = provider._build_openai_tools(
        ToolBox(
            [
                Tool(
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


def test_tool_box_run_returns_error_for_unsupported_tool():
    """Test unknown tool names produce an error payload."""
    result = ToolBox().run(
        tool_name="missing",
        raw_arguments="{}",
    )

    assert result == {"error": "Unsupported tool 'missing'."}


def test_tool_box_run_returns_error_for_invalid_json_arguments():
    """Test invalid tool-call JSON produces an error payload."""
    result = _get_tool_box(lambda args: args).run(
        tool_name="do",
        raw_arguments="{",
    )

    assert result == {"error": "Tool 'do' arguments are not valid JSON."}


def test_tool_box_run_allows_handler_exceptions_to_propagate():
    """Test tool handler failures are not swallowed by the tool box."""

    def handler(args: dict[str, object]):
        """Raise for parsed tool arguments.

        Arguments:
            args: parsed tool arguments
        Raises:
            RuntimeError: always
        """
        raise RuntimeError(f"bad args: {args}")

    with raises(RuntimeError, match=r"bad args: \{'x': 1\}"):
        _get_tool_box(handler).run(
            tool_name="do",
            raw_arguments='{"x": 1}',
        )
