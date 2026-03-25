#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OpenAI LLM Provider."""

from __future__ import annotations

import asyncio
import inspect
import json
from collections.abc import Awaitable
from logging import getLogger
from time import sleep
from typing import TYPE_CHECKING, Any, Unpack, cast, override

from openai import AsyncOpenAI, OpenAI, OpenAIError

from scinoephile.core import ScinoephileError
from scinoephile.llms.base import Answer, ChatCompletionKwargs, LLMProvider
from scinoephile.llms.base.tools import LLMToolSpec, ToolHandler

if TYPE_CHECKING:
    from openai.types.chat import ChatCompletionMessageParam

__all__ = ["OpenAIProvider"]

logger = getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI LLM Provider."""

    def __init__(
        self, client: OpenAI | None = None, aclient: AsyncOpenAI | None = None
    ):
        """Initialize.

        Arguments:
            client: synchronous OpenAI client
            aclient: asynchronous OpenAI client
        """
        self.sync_client = client or OpenAI()
        self.async_client = aclient or AsyncOpenAI()

    @override
    def chat_completion(  # noqa: PLR0912
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer] | None = None,
        model: str | None = "gpt-5.1",
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
            selected_model = model or "gpt-5.1"
            typed_messages = cast(
                "list[ChatCompletionMessageParam]",
                [dict(message) for message in messages],
            )
            if tools:
                openai_tools = self._build_openai_tools(tools)
                handlers = tool_handlers or {}
                request_kwargs: dict[str, Any] = dict(kwargs)
                request_kwargs.setdefault("tool_choice", "auto")
                request_kwargs.setdefault("parallel_tool_calls", False)
                if response_format:
                    create_completion = cast(
                        "Any",
                        self.sync_client.beta.chat.completions.parse,
                    )
                    request_kwargs["response_format"] = response_format
                else:
                    create_completion = cast(
                        "Any", self.sync_client.chat.completions.create
                    )

                max_tool_rounds = 8
                for _round_idx in range(max_tool_rounds):
                    completion = create_completion(
                        messages=typed_messages,
                        model=selected_model,
                        tools=openai_tools,
                        **request_kwargs,
                    )
                    message = completion.choices[0].message
                    tool_calls = message.tool_calls or []
                    if not tool_calls:
                        content = message.content
                        if content is None:
                            raise ScinoephileError(
                                "OpenAI API returned empty message content."
                            )
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
                        tool_name = tool_call.function.name
                        raw_arguments = tool_call.function.arguments
                        tool_result = self._run_tool_handler(
                            tool_name=tool_name,
                            raw_arguments=raw_arguments,
                            tool_handlers=handlers,
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
                    f"{max_tool_rounds} rounds."
                )

            if response_format:
                completion = self.sync_client.beta.chat.completions.parse(
                    messages=typed_messages,
                    response_format=response_format,
                    model=selected_model,
                    **kwargs,
                )
            else:
                completion = self.sync_client.chat.completions.create(
                    messages=typed_messages,
                    model=selected_model,
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

    @staticmethod
    def _build_openai_tools(tools: list[LLMToolSpec]) -> list[dict[str, object]]:
        """Build OpenAI tool payload from local tool specs.

        Arguments:
            tools: local tool specifications
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
                },
            }
            for tool in tools
        ]

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

        try:
            parsed_arguments = json.loads(raw_arguments or "{}")
        except json.JSONDecodeError:
            return {"error": f"Tool '{tool_name}' arguments are not valid JSON."}

        if not isinstance(parsed_arguments, dict):
            return {
                "error": f"Tool '{tool_name}' arguments must decode to a JSON object."
            }

        try:
            return handler(cast("dict[str, Any]", parsed_arguments))
        except Exception:
            logger.exception("Tool '%s' failed during execution.", tool_name)
            return {"error": f"Tool '{tool_name}' failed."}

    @staticmethod
    async def _run_tool_handler_async(
        tool_name: str,
        raw_arguments: str,
        tool_handlers: dict[str, ToolHandler],
    ) -> object:
        """Execute one local tool handler and await async results if needed.

        Arguments:
            tool_name: requested tool name
            raw_arguments: JSON argument payload from model tool call
            tool_handlers: registered tool handlers
        Returns:
            tool result payload
        """
        result = OpenAIProvider._run_tool_handler(
            tool_name=tool_name,
            raw_arguments=raw_arguments,
            tool_handlers=tool_handlers,
        )
        if inspect.isawaitable(result):
            return await result
        return result

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

    @override
    async def chat_completion_async(  # noqa: PLR0912
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer] | None = None,
        model: str | None = "gpt-5.1",
        tools: list[LLMToolSpec] | None = None,
        tool_handlers: dict[str, ToolHandler] | None = None,
        **kwargs: Unpack[ChatCompletionKwargs],
    ) -> str:
        """Return chat completion text asynchronously.

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
            selected_model = model or "gpt-5.1"
            typed_messages = cast(
                "list[ChatCompletionMessageParam]",
                [dict(message) for message in messages],
            )
            if tools:
                openai_tools = self._build_openai_tools(tools)
                handlers = tool_handlers or {}
                request_kwargs: dict[str, Any] = dict(kwargs)
                request_kwargs.setdefault("tool_choice", "auto")
                request_kwargs.setdefault("parallel_tool_calls", False)
                if response_format:
                    create_completion = cast(
                        "Any",
                        self.async_client.beta.chat.completions.parse,
                    )
                    request_kwargs["response_format"] = response_format
                else:
                    create_completion = cast(
                        "Any",
                        self.async_client.chat.completions.create,
                    )

                max_tool_rounds = 8
                for _round_idx in range(max_tool_rounds):
                    completion = await create_completion(
                        messages=typed_messages,
                        model=selected_model,
                        tools=openai_tools,
                        **request_kwargs,
                    )
                    message = completion.choices[0].message
                    tool_calls = message.tool_calls or []
                    if not tool_calls:
                        content = message.content
                        if content is None:
                            raise ScinoephileError(
                                "OpenAI API returned empty message content."
                            )
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
                        tool_name = tool_call.function.name
                        raw_arguments = tool_call.function.arguments
                        tool_result = await self._run_tool_handler_async(
                            tool_name=tool_name,
                            raw_arguments=raw_arguments,
                            tool_handlers=handlers,
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
                    f"{max_tool_rounds} rounds."
                )

            if response_format:
                completion = await self.async_client.beta.chat.completions.parse(
                    messages=typed_messages,
                    response_format=response_format,
                    model=selected_model,
                    **kwargs,
                )
            else:
                completion = await self.async_client.chat.completions.create(
                    messages=typed_messages,
                    model=selected_model,
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
                await asyncio.sleep(1)
            raise ScinoephileError(
                f"OpenAI API error ({exc_code=}, {exc_type=} {exc_param=}): {exc}"
            ) from exc
