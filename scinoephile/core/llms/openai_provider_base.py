#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared OpenAI-SDK implementation for OpenAI-compatible providers."""

from __future__ import annotations

import os
from logging import getLogger
from time import sleep
from typing import Any, Unpack

from openai import OpenAI, OpenAIError

from scinoephile.core import ScinoephileError

from .answer import Answer
from .llm_provider import ChatCompletionKwargs, LLMProvider
from .tools import ToolBox

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

    def chat_completion(  # noqa: PLR0912
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
            messages = [dict(message) for message in messages]
            tool_box = tool_box or ToolBox()
            openai_tools = self._build_openai_tools(tool_box) if tool_box else None
            request_kwargs: dict[str, Any] = dict(kwargs)
            if response_format:
                request_kwargs["response_format"] = response_format
            if openai_tools is not None:
                request_kwargs.setdefault("tool_choice", "auto")
                request_kwargs.setdefault("parallel_tool_calls", False)
                request_kwargs["tools"] = openai_tools

            max_tool_rounds = 8
            for round_idx in range(max_tool_rounds):
                if response_format:
                    completion = self.sync_client.beta.chat.completions.parse(
                        messages=messages,  # ty:ignore[invalid-argument-type]
                        model=self.model,
                        **request_kwargs,
                    )
                else:
                    completion = self.sync_client.chat.completions.create(
                        messages=messages,
                        model=self.model,
                        **request_kwargs,
                    )  # ty:ignore[no-matching-overload]

                message = completion.choices[0].message
                tool_calls = message.tool_calls or []

                if not tool_calls:
                    content = message.content
                    if content is None:
                        raise ScinoephileError(
                            "OpenAI-compatible API returned empty message content."
                        )
                    return content

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
                messages.append(assistant_message)
                for tool_call in tool_calls:
                    tool_result = tool_box.run(
                        tool_name=tool_call.function.name,
                        raw_arguments=tool_call.function.arguments,
                    )
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_box.serialize_result(tool_result),
                        }
                    )

                if openai_tools is None:
                    raise ScinoephileError(
                        "OpenAI-compatible API returned tool calls even though no "
                        "tools were provided."
                    )

            raise ScinoephileError(
                "Tool-calling did not reach a final response after "
                f"{round_idx + 1} rounds."
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
