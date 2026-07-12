#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for provider injection into Queryer and Processor."""

from __future__ import annotations

from functools import cache
from typing import Any, Unpack
from unittest.mock import Mock

from pydantic import ValidationError
from pytest import raises

from scinoephile.core import Language
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
from scinoephile.core.llms.llm_provider import ChatCompletionKwargs
from scinoephile.core.llms.tool_box import ToolBox

_PROMPT = Prompt(
    language=Language.eng,
    base_system_prompt="System prompt",
    schema_intro="Schema",
    few_shot_intro="Few shot",
    few_shot_query_intro="Query",
    few_shot_answer_intro="Answer",
    answer_invalid_pre="Invalid answer pre",
    answer_invalid_post="Invalid answer post",
    test_case_invalid_pre="Invalid test-case pre",
    test_case_invalid_post="Invalid test-case post",
)
"""Prompt fixture for provider-injection tests."""


class _Query(Query):
    """Query fixture for provider-injection tests."""

    text: str
    """Query text."""


class _Answer(Answer):
    """Answer fixture for provider-injection tests."""

    output: str
    """Answer output."""


class _TestCase(TestCase):
    """Test-case fixture for provider-injection tests."""

    query: _Query
    """Query fixture."""
    answer: _Answer | None = None
    """Optional answer fixture."""


class _IncompatibleAnswer(Answer):
    """Incompatible answer fixture for test-case class tests."""

    note: str
    """Answer note."""


class _CompatibleTestCase(TestCase):
    """Alternate compatible test-case fixture for class validation tests."""

    query: _Query
    """Query fixture."""
    answer: _Answer | None = None
    """Optional answer fixture."""


class _IncompatibleTestCase(TestCase):
    """Incompatible test-case fixture for class validation tests."""

    query: _Query
    """Query fixture."""
    answer: _IncompatibleAnswer | None = None
    """Optional incompatible answer fixture."""


_Query.prompt = _PROMPT
_Answer.prompt = _PROMPT
_TestCase.query_cls = _Query
_TestCase.answer_cls = _Answer
_TestCase.prompt = _PROMPT
_CompatibleTestCase.query_cls = _Query
_CompatibleTestCase.answer_cls = _Answer
_CompatibleTestCase.prompt = _PROMPT
_IncompatibleAnswer.prompt = _PROMPT
_IncompatibleTestCase.query_cls = _Query
_IncompatibleTestCase.answer_cls = _IncompatibleAnswer
_IncompatibleTestCase.prompt = _PROMPT


class _Manager(Manager):
    """Manager fixture for provider-injection tests."""

    operation = "test"
    """Stable operation identifier."""
    base_prompt = _PROMPT
    """Base prompt."""
    test_case_base_cls = _TestCase
    """Static test-case model."""

    @classmethod
    @cache
    def get_query_cls(cls, prompt: Prompt) -> type[Query]:
        """Get test query class."""
        return _Query

    @classmethod
    @cache
    def get_answer_cls(cls, prompt: Prompt) -> type[Answer]:
        """Get test answer class."""
        return _Answer


class _Processor(Processor):
    """Processor fixture for provider-injection tests."""

    manager_cls = _Manager
    """Manager fixture class."""


class _RecordingProvider(LLMProvider):
    """Recording provider fixture."""

    def __init__(self, response: str = '{"output":"done"}'):
        """Initialize.

        Arguments:
            response: completion response to return
        """
        self.calls: list[list[dict[str, Any]]] = []
        self.response = response

    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer] | None = None,
        tool_box: ToolBox | None = None,
        **kwargs: Unpack[ChatCompletionKwargs],
    ) -> str:
        """Record messages and return a fixed completion response."""
        _ = (response_format, tool_box, kwargs)
        self.calls.append(messages)
        return self.response


def test_queryer_uses_injected_provider():
    """Test queryer uses the injected provider for completions."""
    provider = _RecordingProvider()
    queryer = Queryer(_TestCase, provider=provider, max_attempts=1)

    test_case = _TestCase(query=_Query(text="input"))
    output_test_case = queryer(test_case)

    assert output_test_case.answer is not None
    assert output_test_case.answer.output == "done"
    assert len(provider.calls) == 1


def test_queryer_requires_injected_provider():
    """Test queryer no longer constructs concrete providers by default."""
    queryer_type: Any = Queryer
    with raises(TypeError):
        queryer_type(_TestCase)


def test_queryer_includes_additional_context_before_few_shot_prompt():
    """Test queryer includes additional context before few-shot examples."""
    provider = _RecordingProvider()
    few_shot_test_case = _TestCase(
        query=_Query(text="example"),
        answer=_Answer(output="example output"),
        few_shot=True,
        verified=True,
    )
    queryer = Queryer(
        _TestCase,
        additional_context="Use canonical names.",
        verified_test_cases=[few_shot_test_case],
        provider=provider,
        max_attempts=1,
    )

    test_case = _TestCase(query=_Query(text="input"))
    queryer(test_case)

    messages = provider.calls[0]
    system_message = messages[0]["content"]
    assert "Additional context:\nUse canonical names." in system_message
    assert system_message.index("Additional context:") < system_message.index(
        _PROMPT.few_shot_intro
    )


def test_queryer_preserves_existing_encountered_test_case_metadata():
    """Test queryer preserves existing few-shot and verified metadata."""
    provider = Mock(spec=LLMProvider)
    queryer = Queryer(_TestCase, provider=provider)
    test_case = _TestCase(
        query=_Query(text="input"),
        answer=_Answer(output="done"),
        few_shot=True,
        verified=True,
    )

    queryer.log_encountered_test_case(test_case)

    encountered_test_case = queryer.encountered_test_cases[test_case.query.key]
    assert encountered_test_case.few_shot is True
    assert encountered_test_case.verified is True


def test_queryer_clears_stale_verified_metadata_after_generating_answer():
    """Test queryer clears stale verified metadata after generating an answer."""
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = '{"output":"new"}'
    queryer = Queryer(_TestCase, provider=provider, max_attempts=1)
    test_case = _TestCase(
        query=_Query(text="input"),
        answer=_Answer(output="old"),
        few_shot=True,
        verified=True,
    )

    output_test_case = queryer(test_case)

    assert output_test_case.answer is not None
    assert output_test_case.answer.output == "new"
    assert output_test_case.few_shot is False
    assert output_test_case.verified is False


def test_queryer_preserves_auto_verified_encountered_test_case(monkeypatch):
    """Test queryer preserves auto-verified encountered test cases."""
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.return_value = '{"output":"done"}'
    monkeypatch.setattr(_TestCase, "get_auto_verified", lambda self: True)
    queryer = Queryer(_TestCase, provider=provider, max_attempts=1, auto_verify=True)

    test_case = queryer(_TestCase(query=_Query(text="input")))

    encountered_test_case = queryer.encountered_test_cases[test_case.query.key]
    assert encountered_test_case.verified is True


def test_queryer_rejects_verified_test_case_from_incompatible_class():
    """Test verified answers must conform to the configured test-case class."""
    provider = Mock(spec=LLMProvider)
    incompatible = _IncompatibleTestCase(
        query=_Query(text="input"),
        answer=_IncompatibleAnswer(note="reviewed"),
        verified=True,
    )

    with raises(ValidationError):
        Queryer(_TestCase, verified_test_cases=[incompatible], provider=provider)


def test_queryer_normalizes_input_into_configured_test_case_class():
    """Test compatible inputs are returned using the configured test-case class."""
    provider = Mock(spec=LLMProvider)
    verified = _TestCase(
        query=_Query(text="input"),
        answer=_Answer(output="done"),
        verified=True,
    )
    queryer = Queryer(_TestCase, verified_test_cases=[verified], provider=provider)

    result = queryer(_CompatibleTestCase(query=_Query(text="input")))

    assert type(result) is _TestCase
    assert result.answer == _Answer(output="done")
    provider.chat_completion.assert_not_called()


def test_queryer_requires_answers_for_verified_test_cases():
    """Test verified inputs cannot omit their answers."""
    provider = Mock(spec=LLMProvider)
    incomplete = _TestCase.model_construct(
        query=_Query(text="input"),
        answer=None,
        verified=True,
    )

    with raises(ValidationError):
        Queryer(_TestCase, verified_test_cases=[incomplete], provider=provider)


def test_queryer_requires_test_cases_to_be_verified():
    """Test Queryer rejects unverified test cases."""
    provider = Mock(spec=LLMProvider)
    unverified = _TestCase(
        query=_Query(text="input"),
        answer=_Answer(output="done"),
    )

    with raises(ValueError, match="must be verified"):
        Queryer(_TestCase, verified_test_cases=[unverified], provider=provider)


def test_test_case_requires_answer_when_verified():
    """Test verified metadata requires an answer during model validation."""
    with raises(ValidationError, match="must include an answer"):
        _TestCase(query=_Query(text="input"), verified=True)


def test_test_case_requires_few_shot_to_be_verified():
    """Test few-shot metadata requires verified metadata."""
    with raises(ValidationError, match="must be verified"):
        _TestCase(
            query=_Query(text="input"),
            answer=_Answer(output="done"),
            few_shot=True,
        )


def test_queryer_merges_identical_verified_duplicates():
    """Test identical duplicate answers merge their metadata."""
    provider = Mock(spec=LLMProvider)
    few_shot = _TestCase(
        query=_Query(text="input"),
        answer=_Answer(output="done"),
        difficulty=1,
        few_shot=True,
        verified=True,
    )
    verified = _TestCase(
        query=_Query(text="input"),
        answer=_Answer(output="done"),
        difficulty=3,
        verified=True,
    )

    queryer = Queryer(
        _TestCase,
        verified_test_cases=[few_shot, verified],
        provider=provider,
    )

    merged = queryer.verified_test_cases[verified.query.key]
    assert merged is queryer.few_shot_test_cases[few_shot.query.key]
    assert merged.difficulty == 3
    assert merged.few_shot is True
    assert merged.verified is True


def test_queryer_rejects_conflicting_verified_duplicates():
    """Test duplicate queries cannot silently choose one of two answers."""
    provider = Mock(spec=LLMProvider)
    first = _TestCase(
        query=_Query(text="input"),
        answer=_Answer(output="first"),
        verified=True,
    )
    second = _TestCase(
        query=_Query(text="input"),
        answer=_Answer(output="second"),
        verified=True,
    )

    with raises(ValueError, match="Conflicting verified answers"):
        Queryer(
            _TestCase,
            verified_test_cases=[first, second],
            provider=provider,
        )


def test_queryer_snapshots_verified_test_cases():
    """Test later mutation of caller-owned cases does not alter queryer state."""
    provider = Mock(spec=LLMProvider)
    verified = _TestCase(
        query=_Query(text="input"),
        answer=_Answer(output="original"),
        verified=True,
    )
    queryer = Queryer(_TestCase, verified_test_cases=[verified], provider=provider)

    assert verified.answer is not None
    verified.answer.output = "mutated"

    stored = queryer.verified_test_cases[verified.query.key]
    assert stored.answer is not None
    assert stored.answer.output == "original"


def test_processor_passes_injected_provider_to_queryer():
    """Test processor wires injected providers into its queryer."""
    provider = Mock(spec=LLMProvider)
    processor = _Processor(prompt=_PROMPT, provider=provider)

    assert processor.queryer.provider is provider
