#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared OpenAI-SDK implementation for OpenAI-compatible providers."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import asdict
from hashlib import sha256
from json import dumps
from logging import getLogger
from time import monotonic, sleep
from typing import Any, Unpack, cast

from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletionMessageFunctionToolCall
from pydantic import JsonValue, ValidationError

from scinoephile.core.exceptions import ScinoephileError

from .answer import Answer
from .llm_provider import ChatCompletionKwargs, ChatCompletionMetrics, LLMProvider
from .tool_box import ToolBox

__all__ = ["OpenAIProviderBase"]

logger = getLogger(__name__)


class OpenAIProviderBase(LLMProvider):
    """Shared OpenAI-SDK implementation for OpenAI-compatible providers."""

    model: str
    """Model identifier."""

    api_key_env_var_name: str | None = None
    """Environment variable name used for the API key."""

    base_url: str | None = None
    """Default base URL for the OpenAI client."""

    timeout_seconds: float
    """Timeout for each provider request."""

    def __init__(
        self,
        client: OpenAI | None = None,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: float = 120.0,
    ):
        """Initialize.

        Arguments:
            client: synchronous OpenAI client
            api_key: explicit API key; if omitted, env var is used if configured
            base_url: explicit base URL; if omitted, provider default is used
            model: model identifier override
            timeout_seconds: timeout for each provider request
        Raises:
            ValueError: if timeout_seconds is not positive
        """
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive.")
        self._sync_client: OpenAI | None = client
        self._api_key: str | None = api_key
        self.timeout_seconds = timeout_seconds
        self.completion_metrics: list[ChatCompletionMetrics] = []
        """Usage and timing for completions made by this provider instance."""
        if base_url is not None:
            self.base_url = base_url
        if model is not None:
            self.model = model

    @property
    def api_key(self) -> str | None:
        """API key for the OpenAI client."""
        if self._api_key is not None:
            return self._api_key
        if self.api_key_env_var_name is None:
            return None
        return os.environ.get(self.api_key_env_var_name)

    @property
    def cache_identity(self) -> dict[str, JsonValue]:
        """Stable, non-secret OpenAI-compatible provider configuration."""
        identity = super().cache_identity
        base_url = None
        if self._sync_client is not None:
            client_base_url = getattr(self._sync_client, "base_url", None)
            if client_base_url is not None:
                base_url = str(client_base_url)
        if base_url is None:
            base_url = self.base_url
        if base_url is None:
            base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        if base_url is not None:
            base_url = base_url.rstrip("/")
        identity.update(
            {
                "model": self.model,
                "base_url": base_url,
                "use_strict_tools": self.use_strict_tools,
            }
        )
        return identity

    @property
    def sync_client(self) -> OpenAI:
        """Synchronous OpenAI client."""
        if self._sync_client is None:
            self._sync_client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout_seconds,
            )
        return self._sync_client

    @property
    def use_explicit_prompt_caching(self) -> bool:
        """Whether requests should mark and route a stable cached prefix."""
        return False

    @property
    def use_strict_tools(self) -> bool:
        """Whether function tool schemas should request strict mode by default."""
        return True

    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer],
        tool_box: ToolBox | None = None,
        *,
        operation: str | None = None,
        query_key_sha256: str | None = None,
        query_attempt: int = 1,
        **kwargs: Unpack[ChatCompletionKwargs],
    ) -> str:
        """Return chat completion text synchronously.

        Arguments:
            messages: messages to send
            response_format: structured response format
            tool_box: available tools and handlers
            operation: stable LLM operation identifier
            query_key_sha256: SHA-256 digest of the semantic query key
            query_attempt: one-based answer-validation attempt
            **kwargs: additional keyword arguments
        Returns:
            completion text from the model
        Raises:
            ScinoephileError: Error during chat completion
        """
        try:
            # Organize arguments
            messages = [dict(message) for message in messages]
            tool_box = tool_box or ToolBox()
            openai_tools = self._build_openai_tools(tool_box) if tool_box else None
            prompt_cache_key = None
            if self.use_explicit_prompt_caching:
                messages, prompt_cache_key = self._configure_prompt_cache(
                    messages, response_format, openai_tools
                )
            request_kwargs = self._build_request_kwargs(
                response_format, openai_tools, kwargs
            )
            if prompt_cache_key is not None:
                request_kwargs["prompt_cache_key"] = prompt_cache_key
                request_kwargs["prompt_cache_options"] = {"mode": "explicit"}

            # Query provider, process tool calls if applicable, and return
            max_tool_rounds = 8
            for tool_round in range(1, max_tool_rounds + 1):
                # Query provider
                start_time = monotonic()
                completion, transport_retries = self._query(messages, request_kwargs)
                metrics = self._get_completion_metrics(
                    completion,
                    operation=operation,
                    query_key_sha256=query_key_sha256,
                    query_attempt=query_attempt,
                    tool_round=tool_round,
                    transport_retries=transport_retries,
                    latency_seconds=monotonic() - start_time,
                    prompt_cache_key=prompt_cache_key,
                )
                self.completion_metrics.append(metrics)
                logger.info(f"LLM completion metrics: {dumps(asdict(metrics))}")
                message = completion.choices[0].message
                tool_calls = cast(
                    list[ChatCompletionMessageFunctionToolCall],
                    message.tool_calls or [],
                )

                # If no tool calls requested, return
                if not tool_calls:
                    content = message.content
                    if content is None:
                        raise ScinoephileError(
                            "OpenAI-compatible API returned empty message content."
                        )
                    return content

                # If tool call requested without tools available, raise Exception
                if openai_tools is None:
                    raise ScinoephileError(
                        "OpenAI-compatible API returned tool calls even though no "
                        "tools were provided."
                    )

                # Call tool
                messages.extend(self._call_tool(message, tool_calls, tool_box))

            # The provider never produced a final answer within the allowed rounds.
            raise ScinoephileError(
                f"Tool-calling did not reach a final response after {max_tool_rounds} "
                "rounds."
            )
        except OpenAIError as exc:
            exc_code = getattr(exc, "code", None)
            exc_type = getattr(exc, "type", None)
            exc_param = getattr(exc, "param", None)
            if exc_code == "rate_limit_exceeded":
                logger.error(
                    f"OpenAI-compatible API rate limit exceeded "
                    f"({exc_code=}, {exc_type=} {exc_param=}): {exc}"
                )
                sleep(1)
            raise ScinoephileError(
                f"OpenAI-compatible API error ({exc_code=}, {exc_type=} {exc_param=}): "
                f"{exc}"
            ) from exc
        except ValidationError as exc:
            raise ScinoephileError(
                "OpenAI-compatible API returned content that failed structured "
                "response validation."
            ) from exc

    def get_completion_metrics(self) -> tuple[ChatCompletionMetrics, ...]:
        """Get completion metrics recorded by this provider instance.

        Returns:
            immutable snapshot of recorded completion metrics
        """
        return tuple(self.completion_metrics)

    def _build_openai_tools(self, tool_box: ToolBox) -> list[dict[str, object]]:
        """Build OpenAI tool payload from local tool specs.

        Arguments:
            tool_box: local tools and handlers
        Returns:
            OpenAI-compatible function-tool payloads
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"],
                    "strict": self.use_strict_tools,
                },
            }
            for tool in tool_box.specs
        ]

    def _query(
        self, messages: list[dict[str, Any]], request_kwargs: dict[str, Any]
    ) -> tuple[Any, int | None]:
        """Query provider for completion.

        Arguments:
            messages: messages to send
            request_kwargs: OpenAI SDK request keyword arguments
        Returns:
            completion response object and transport retry count, if available
        """
        completions = self.sync_client.beta.chat.completions
        raw_completions = getattr(completions, "with_raw_response", None)
        if raw_completions is None:
            completion = completions.parse(
                messages=messages,  # ty:ignore[invalid-argument-type]
                model=self.model,
                timeout=self.timeout_seconds,
                **request_kwargs,
            )
            return completion, None
        response = raw_completions.parse(
            messages=messages,
            model=self.model,
            timeout=self.timeout_seconds,
            **request_kwargs,
        )
        return response.parse(), getattr(response, "retries_taken", None)

    def _configure_prompt_cache(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer],
        openai_tools: list[dict[str, object]] | None,
    ) -> tuple[list[dict[str, Any]], str | None]:
        """Mark the stable message prefix and derive its routing key.

        Arguments:
            messages: completion messages
            response_format: structured response format
            openai_tools: serialized OpenAI tool payload
        Returns:
            copied messages with an explicit breakpoint and its cache key
        """
        stable_end = -1
        for index, message in enumerate(messages):
            if message.get("role") not in {"system", "developer"}:
                break
            stable_end = index
        if stable_end < 0:
            return messages, None

        stable_content = messages[stable_end].get("content")
        if not isinstance(stable_content, str):
            return messages, None
        cache_payload = {
            "messages": messages[: stable_end + 1],
            "model": self.model,
            "response_format": response_format.model_json_schema(),
            "tools": openai_tools,
        }
        digest = sha256(
            dumps(
                cache_payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
            ).encode()
        ).hexdigest()[:32]
        messages[stable_end]["content"] = [
            {
                "type": "text",
                "text": stable_content,
                "prompt_cache_breakpoint": {"mode": "explicit"},
            }
        ]
        return messages, f"scinoephile:{digest}"

    def _get_completion_metrics(
        self,
        completion: Any,
        *,
        operation: str | None,
        query_key_sha256: str | None,
        query_attempt: int,
        tool_round: int,
        transport_retries: int | None,
        latency_seconds: float,
        prompt_cache_key: str | None,
    ) -> ChatCompletionMetrics:
        """Extract usage and timing from one completion.

        Arguments:
            completion: provider completion response
            operation: stable LLM operation identifier
            query_key_sha256: SHA-256 digest of the semantic query key
            query_attempt: one-based answer-validation attempt
            tool_round: one-based tool-calling round
            transport_retries: transport retries taken by the SDK, if reported
            latency_seconds: wall-clock request latency
            prompt_cache_key: provider prompt-cache routing key
        Returns:
            normalized completion metrics
        """
        usage = getattr(completion, "usage", None)
        prompt_details = getattr(usage, "prompt_tokens_details", None)
        completion_details = getattr(usage, "completion_tokens_details", None)
        return ChatCompletionMetrics(
            operation=operation,
            query_key_sha256=query_key_sha256,
            model=self.model,
            query_attempt=query_attempt,
            tool_round=tool_round,
            input_tokens=getattr(usage, "prompt_tokens", None),
            cached_input_tokens=getattr(prompt_details, "cached_tokens", None),
            cache_write_tokens=getattr(prompt_details, "cache_write_tokens", None),
            output_tokens=getattr(usage, "completion_tokens", None),
            reasoning_tokens=getattr(completion_details, "reasoning_tokens", None),
            total_tokens=getattr(usage, "total_tokens", None),
            transport_retries=transport_retries,
            latency_seconds=latency_seconds,
            prompt_cache_key=prompt_cache_key,
        )

    @staticmethod
    def _call_tool(
        message: Any,
        tool_calls: list[ChatCompletionMessageFunctionToolCall],
        tool_box: ToolBox,
    ) -> list[dict[str, Any]]:
        """Call a tool.

        Arguments:
            message: assistant message returned by the provider
            tool_calls: tool calls requested by the provider
            tool_box: available tools and handlers
        Returns:
            messages to append to the conversation history
        """
        # Prepare assistant message to precede tool call results
        assistant_message: dict[str, Any] = {
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
                for tool_call in tool_calls
            ],
        }
        reasoning_content = getattr(message, "reasoning_content", None)
        if reasoning_content:
            assistant_message["reasoning_content"] = reasoning_content
        tool_messages: list[dict[str, Any]] = [assistant_message]

        # Execute each requested tool and append response
        for tool_call in tool_calls:
            tool_result = tool_box.run(
                tool_call.function.name, tool_call.function.arguments
            )
            tool_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_box.serialize_result(tool_result),
                }
            )
        return tool_messages

    @staticmethod
    def _build_request_kwargs(
        response_format: type[Answer],
        openai_tools: list[dict[str, object]] | None,
        kwargs: Mapping[str, Any],
    ) -> dict[str, Any]:
        """Build request kwargs for one completion call.

        Arguments:
            response_format: structured response format, if any
            openai_tools: serialized OpenAI tool payload
            kwargs: caller-supplied completion kwargs
        Returns:
            request kwargs for the OpenAI SDK call
        """
        request_kwargs: dict[str, Any] = dict(kwargs)
        request_kwargs["response_format"] = response_format
        if openai_tools is not None:
            request_kwargs.setdefault("tool_choice", "auto")
            request_kwargs.setdefault("parallel_tool_calls", False)
            request_kwargs["tools"] = openai_tools
        return request_kwargs
