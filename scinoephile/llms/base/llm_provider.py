#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, TypedDict, Unpack

if TYPE_CHECKING:
    from .answer import Answer

__all__ = [
    "ChatCompletionKwargs",
    "LLMToolSpec",
    "LLMProvider",
    "ToolHandler",
]


class ChatCompletionKwargs(TypedDict, total=False):
    """Keyword arguments for LLM chat completion methods.

    These correspond to common parameters accepted by LLM APIs like OpenAI.
    """

    temperature: float
    max_tokens: int
    top_p: float
    frequency_penalty: float
    presence_penalty: float
    stop: str | list[str]
    seed: int


class LLMToolSpec(TypedDict):
    """Specification for one LLM-callable function tool."""

    name: str
    description: str
    parameters: dict[str, object]


type ToolHandler = Callable[[dict[str, Any]], object]
"""Function that executes one tool call from parsed JSON arguments."""


class LLMProvider(ABC):
    """ABC for LLM providers."""

    @abstractmethod
    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer] | None = None,
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
            **kwargs: additional keyword arguments
        Returns:
            completion text from the model
        Raises:
            ScinoephileError: Error during chat completion
        """
        raise NotImplementedError()

    @abstractmethod
    async def chat_completion_async(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer] | None = None,
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
            **kwargs: additional keyword arguments
        Returns:
            completion text from the model
        Raises:
            ScinoephileError: Error during chat completion
        """
        raise NotImplementedError()
