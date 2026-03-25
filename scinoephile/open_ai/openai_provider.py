#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OpenAI LLM Provider."""

from __future__ import annotations

import json
from collections.abc import Awaitable
from logging import getLogger
from time import sleep
from typing import TYPE_CHECKING, Any, Unpack, cast, override

from openai import OpenAI, OpenAIError

from scinoephile.core import ScinoephileError
from scinoephile.llms.base import Answer, ChatCompletionKwargs, LLMProvider
from scinoephile.llms.base.tools import LLMToolSpec, ToolHandler

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionMessageParam
    from openai.types.chat.chat_completion_function_tool_param import (
        ChatCompletionFunctionToolParam,
    )

__all__ = ["OpenAIProvider"]

logger = getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI LLM Provider."""

    def __init__(self, client: OpenAI | None = None):
        """Initialize.

        Arguments:
            client: synchronous OpenAI client
        """
        self.sync_client = client or OpenAI()

    @override
    def chat_completion(  # noqa: PLR0912
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer] | None = None,
        model: str = "gpt-5.1",
        tools: list[LLMToolSpec] | None = None,
        tool_handlers: dict[str, ToolHandler] | None = None,
        **kwargs: Unpack[ChatCompletionKwargs],
    ) -> str:
        """Return chat completion text synchronously.

        Arguments:
            messages: messages to send
            response_format: response format
            tools: available function-tool definitions
            tool_handlers: handlers for available function tools
            model: model to use
            **kwargs: additional keyword arguments
        Returns:
            completion text from the model
        Raises:
            ScinoephileError: Error during chat completion
        """
        try:
            typed_messages = self._get_typed_messages(messages)
            if tools:
                return self._chat_completion_with_tools(
                    typed_messages=typed_messages,
                    response_format=response_format,
                    model=model,
                    tools=tools,
                    tool_handlers=tool_handlers or {},
                    **kwargs,
                )

            if response_format:
                completion = self.sync_client.beta.chat.completions.parse(
                    messages=typed_messages,
                    response_format=response_format,
                    model=model,
                    **kwargs,
                )
            else:
                completion = self.sync_client.chat.completions.create(
                    messages=typed_messages,
                    model=model,
                    **kwargs,
                )
            content = completion.choices[0].message.content
            if content is None:
                raise ScinoephileError("OpenAI API returned empty message content.")
            return content
        except OpenAIError as exc:
            exc_code = getattr(exc, "code", None)
            exc_type = getattr(exc, "type", None)
            exc_param = getattr(exc, "param", None)
            # TODO: Parse out rate limit and backoff properly
            # Probably subclass Scinoephile Error and store time to wait there
            if exc_code == "rate_limit_exceeded":
                sleep(1)
            raise ScinoephileError(
                f"OpenAI API error ({exc_code=}, {exc_type=} {exc_param=}): {exc}"
            ) from exc

    def _chat_completion_with_tools(
        self,
        typed_messages: list[ChatCompletionMessageParam],
        response_format: type[Answer] | None,
        model: str,
        tools: list[LLMToolSpec],
        tool_handlers: dict[str, ToolHandler],
        **kwargs: Unpack[ChatCompletionKwargs],
    ) -> str:
        """Run a tool-calling chat loop until a final assistant message is returned.

        Arguments:
            typed_messages: OpenAI-typed chat messages
            response_format: response format
            model: model to use
            tools: available function-tool definitions
            tool_handlers: handlers for available function tools
            **kwargs: additional keyword arguments
        Returns:
            completion text from the model
        """
        openai_tools = self._build_openai_tools(tools)
        request_kwargs: dict[str, Any] = dict(kwargs)
        request_kwargs.setdefault("tool_choice", "auto")
        request_kwargs.setdefault("parallel_tool_calls", False)
        if response_format:
            request_kwargs["response_format"] = response_format

        max_tool_rounds = 8
        for round_idx in range(max_tool_rounds):
            if response_format:
                completion = self._parse_completion(
                    messages=typed_messages,
                    model=model,
                    tools=openai_tools,
                    **request_kwargs,
                )
            else:
                completion = self._create_completion(
                    messages=typed_messages,
                    model=model,
                    tools=openai_tools,
                    **request_kwargs,
                )

            message = completion.choices[0].message
            tool_calls = message.tool_calls or []
            if not tool_calls:
                content = message.content
                if content is None:
                    raise ScinoephileError("OpenAI API returned empty message content.")
                return content

            typed_messages.append(
                {
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
            )
            for tool_call in tool_calls:
                tool_result = self._run_tool_handler(
                    tool_name=tool_call.function.name,
                    raw_arguments=tool_call.function.arguments,
                    tool_handlers=tool_handlers,
                )
                typed_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": self._serialize_tool_result(tool_result),
                    }
                )

        raise ScinoephileError(
            "OpenAI tool-calling did not reach a final response after "
            f"{round_idx + 1} rounds."
        )

    @staticmethod
    def _get_typed_messages(
        messages: list[dict[str, Any]],
    ) -> list[ChatCompletionMessageParam]:
        """Normalize message payloads for the OpenAI client.

        Arguments:
            messages: raw chat messages
        Returns:
            OpenAI-typed chat messages
        """
        return cast(
            "list[ChatCompletionMessageParam]",
            [dict(message) for message in messages],
        )

    def _parse_completion(self, **kwargs: Any) -> Any:
        """Call the OpenAI structured-output API behind a typed boundary."""
        return cast("Any", self.sync_client.beta.chat.completions.parse)(**kwargs)

    def _create_completion(self, **kwargs: Any) -> Any:
        """Call the OpenAI chat completion API behind a typed boundary."""
        return cast("Any", self.sync_client.chat.completions.create)(**kwargs)

    @staticmethod
    def _build_openai_tools(
        tools: list[LLMToolSpec],
    ) -> list[ChatCompletionFunctionToolParam]:
        """Build OpenAI tool payload from local tool specs.

        Arguments:
            tools: local tool specifications
        Returns:
            OpenAI-compatible function-tool payloads
        """
        return cast(
            "list[ChatCompletionFunctionToolParam]",
            [
                {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["parameters"],
                    },
                }
                for tool in tools
            ],
        )

    @staticmethod
    def _parse_tool_arguments(
        tool_name: str,
        raw_arguments: str,
    ) -> dict[str, Any]:
        """Parse tool arguments from model-produced JSON.

        Arguments:
            tool_name: requested tool name
            raw_arguments: JSON argument payload from model tool call
        Returns:
            parsed arguments, or an error payload
        """
        try:
            parsed_arguments = json.loads(raw_arguments or "{}")
        except json.JSONDecodeError:
            return {"error": f"Tool '{tool_name}' arguments are not valid JSON."}

        if not isinstance(parsed_arguments, dict):
            return {
                "error": f"Tool '{tool_name}' arguments must decode to a JSON object."
            }

        return parsed_arguments

    @staticmethod
    def _run_tool_handler(
        tool_name: str,
        raw_arguments: str,
        tool_handlers: dict[str, ToolHandler],
    ) -> object | Awaitable[object]:
        """Execute one local tool handler with parsed arguments.

        Arguments:
            tool_name: requested tool name
            raw_arguments: JSON argument payload from model tool call
            tool_handlers: registered tool handlers
        Returns:
            tool result payload
        """
        handler = tool_handlers.get(tool_name)
        if handler is None:
            return {"error": f"Unsupported tool '{tool_name}'."}

        parsed_arguments = OpenAIProvider._parse_tool_arguments(
            tool_name=tool_name,
            raw_arguments=raw_arguments,
        )
        if isinstance(parsed_arguments, dict) and "error" in parsed_arguments:
            return parsed_arguments

        try:
            return handler(parsed_arguments)
        except Exception:
            logger.exception("Tool '%s' failed during execution.", tool_name)
            return {"error": f"Tool '{tool_name}' failed."}

    @staticmethod
    def _serialize_tool_result(result: object) -> str:
        """Serialize tool-call result for tool response message content.

        Arguments:
            result: tool execution result
        Returns:
            serialized JSON content
        """
        try:
            return json.dumps(result, ensure_ascii=False)
        except TypeError:
            return json.dumps({"result": str(result)}, ensure_ascii=False)
