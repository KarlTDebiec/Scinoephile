#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for asynchronous LLMQueryer."""

from __future__ import annotations

import asyncio
import json
from functools import cached_property
from typing import Any

from scinoephile.core.abcs import Answer, FixedLLMQueryer, LLMProvider, Query, TestCase


class _StubProvider(LLMProvider):
    """Stub provider returning a canned response."""

    def __init__(self, response: dict[str, str]):
        """Initialize.

        Arguments:
            response: Response to return for any query
        """
        self._response = json.dumps(response)

    def chat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.0,
        seed: int = 0,
        response_format: type[Answer] | None = None,
    ) -> str:
        """Return canned response."""
        return self._response

    async def achat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.0,
        seed: int = 0,
        response_format: type[Answer] | None = None,
    ) -> str:
        """Return canned response asynchronously."""
        await asyncio.sleep(0)
        return self._response


class _EchoQuery(Query):
    """Simple echo query."""

    text: str


class _EchoAnswer(Answer):
    """Simple echo answer."""

    reply: str


class _EchoTestCase(TestCase[_EchoQuery, _EchoAnswer], _EchoQuery, _EchoAnswer):
    """Test case combining query and answer."""


class _EchoQueryer(FixedLLMQueryer[_EchoQuery, _EchoAnswer, _EchoTestCase]):
    """Queryer for echo tests."""

    @cached_property
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return "Echo the provided text."


def test_acall_returns_answer() -> None:
    """Ensure asynchronous call returns expected answer."""

    async def _run() -> None:
        provider = _StubProvider({"reply": "pong"})
        queryer = _EchoQueryer(provider=provider)
        answer = await queryer.acall(_EchoQuery(text="ping"))
        assert answer.reply == "pong"

    asyncio.run(_run())
