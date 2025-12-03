#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OpenAI LLM Provider."""

from __future__ import annotations

from typing import Any, override

from openai import AsyncOpenAI, OpenAI, OpenAIError

from scinoephile.core import RateLimitError, ScinoephileError
from scinoephile.core.abcs.answer import Answer
from scinoephile.core.abcs.llm_provider import LLMProvider


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
    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer] | None = None,
        model: str = "gpt-5.1",
        **kwargs: Any,
    ) -> str:
        """Return chat completion text synchronously.

        Arguments:
            messages: messages to send
            response_format: response format
            model: model to use
            kwargs: additional keyword arguments
        Returns:
            completion text from the model
        Raises:
            ScinoephileError: Error during chat completion
        """
        try:
            if response_format:
                completion = self.sync_client.beta.chat.completions.parse(
                    messages=messages,
                    response_format=response_format,
                    model=model,
                    **kwargs,
                )
            else:
                completion = self.sync_client.chat.completions.create(
                    messages=messages,
                    model=model,
                    **kwargs,
                )
            return completion.choices[0].message.content
        except OpenAIError as exc:
            exc_code = getattr(exc, "code", None)
            exc_type = getattr(exc, "type", None)
            exc_param = getattr(exc, "param", None)
            if exc_code == "rate_limit_exceeded":
                raise RateLimitError(
                    (
                        f"OpenAI API rate limit error "
                        f"({exc_code=}, {exc_type=} {exc_param=}): {exc}"
                    ),
                    wait_time=self._get_retry_after(exc),
                ) from exc
            raise ScinoephileError(
                f"OpenAI API error ({exc_code=}, {exc_type=} {exc_param=}): {exc}"
            ) from exc

    @override
    async def chat_completion_async(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer] | None = None,
        model: str = "gpt-5.1",
        **kwargs: Any,
    ) -> str:
        """Return chat completion text asynchronously.

        Arguments:
            messages: messages to send
            response_format: response format
            model: model to use
            kwargs: additional keyword arguments
        Returns:
            completion text from the model
        Raises:
            ScinoephileError: Error during chat completion
        """
        try:
            if response_format:
                completion = await self.async_client.beta.chat.completions.parse(
                    messages=messages,
                    response_format=response_format,
                    model=model,
                    **kwargs,
                )
            else:
                completion = await self.async_client.chat.completions.create(
                    messages=messages,
                    model=model,
                    **kwargs,
                )
            return completion.choices[0].message.content
        except OpenAIError as exc:
            exc_code = getattr(exc, "code", None)
            exc_type = getattr(exc, "type", None)
            exc_param = getattr(exc, "param", None)
            if exc_code == "rate_limit_exceeded":
                raise RateLimitError(
                    (
                        f"OpenAI API rate limit error "
                        f"({exc_code=}, {exc_type=} {exc_param=}): {exc}"
                    ),
                    wait_time=self._get_retry_after(exc),
                ) from exc
            raise ScinoephileError(
                f"OpenAI API error ({exc_code=}, {exc_type=} {exc_param=}): {exc}"
            ) from exc

    def _get_retry_after(self, exc: OpenAIError) -> float | None:
        """Return the retry-after time from an OpenAI error if available.

        Arguments:
            exc: OpenAI error returned by the client.
        Returns:
            Number of seconds to wait before retrying, if provided by the response.
        """
        response = getattr(exc, "response", None)
        headers = getattr(response, "headers", None) if response else None
        if headers:
            retry_after = headers.get("Retry-After") or headers.get("retry-after")
            if retry_after is not None:
                try:
                    return float(retry_after)
                except (TypeError, ValueError):
                    return None
        return None
