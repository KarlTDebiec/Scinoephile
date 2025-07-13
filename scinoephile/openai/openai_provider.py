# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM provider that uses the OpenAI API."""

from __future__ import annotations

from typing import Any

from openai import OpenAI

from scinoephile.core.abcs.llm_provider import LLMProvider


class OpenAiProvider(LLMProvider):
    """Provider using OpenAI chat completions."""

    def __init__(self, client: OpenAI | None = None):
        """Initialize provider."""
        self.client = client or OpenAI()

    def chat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.0,
    ) -> str:
        """Return chat completion text."""
        completion = self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        return completion.choices[0].message.content
