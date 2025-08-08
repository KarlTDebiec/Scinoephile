#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OpenAI LLM Provider."""

from __future__ import annotations

import asyncio
from time import sleep
from typing import Any, override

from openai import AsyncOpenAI, OpenAI, OpenAIError

from scinoephile.core import ScinoephileError
from scinoephile.core.abcs.answer import Answer
from scinoephile.core.abcs.llm_provider import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI LLM Provider."""

    def __init__(
        self, client: OpenAI | None = None, aclient: AsyncOpenAI | None = None
    ):
        """Initialize.

        Arguments:
            client: OpenAI client
            aclient: Asynchronous OpenAI client
        """
        self.client = client or OpenAI()
        self.aclient = aclient or AsyncOpenAI()

    @override
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
        Raises:
            ScinoephileError: Error during chat completion
        """
        try:
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
        except OpenAIError as exc:
            exc_code = getattr(exc, "code", None)
            exc_type = getattr(exc, "type", None)
            exc_param = getattr(exc, "param", None)
            if exc_code == "rate_limit_exceeded":
                sleep(1)
            raise ScinoephileError(
                f"OpenAI API error ({exc_code=}, {exc_type=} {exc_param=}): {exc}"
            ) from exc

    @override
    async def achat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.0,
        seed: int = 0,
        response_format: type[Answer] | None = None,
    ) -> str:
        """Complete chat message asynchronously.

        Arguments:
            model: Model to use for completion
            messages: Messages to send
            temperature: Sampling temperature
            seed: Seed for reproducibility
            response_format: Response format
        Returns:
            Completion text from the model
        Raises:
            ScinoephileError: Error during chat completion
        """
        try:
            if response_format:
                completion = await self.aclient.beta.chat.completions.parse(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    seed=seed,
                    response_format=response_format,
                )
            else:
                completion = await self.aclient.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    seed=seed,
                )
            return completion.choices[0].message.content
        except OpenAIError as exc:
            exc_code = getattr(exc, "code", None)
            exc_type = getattr(exc, "type", None)
            exc_param = getattr(exc, "param", None)
            if exc_code == "rate_limit_exceeded":
                await asyncio.sleep(1)
            raise ScinoephileError(
                f"OpenAI API error ({exc_code=}, {exc_type=} {exc_param=}): {exc}"
            ) from exc
