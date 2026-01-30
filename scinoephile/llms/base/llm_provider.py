#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypedDict, Unpack

from .answer import Answer

__all__ = ["LLMProvider", "ChatCompletionKwargs"]


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


class LLMProvider(ABC):
    """ABC for LLM providers."""

    @abstractmethod
    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer] | None = None,
        **kwargs: Unpack[ChatCompletionKwargs],
    ) -> str:
        """Return chat completion text synchronously.

        Arguments:
            messages: messages to send
            response_format: response format
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
        **kwargs: Unpack[ChatCompletionKwargs],
    ) -> str:
        """Return chat completion text asynchronously.

        Arguments:
            messages: messages to send
            response_format: response format
            **kwargs: additional keyword arguments
        Returns:
            completion text from the model
        Raises:
            ScinoephileError: Error during chat completion
        """
        raise NotImplementedError()
