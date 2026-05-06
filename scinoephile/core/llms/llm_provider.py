#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypedDict, Unpack

from .answer import Answer
from .tool_box import ToolBox

__all__ = [
    "ChatCompletionKwargs",
    "LLMProvider",
]


class ChatCompletionKwargs(TypedDict, total=False):
    """Keyword arguments for LLM chat completion methods.

    These correspond to common parameters accepted by chat-completion style APIs.
    """

    temperature: float
    """Sampling temperature."""

    max_tokens: int
    """Maximum number of tokens to generate."""

    top_p: float
    """Nucleus sampling cutoff."""

    frequency_penalty: float
    """Penalty for repeated token frequency."""

    presence_penalty: float
    """Penalty for repeated token presence."""

    stop: str | list[str]
    """Stop sequence or sequences."""

    seed: int
    """Deterministic sampling seed."""


class LLMProvider(ABC):
    """ABC for LLM providers."""

    @abstractmethod
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
            tool_box: available tools
            **kwargs: provider-specific keyword arguments
        Returns:
            completion text from the model
        Raises:
            ScinoephileError: Error during chat completion
        """
        raise NotImplementedError()
