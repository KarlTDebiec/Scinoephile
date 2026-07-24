#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for provider injection into Queryer and Processor."""

from __future__ import annotations

import gc
import json
from functools import cache
from typing import Any, Unpack
from unittest.mock import Mock
from weakref import ref

from pydantic import JsonValue, ValidationError
from pytest import raises

from scinoephile.core import Language, ScinoephileError
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

    def __init__(
        self,
        response: str = '{"output":"done"}',
        *,
        model: str = "test-model",
        base_url: str | None = None,
    ):
        """Initialize.

        Arguments:
            response: completion response to return
            model: model identity for cache namespacing
            base_url: base URL identity for cache namespacing
        """
        self.calls: list[list[dict[str, Any]]] = []
        self.response_formats: list[type[Answer]] = []
        self.response = response
        self.model = model
        self.base_url = base_url

    @property
    def cache_identity(self) -> dict[str, JsonValue]:
        """Stable provider configuration for cache namespacing."""
        return {
            **super().cache_identity,
            "model": self.model,
            "base_url": self.base_url,
        }

    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer],
        tool_box: ToolBox | None = None,
        **kwargs: Unpack[ChatCompletionKwargs],
    ) -> str:
        """Record messages and return a fixed completion response."""
        _ = (tool_box, kwargs)
        self.calls.append(messages)
        self.response_formats.append(response_format)
        return self.response


class _AlternateRecordingProvider(_RecordingProvider):
    """Alternate provider implementation for cache identity tests."""


def test_queryer_uses_injected_provider():
    """Test queryer uses the injected provider for completions."""
    provider = _RecordingProvider()
    queryer = Queryer(_TestCase, provider=provider, max_attempts=1)

    test_case = _TestCase(query=_Query(text="input"))
    output_test_case = queryer(test_case)

    assert output_test_case.answer is not None
    assert output_test_case.answer.output == "done"
    assert len(provider.calls) == 1
    assert provider.response_formats == [_Answer]
    assert queryer.system_prompt == _PROMPT.base_system_prompt


def test_queryer_retries_provider_errors():
    """Test transient provider errors use the configured attempt count."""
    provider = Mock(spec=LLMProvider)
    provider.chat_completion.side_effect = [
        ScinoephileError("invalid structured content"),
        '{"output":"done"}',
    ]
    queryer = Queryer(_TestCase, provider=provider, max_attempts=2)

    result = queryer(_TestCase(query=_Query(text="input")))

    assert result.answer == _Answer(output="done")
    assert provider.chat_completion.call_count == 2


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
    assert system_message == queryer.system_prompt
    assert "Additional context:" not in system_message
    assert "\n\nUse canonical names." in system_message
    assert system_message.index("Use canonical names.") < system_message.index(
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


def test_queryer_cache_is_namespaced_by_provider_model(tmp_path):
    """Test one provider model cannot load another model's cached answer."""
    provider_one = _RecordingProvider('{"output":"one"}', model="model-one")
    queryer_one = Queryer(
        _TestCase,
        provider=provider_one,
        cache_dir_path=tmp_path,
        max_attempts=1,
    )
    test_case = _TestCase(query=_Query(text="input"))

    result_one = queryer_one(test_case)

    provider_two = _RecordingProvider('{"output":"two"}', model="model-two")
    queryer_two = Queryer(
        _TestCase,
        provider=provider_two,
        cache_dir_path=tmp_path,
        max_attempts=1,
    )
    result_two = queryer_two(test_case)

    assert result_one.answer == _Answer(output="one")
    assert result_two.answer == _Answer(output="two")
    assert len(provider_one.calls) == 1
    assert len(provider_two.calls) == 1


def test_queryer_cache_stores_only_answer_and_preserves_current_metadata(tmp_path):
    """Test cached answers are attached to the current normalized test case."""
    provider = _RecordingProvider('{"output":"cached"}')
    queryer = Queryer(
        _TestCase,
        provider=provider,
        cache_dir_path=tmp_path,
        max_attempts=1,
    )

    first = queryer(_TestCase(query=_Query(text="input")))

    cache_paths = list(tmp_path.glob("*.json"))
    assert len(cache_paths) == 1
    assert json.loads(cache_paths[0].read_text(encoding="utf-8")) == {
        "output": "cached"
    }

    current = _TestCase(
        query=_Query(text="input"),
        answer=_Answer(output="stale"),
        difficulty=4,
        few_shot=True,
        verified=True,
    )
    second = queryer(current)

    assert first.answer == _Answer(output="cached")
    assert second.answer == _Answer(output="cached")
    assert second.difficulty == 4
    assert second.few_shot is False
    assert second.verified is False
    assert len(provider.calls) == 1


def test_queryer_overwrites_matching_cache(tmp_path):
    """Test cache overwrite queries the provider and replaces the cached answer."""
    cached_provider = _RecordingProvider('{"output":"cached"}')
    test_case = _TestCase(query=_Query(text="input"))
    Queryer(
        _TestCase,
        provider=cached_provider,
        cache_dir_path=tmp_path,
        max_attempts=1,
    )(test_case)

    fresh_provider = _RecordingProvider('{"output":"fresh"}')
    result = Queryer(
        _TestCase,
        provider=fresh_provider,
        cache_dir_path=tmp_path,
        max_attempts=1,
        overwrite_cache=True,
    )(test_case)

    cache_paths = list(tmp_path.glob("*.json"))
    assert result.answer == _Answer(output="fresh")
    assert len(fresh_provider.calls) == 1
    assert len(cache_paths) == 1
    assert json.loads(cache_paths[0].read_text(encoding="utf-8")) == {"output": "fresh"}


def test_queryer_cache_is_namespaced_by_test_case_class(tmp_path):
    """Test compatible test-case classes do not share cached answers."""
    provider_one = _RecordingProvider('{"output":"one"}')
    queryer_one = Queryer(
        _TestCase,
        provider=provider_one,
        cache_dir_path=tmp_path,
        max_attempts=1,
    )
    test_case = _TestCase(query=_Query(text="input"))

    result_one = queryer_one(test_case)

    provider_two = _RecordingProvider('{"output":"two"}')
    queryer_two = Queryer(
        _CompatibleTestCase,
        provider=provider_two,
        cache_dir_path=tmp_path,
        max_attempts=1,
    )
    result_two = queryer_two(test_case)

    assert result_one.answer == _Answer(output="one")
    assert result_two.answer == _Answer(output="two")
    assert len(provider_one.calls) == 1
    assert len(provider_two.calls) == 1


def test_queryer_cache_is_namespaced_by_provider_implementation(tmp_path):
    """Test different provider implementations have different cache paths."""
    queryer_one = Queryer(
        _TestCase,
        provider=_RecordingProvider(),
        cache_dir_path=tmp_path,
    )
    queryer_two = Queryer(
        _TestCase,
        provider=_AlternateRecordingProvider(),
        cache_dir_path=tmp_path,
    )

    cache_path_one = queryer_one._get_cache_path("system", "tools", "query")
    cache_path_two = queryer_two._get_cache_path("system", "tools", "query")

    assert cache_path_one is not None
    assert cache_path_two is not None
    assert cache_path_one != cache_path_two


def test_queryer_cache_is_namespaced_by_provider_base_url(tmp_path):
    """Test OpenAI-compatible endpoints do not share cached answers."""
    provider_one = _RecordingProvider(
        '{"output":"one"}',
        base_url="https://one.example/v1",
    )
    provider_two = _RecordingProvider(
        '{"output":"two"}',
        base_url="https://two.example/v1",
    )
    test_case = _TestCase(query=_Query(text="input"))

    result_one = Queryer(
        _TestCase,
        provider=provider_one,
        cache_dir_path=tmp_path,
        max_attempts=1,
    )(test_case)
    result_two = Queryer(
        _TestCase,
        provider=provider_two,
        cache_dir_path=tmp_path,
        max_attempts=1,
    )(test_case)

    assert result_one.answer == _Answer(output="one")
    assert result_two.answer == _Answer(output="two")
    assert len(provider_one.calls) == 1
    assert len(provider_two.calls) == 1


def test_cache_path_does_not_retain_queryer(tmp_path):
    """Test calculating a cache path does not retain the Queryer instance."""
    queryer = Queryer(
        _TestCase,
        provider=_RecordingProvider(),
        cache_dir_path=tmp_path,
    )
    queryer_ref = ref(queryer)
    assert queryer._get_cache_path("system", "tools", "query") is not None

    del queryer
    gc.collect()

    assert queryer_ref() is None


def test_processor_passes_injected_provider_to_queryer():
    """Test processor wires injected providers into its queryer."""
    provider = Mock(spec=LLMProvider)
    processor = _Processor(prompt=_PROMPT, provider=provider)

    assert processor.queryer.provider is provider
