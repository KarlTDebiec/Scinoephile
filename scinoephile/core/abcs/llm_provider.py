#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base class for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from scinoephile.core.abcs.answer import Answer


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def chat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.0,
        seed: int = 0,
        response_format: type[Answer] | None = None,
    ) -> str:
        """Return chat completion text.

        Arguments:
            model: Model to use for completion
            messages: Messages to send
            temperature: Sampling temperature for randomness
            seed: Seed for reproducibility
            response_format: Response format
        Returns:
            Completion text from the model
        Raises:
            ScinoephileError: Error during chat completion
        """
        raise NotImplementedError()

    @abstractmethod
    async def achat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.0,
        seed: int = 0,
        response_format: type[Answer] | None = None,
    ) -> str:
        """Return chat completion text asynchronously.

        Arguments:
            model: Model to use for completion
            messages: Messages to send
            temperature: Sampling temperature for randomness
            seed: Seed for reproducibility
            response_format: Response format
        Returns:
            Completion text from the model
        Raises:
            ScinoephileError: Error during chat completion
        """
        raise NotImplementedError()
