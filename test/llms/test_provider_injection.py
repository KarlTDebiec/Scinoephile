#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for provider injection into Queryer and Processor."""

from __future__ import annotations

from functools import cache
from unittest.mock import Mock

import pytest

from scinoephile.core.llms import (
    Answer,
    LLMProvider,
    Manager,
    Processor,
    Prompt,
    Query,
    Queryer,
    TestCase,
)


class _Prompt(Prompt):
    """Prompt fixture for provider-injection tests."""

    base_system_prompt = "System prompt"
    schema_intro = "Schema"
    few_shot_intro = "Few shot"
    few_shot_query_intro = "Query"
    few_shot_answer_intro = "Answer"
    answer_invalid_pre = "Invalid answer pre"
    answer_invalid_post = "Invalid answer post"
    test_case_invalid_pre = "Invalid test-case pre"
    test_case_invalid_post = "Invalid test-case post"


class _Query(Query):
    """Query fixture for provider-injection tests."""

    text: str


class _Answer(Answer):
    """Answer fixture for provider-injection tests."""

    output: str


class _TestCase(TestCase):
    """Test-case fixture for provider-injection tests."""

    query: _Query
    answer: _Answer | None = None


_Query.prompt_cls = _Prompt
_Answer.prompt_cls = _Prompt
_TestCase.query_cls = _Query
_TestCase.answer_cls = _Answer
_TestCase.prompt_cls = _Prompt


class _Manager(Manager):
    """Manager fixture for provider-injection tests."""

    @classmethod
    @cache
    def get_query_cls(cls, prompt_cls: type[Prompt]) -> type[Query]:
        """Get test query class."""
        return _Query

    @classmethod
    @cache
    def get_answer_cls(cls, prompt_cls: type[Prompt]) -> type[Answer]:
        """Get test answer class."""
        return _Answer


class _Processor(Processor):
    """Processor fixture for provider-injection tests."""

    manager_cls = _Manager


def test_queryer_uses_injected_provider():
    """Test queryer uses the injected provider for completions."""
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = '{"output":"done"}'
    queryer_cls = Queryer.get_queryer_cls(_Prompt)
    queryer = queryer_cls(provider=provider, max_attempts=1)

    test_case = _TestCase(query=_Query(text="input"))
    output_test_case = queryer(test_case)

    assert output_test_case.answer is not None
    assert output_test_case.answer.output == "done"
    provider.chat_completion.assert_called_once()


def test_queryer_requires_injected_provider():
    """Test queryer no longer constructs concrete providers by default."""
    queryer_cls = Queryer.get_queryer_cls(_Prompt)

    with pytest.raises(TypeError):
        queryer_cls()


def test_processor_passes_injected_provider_to_queryer():
    """Test processor wires injected providers into its queryer."""
    provider = Mock(spec=LLMProvider)
    processor = _Processor(prompt_cls=_Prompt, provider=provider)

    assert processor.queryer.provider is provider
