#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Offline tests for OpenAIProviderBase tool-call loop behavior."""

from __future__ import annotations

import json
from collections.abc import Callable
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock, patch

from openai import OpenAI
from pydantic import ValidationError
from pytest import mark, raises

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import Answer, OpenAIProviderBase
from scinoephile.core.llms.tool import Tool
from scinoephile.core.llms.tool_box import ToolBox


class _DummyProvider(OpenAIProviderBase):
    """Concrete provider for exercising base logic."""

    model = "dummy-model"
    """Dummy model name."""


class _CachingDummyProvider(_DummyProvider):
    """Dummy provider with explicit prompt caching enabled."""

    explicit_prompt_caching = True
    """Enable explicit prompt caching for tests."""


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

    def __init__(self, message: _Message, *, include_usage: bool = True):
        """Initialize completion fixture.

        Arguments:
            message: completion message
            include_usage: whether to expose provider usage details
        """
        self.choices = [SimpleNamespace(message=message)]
        if include_usage:
            self.usage = SimpleNamespace(
                prompt_tokens=100,
                prompt_tokens_details=SimpleNamespace(
                    cached_tokens=60, cache_write_tokens=20
                ),
                completion_tokens=12,
                completion_tokens_details=SimpleNamespace(reasoning_tokens=7),
                total_tokens=112,
            )


class _DummyClient:
    """Dummy client that returns tool calls once then a final response."""

    def __init__(self, *, include_usage: bool = True, use_raw_response: bool = False):
        """Initialize dummy client state and completion surface.

        Arguments:
            include_usage: whether completions expose provider usage details
            use_raw_response: whether to expose SDK retry metadata
        """
        self.calls: list[dict[str, object]] = []
        self.parse_calls = 0
        self._round = 0

        def create(
            *, messages: list[dict[str, object]], model: str, **kwargs: Any
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
                    ),
                    include_usage=include_usage,
                )
            return _Completion(
                _Message(content="done", tool_calls=[]), include_usage=include_usage
            )

        def parse(
            *, messages: list[dict[str, object]], model: str, **kwargs: Any
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
        completions = SimpleNamespace(parse=parse)
        if use_raw_response:

            def raw_parse(
                *, messages: list[dict[str, object]], model: str, **kwargs: Any
            ) -> SimpleNamespace:
                """Return a raw response carrying retry metadata.

                Arguments:
                    messages: messages value
                    model: model
                    **kwargs: additional keyword arguments
                Returns:
                    a raw response carrying retry metadata
                """
                self.parse_calls += 1
                completion = create(messages=messages, model=model, **kwargs)
                return SimpleNamespace(parse=lambda: completion, retries_taken=2)

            completions.with_raw_response = SimpleNamespace(parse=raw_parse)
        self.beta = SimpleNamespace(chat=SimpleNamespace(completions=completions))


def _get_tool_box(handler: Callable[[dict[str, object]], object]) -> ToolBox:
    """Build a tool box for the shared dummy tool.

    Arguments:
        handler: handler value
    Returns:
        a tool box for the shared dummy tool
    """
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
    assert "prompt_cache_key" not in first_call_kwargs
    second_call_messages = cast(list[dict[str, object]], client.calls[1]["messages"])
    assert second_call_messages[1]["reasoning_content"] == (
        "Need tool output before answering."
    )
    assert [metrics.tool_round for metrics in provider.completion_metrics] == [1, 2]
    assert provider.completion_metrics[0].input_tokens == 100
    assert provider.completion_metrics[0].cached_input_tokens == 60
    assert provider.completion_metrics[0].cache_write_tokens == 20
    assert provider.completion_metrics[0].output_tokens == 12
    assert provider.completion_metrics[0].reasoning_tokens == 7
    assert provider.completion_metrics[0].total_tokens == 112
    assert provider.completion_metrics[0].transport_retries is None
    assert provider.completion_metrics[0].latency_seconds >= 0


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


def test_completion_requests_use_configured_timeout():
    """Test completion requests forward the timeout to an injected client."""
    client = _DummyClient()
    provider = _DummyProvider(client=cast(OpenAI, client), timeout_seconds=45.0)

    result = provider.chat_completion(
        messages=[{"role": "user", "content": "hi"}],
        response_format=_Answer,
        tool_box=_get_tool_box(lambda args: args),
    )

    assert result == "done"
    assert [
        cast(dict[str, object], call["kwargs"])["timeout"] for call in client.calls
    ] == [45.0, 45.0]


def test_structured_response_validation_error_is_wrapped():
    """Test client-side structured validation failures become domain errors."""
    client = Mock()
    with raises(ValidationError) as exc_info:
        _Answer.model_validate({})
    client.beta.chat.completions.parse.side_effect = exc_info.value
    client.beta.chat.completions.with_raw_response = None
    provider = _DummyProvider(client=cast(OpenAI, client))

    with raises(ScinoephileError, match="failed structured response validation"):
        provider.chat_completion(
            messages=[{"role": "user", "content": "hi"}], response_format=_Answer
        )


def test_completion_metrics_preserve_missing_usage_details():
    """Test omitted provider metrics remain unknown rather than becoming zero."""
    client = _DummyClient(include_usage=False)
    provider = _DummyProvider(client=cast(OpenAI, client))

    provider.chat_completion(
        messages=[{"role": "user", "content": "hi"}],
        response_format=_Answer,
        tool_box=_get_tool_box(lambda args: args),
    )

    metrics = provider.completion_metrics[0]
    assert metrics.input_tokens is None
    assert metrics.cached_input_tokens is None
    assert metrics.cache_write_tokens is None
    assert metrics.output_tokens is None
    assert metrics.reasoning_tokens is None
    assert metrics.total_tokens is None
    assert metrics.transport_retries is None


def test_raw_response_records_transport_retries():
    """Test SDK retry metadata is retained for every completion."""
    client = _DummyClient(use_raw_response=True)
    provider = _DummyProvider(client=cast(OpenAI, client))

    result = provider.chat_completion(
        messages=[{"role": "user", "content": "hi"}],
        response_format=_Answer,
        tool_box=_get_tool_box(lambda args: args),
        query_attempt=3,
    )

    assert result == "done"
    assert [metrics.transport_retries for metrics in provider.completion_metrics] == [
        2,
        2,
    ]
    assert [metrics.query_attempt for metrics in provider.completion_metrics] == [3, 3]


def test_explicit_prompt_cache_reuses_stable_prefix_without_mutation():
    """Test cache routing ignores user content and preserves caller messages."""
    client = _DummyClient()
    provider = _CachingDummyProvider(client=cast(OpenAI, client))
    tool_box = _get_tool_box(lambda args: args)
    first_messages = [
        {"role": "system", "content": "Stable system instructions"},
        {"role": "developer", "content": "Stable developer instructions"},
        {"role": "user", "content": "first query"},
    ]
    expected_first_messages = [dict(message) for message in first_messages]

    provider.chat_completion(
        messages=first_messages, response_format=_Answer, tool_box=tool_box
    )
    provider.chat_completion(
        messages=[
            {"role": "system", "content": "Stable system instructions"},
            {"role": "developer", "content": "Stable developer instructions"},
            {"role": "user", "content": "second query"},
        ],
        response_format=_Answer,
        tool_box=tool_box,
    )
    provider.chat_completion(
        messages=[
            {"role": "system", "content": "Changed instructions"},
            {"role": "user", "content": "second query"},
        ],
        response_format=_Answer,
        tool_box=tool_box,
    )

    first_kwargs = cast(dict[str, object], client.calls[0]["kwargs"])
    second_kwargs = cast(dict[str, object], client.calls[2]["kwargs"])
    third_kwargs = cast(dict[str, object], client.calls[3]["kwargs"])
    assert first_kwargs["prompt_cache_key"] == second_kwargs["prompt_cache_key"]
    assert first_kwargs["prompt_cache_key"] != third_kwargs["prompt_cache_key"]
    assert first_kwargs["prompt_cache_options"] == {"mode": "explicit"}
    sent_messages = cast(list[dict[str, object]], client.calls[0]["messages"])
    assert sent_messages[0]["content"] == "Stable system instructions"
    assert sent_messages[1]["content"] == [
        {
            "type": "text",
            "text": "Stable developer instructions",
            "prompt_cache_breakpoint": {"mode": "explicit"},
        }
    ]
    assert sent_messages[2]["content"] == "first query"
    assert first_messages == expected_first_messages
    assert (
        provider.completion_metrics[0].prompt_cache_key
        == (first_kwargs["prompt_cache_key"])
    )


def test_timeout_defaults_to_120_seconds():
    """Test provider requests default to a 120-second timeout."""
    provider = _DummyProvider(client=cast(OpenAI, _DummyClient()))

    assert provider.timeout_seconds == 120.0


def test_custom_timeout_is_stored():
    """Test providers retain a custom request timeout."""
    provider = _DummyProvider(client=cast(OpenAI, _DummyClient()), timeout_seconds=45.0)

    assert provider.timeout_seconds == 45.0


@mark.parametrize("timeout_seconds", [0.0, -1.0])
def test_timeout_must_be_positive(timeout_seconds: float):
    """Test provider request timeouts must be positive.

    Arguments:
        timeout_seconds: timeout seconds value
    """
    with raises(ValueError, match="timeout_seconds must be positive"):
        _DummyProvider(timeout_seconds=timeout_seconds)


def test_sync_client_is_created_lazily_with_configured_timeout():
    """Test lazy OpenAI client construction uses the configured timeout."""
    with patch("scinoephile.core.llms.openai_provider_base.OpenAI") as openai:
        provider = _DummyProvider(
            api_key="test-api-key",
            base_url="https://example.invalid/v1",
            timeout_seconds=45.0,
        )

        openai.assert_not_called()
        assert provider.sync_client is openai.return_value
        openai.assert_called_once_with(
            api_key="test-api-key", base_url="https://example.invalid/v1", timeout=45.0
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
    """Test cache identity honors the SDK's base URL environment override.

    Arguments:
        monkeypatch: pytest monkeypatch fixture
    """
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
    result = ToolBox().run(tool_name="missing", raw_arguments="{}")

    assert result == {"error": "Unsupported tool 'missing'."}


def test_tool_box_run_returns_error_for_invalid_json_arguments():
    """Test invalid tool-call JSON produces an error payload."""
    result = _get_tool_box(lambda args: args).run(tool_name="do", raw_arguments="{")

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
        _get_tool_box(handler).run(tool_name="do", raw_arguments='{"x": 1}')
