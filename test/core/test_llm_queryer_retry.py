#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for retry behaviour of LLMQueryer."""

from __future__ import annotations

import json
from typing import Any

import pytest

from scinoephile.core.abcs import Answer, LLMProvider, LLMQueryer, Query, TestCase


class DummyQuery(Query):
    """Simple query for testing."""

    prompt: str


class DummyAnswer(Answer):
    """Simple answer for testing."""

    text: str


class DummyTestCase(DummyQuery, DummyAnswer, TestCase[DummyQuery, DummyAnswer]):
    """Simple test case."""


class FailingProvider(LLMProvider):
    """Provider that fails a configurable number of times."""

    def __init__(self, failures: int, response: str) -> None:
        """Initialize the provider."""
        self.failures = failures
        self.calls = 0
        self.response = response

    def chat_completion(
        self,
        model: str,
        messages: list[dict[str, Any]],
        temperature: float = 0.0,
        seed: int = 0,
        response_format: type[Answer] | None = None,
    ) -> str:
        """Return completion text or raise an error."""
        self.calls += 1
        if self.calls <= self.failures:
            raise RuntimeError("failure")
        return self.response


class DummyQueryer(LLMQueryer[DummyQuery, DummyAnswer, DummyTestCase]):
    """Queryer used for testing retries."""

    @property
    def answer_cls(self) -> type[DummyAnswer]:
        """Answer class."""
        return DummyAnswer

    @property
    def answer_example(self) -> DummyAnswer:
        """Example answer."""
        return DummyAnswer(text="example")

    @property
    def answer_template(self) -> str:
        """Answer template."""
        return json.dumps({"text": "{text}"}) + "\n"

    @property
    def base_system_prompt(self) -> str:
        """Base system prompt."""
        return "Provide a JSON response"

    @property
    def query_cls(self) -> type[DummyQuery]:
        """Query class."""
        return DummyQuery

    @property
    def query_template(self) -> str:
        """Query template."""
        return "{prompt}\n"

    @property
    def test_case_cls(self) -> type[DummyTestCase]:
        """Test case class."""
        return DummyTestCase


def test_retry_success() -> None:
    """Provider succeeds after a few failures."""
    response = json.dumps({"text": "ok"})
    provider = FailingProvider(failures=2, response=response)
    queryer = DummyQueryer(provider=provider, max_attempts=3)
    answer = queryer(DummyQuery(prompt="hi"))
    assert answer.text == "ok"
    assert provider.calls == 3


def test_retry_failure() -> None:
    """Provider keeps failing until attempts exhausted."""
    provider = FailingProvider(failures=5, response="{}")
    queryer = DummyQueryer(provider=provider, max_attempts=3)
    with pytest.raises(RuntimeError):
        queryer(DummyQuery(prompt="hi"))
    assert provider.calls == 3
