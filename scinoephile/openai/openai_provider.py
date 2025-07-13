#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OpenAI LLM Provider."""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from scinoephile.core.abcs.answer import Answer
from scinoephile.core.abcs.llm_provider import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI LLM Provider."""

    def __init__(self, client: OpenAI | None = None):
        """Initialize.

        Arguments:
            client: OpenAI client
        """
        self.client = client or OpenAI()

    def chat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.0,
        seed: int = 0,
        response_format: type[Answer] | None = None,
    ) -> str:
        """Complete chat message.

        Arguments:
            model: Model to use for completion
            messages: Messages to send
            temperature: Sampling temperature
            seed: Seed for reproducibility
            response_format: Response format
        Returns:
            Completion text from the model
        """
        if response_format:
            completion = self.client.beta.chat.completions.parse(
                model=model,
                messages=messages,
                temperature=temperature,
                seed=seed,
                response_format=response_format,
            )
        else:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                seed=seed,
            )
        return completion.choices[0].message.content
