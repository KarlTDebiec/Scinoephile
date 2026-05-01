#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared OpenAI-SDK implementation for OpenAI-compatible providers."""

from __future__ import annotations

import os
from logging import getLogger
from time import sleep
from typing import Any, Unpack, cast

from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletionMessageFunctionToolCall

from scinoephile.core import ScinoephileError

from .answer import Answer
from .llm_provider import ChatCompletionKwargs, LLMProvider
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

    def __init__(
        self,
        client: OpenAI | None = None,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
    ):
        """Initialize.

        Arguments:
            client: synchronous OpenAI client
            api_key: explicit API key; if omitted, env var is used if configured
            base_url: explicit base URL; if omitted, provider default is used
            model: model identifier override
        """
        self._sync_client: OpenAI | None = client
        self._api_key: str | None = api_key
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
    def sync_client(self) -> OpenAI:
        """Synchronous OpenAI client."""
        if self._sync_client is None:
            self._sync_client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self._sync_client

    @property
    def use_strict_tools(self) -> bool:
        """Whether function tool schemas should request strict mode by default."""
        return True

    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer] | None = None,
        tool_box: ToolBox | None = None,
        **kwargs: Unpack[ChatCompletionKwargs],
    ) -> str:
        """Return chat completion text synchronously.

        Arguments:
            messages: messages to send
            response_format: response format
            tool_box: available tools and handlers
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
            request_kwargs = self._build_request_kwargs(
                response_format, openai_tools, kwargs
            )

            # Query provider, process tool calls if applicable, and return
            max_tool_rounds = 8
            for _ in range(max_tool_rounds):
                # Query provider
                completion = self._query(messages, response_format, request_kwargs)
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
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer] | None,
        request_kwargs: dict[str, Any],
    ) -> Any:
        """Query provider for completion.

        Arguments:
            messages: messages to send
            response_format: structured response format, if any
            request_kwargs: OpenAI SDK request keyword arguments
        Returns:
            completion response object
        """
        if response_format:
            return self.sync_client.beta.chat.completions.parse(
                messages=messages,  # ty:ignore[invalid-argument-type]
                model=self.model,
                **request_kwargs,
            )
        return self.sync_client.chat.completions.create(
            messages=messages,
            model=self.model,
            **request_kwargs,
        )  # ty:ignore[no-matching-overload]

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
        response_format: type[Answer] | None,
        openai_tools: list[dict[str, object]] | None,
        kwargs: dict[str, Any],
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
        if response_format:
            request_kwargs["response_format"] = response_format
        if openai_tools is not None:
            request_kwargs.setdefault("tool_choice", "auto")
            request_kwargs.setdefault("parallel_tool_calls", False)
            request_kwargs["tools"] = openai_tools
        return request_kwargs
