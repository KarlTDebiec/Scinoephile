#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .answer import Answer

__all__ = ["LLMProvider"]


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer] | None = None,
        **kwargs: Any,
    ) -> str:
        """Return chat completion text synchronously.

        Arguments:
            messages: messages to send
            response_format: response format
            kwargs: additional keyword arguments
        Returns:
            completion text from the model
        Raises:
            ScinoephileError: Error during chat completion
        """
        pass

    @abstractmethod
    async def chat_completion_async(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer] | None = None,
        **kwargs: Any,
    ) -> str:
        """Return chat completion text asynchronously.

        Arguments:
            messages: messages to send
            response_format: response format
            kwargs: additional keyword arguments
        Returns:
            completion text from the model
        Raises:
            ScinoephileError: Error during chat completion
        """
        pass
