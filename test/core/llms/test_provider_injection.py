#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for provider injection into Queryer and Processor."""

from __future__ import annotations

import gc
import json
from functools import cache
from pathlib import Path
from typing import Any, Unpack
from unittest.mock import Mock
from weakref import ref

from pydantic import JsonValue, ValidationError
from pytest import raises

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import (
    Answer,
    ChatCompletionMetrics,
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
from scinoephile.core.llms.utils import (
    load_test_cases_from_json,
    save_test_cases_to_json,
)

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

    def get_no_op_answer(self) -> _Answer:
        """Get an answer that echoes the query text."""
        return _Answer(output=self.query.text)


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
_TestCase.operation = "test"
_TestCase.prompt = _PROMPT
_CompatibleTestCase.query_cls = _Query
_CompatibleTestCase.answer_cls = _Answer
_CompatibleTestCase.operation = "test"
_CompatibleTestCase.prompt = _PROMPT
_IncompatibleAnswer.prompt = _PROMPT
_IncompatibleTestCase.query_cls = _Query
_IncompatibleTestCase.answer_cls = _IncompatibleAnswer
_IncompatibleTestCase.operation = "test"
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
        self.completion_metrics: list[ChatCompletionMetrics] = []
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
        *,
        operation: str | None = None,
        query_key_sha256: str | None = None,
        query_attempt: int = 1,
        **kwargs: Unpack[ChatCompletionKwargs],
    ) -> str:
        """Record messages and return a fixed completion response."""
        _ = (tool_box, kwargs)
        self.calls.append(messages)
        self.response_formats.append(response_format)
        self.completion_metrics.append(
            ChatCompletionMetrics(
                operation=operation,
                query_key_sha256=query_key_sha256,
                model=self.model,
                query_attempt=query_attempt,
                tool_round=1,
                input_tokens=10,
                cached_input_tokens=0,
                cache_write_tokens=0,
                output_tokens=2,
                reasoning_tokens=0,
                total_tokens=12,
                transport_retries=0,
                latency_seconds=0.1,
                prompt_cache_key=None,
            )
        )
        return self.response


class _AlternateRecordingProvider(_RecordingProvider):
    """Alternate provider implementation for cache identity tests."""


class _SequenceRecordingProvider(_RecordingProvider):
    """Recording provider returning a sequence of responses."""

    def __init__(self, responses: list[str]):
        """Initialize.

        Arguments:
            responses: completion responses to return in order
        """
        if not responses:
            raise ValueError("responses must not be empty.")
        super().__init__(responses[0])
        self.responses = responses.copy()

    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer],
        tool_box: ToolBox | None = None,
        *,
        operation: str | None = None,
        query_key_sha256: str | None = None,
        query_attempt: int = 1,
        **kwargs: Unpack[ChatCompletionKwargs],
    ) -> str:
        """Record messages and return the next completion response."""
        self.response = self.responses.pop(0)
        return super().chat_completion(
            messages,
            response_format,
            tool_box,
            operation=operation,
            query_key_sha256=query_key_sha256,
            query_attempt=query_attempt,
            **kwargs,
        )


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
    [completion_metrics] = provider.completion_metrics
    assert completion_metrics.operation == "test"
    assert completion_metrics.query_key_sha256 is not None
    assert len(completion_metrics.query_key_sha256) == 64
    assert completion_metrics.query_attempt == 1
    assert queryer.completion_metrics == provider.completion_metrics
    assert queryer.system_prompt == _PROMPT.base_system_prompt


def test_queryer_no_op_bypasses_provider_and_response_cache(tmp_path: Path):
    """No-op queries should use neutral answers without creating a cache.

    Arguments:
        tmp_path: temporary directory path
    """
    provider = _RecordingProvider(response='{"output":"provider"}')
    cache_root_path = tmp_path / "cache"
    queryer = Queryer(
        _TestCase, provider=provider, cache_root_path=cache_root_path, no_op=True
    )

    result = queryer(_TestCase(query=_Query(text="input")))

    assert result.answer == _Answer(output="input")
    assert result.verified is False
    assert not provider.calls
    assert not cache_root_path.exists()


def test_queryer_no_op_ignores_existing_response_cache(tmp_path: Path):
    """No-op queries should not reuse an existing unverified cached answer.

    Arguments:
        tmp_path: temporary directory path
    """
    query = _Query(text="input")
    cached_provider = _RecordingProvider(response='{"output":"cached"}')
    Queryer(
        _TestCase, provider=cached_provider, cache_root_path=tmp_path, max_attempts=1
    )(_TestCase(query=query))
    no_op_provider = _RecordingProvider(response='{"output":"provider"}')
    queryer = Queryer(
        _TestCase, provider=no_op_provider, cache_root_path=tmp_path, no_op=True
    )

    result = queryer(_TestCase(query=query))

    assert result.answer == _Answer(output="input")
    assert not no_op_provider.calls


def test_queryer_no_op_prefers_verified_answer(tmp_path: Path):
    """No-op queries should retain trusted verified answers.

    Arguments:
        tmp_path: temporary directory path
    """
    provider = _RecordingProvider(response='{"output":"provider"}')
    verified = _TestCase(
        query=_Query(text="input"), answer=_Answer(output="verified"), verified=True
    )
    cache_root_path = tmp_path / "cache"
    queryer = Queryer(
        _TestCase,
        verified_test_cases=[verified],
        provider=provider,
        cache_root_path=cache_root_path,
        no_op=True,
    )

    result = queryer(_TestCase(query=_Query(text="input")))

    assert result.answer == _Answer(output="verified")
    assert result.verified is True
    assert not provider.calls
    assert not cache_root_path.exists()


def test_queryer_retries_provider_errors():
    """Test transient provider errors use the configured attempt count."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.side_effect = [
        ScinoephileError("invalid structured content"),
        '{"output":"done"}',
    ]
    queryer = Queryer(_TestCase, provider=provider, max_attempts=2)

    result = queryer(_TestCase(query=_Query(text="input")))

    assert result.answer == _Answer(output="done")
    assert provider.chat_completion.call_count == 2
    assert [
        call.kwargs["query_attempt"] for call in provider.chat_completion.call_args_list
    ] == [1, 2]


def test_queryer_attributes_validation_retries_to_one_query(tmp_path: Path):
    """Test validation retries retain their query identity and attempt number.

    Arguments:
        tmp_path: temporary directory path
    """
    provider = _SequenceRecordingProvider(["{}", '{"output":"done"}'])
    queryer = Queryer(
        _TestCase, provider=provider, cache_root_path=tmp_path, max_attempts=2
    )

    result = queryer(_TestCase(query=_Query(text="input")))

    assert result.answer == _Answer(output="done")
    assert [metrics.query_attempt for metrics in queryer.completion_metrics] == [1, 2]
    assert (
        len({metrics.query_key_sha256 for metrics in queryer.completion_metrics}) == 1
    )


def test_queryers_sharing_provider_retain_only_their_metrics(tmp_path: Path):
    """Test shared provider history is partitioned by completion call metadata.

    Arguments:
        tmp_path: temporary directory path
    """
    provider = _RecordingProvider()
    first_queryer = Queryer(
        _TestCase, provider=provider, cache_root_path=tmp_path, max_attempts=1
    )
    second_queryer = Queryer(
        _TestCase, provider=provider, cache_root_path=tmp_path, max_attempts=1
    )

    first_queryer(_TestCase(query=_Query(text="first")))
    second_queryer(_TestCase(query=_Query(text="second")))

    assert len(provider.completion_metrics) == 2
    assert first_queryer.completion_metrics == [provider.completion_metrics[0]]
    assert second_queryer.completion_metrics == [provider.completion_metrics[1]]
    assert (
        first_queryer.completion_metrics[0].query_key_sha256
        != second_queryer.completion_metrics[0].query_key_sha256
    )


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
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
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
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
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
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    provider.chat_completion.return_value = '{"output":"done"}'
    monkeypatch.setattr(_TestCase, "get_auto_verified", lambda self: True)
    queryer = Queryer(_TestCase, provider=provider, max_attempts=1, auto_verify=True)

    test_case = queryer(_TestCase(query=_Query(text="input")))

    encountered_test_case = queryer.encountered_test_cases[test_case.query.key]
    assert encountered_test_case.verified is True


def test_queryer_rejects_verified_test_case_from_incompatible_class():
    """Test verified answers must conform to the configured test-case class."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    incompatible = _IncompatibleTestCase(
        query=_Query(text="input"),
        answer=_IncompatibleAnswer(note="reviewed"),
        verified=True,
    )

    with raises(ValidationError):
        Queryer(_TestCase, verified_test_cases=[incompatible], provider=provider)


def test_queryer_normalizes_input_into_configured_test_case_class():
    """Test compatible inputs are returned using the configured test-case class."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    verified = _TestCase(
        query=_Query(text="input"), answer=_Answer(output="done"), verified=True
    )
    queryer = Queryer(_TestCase, verified_test_cases=[verified], provider=provider)

    result = queryer(_CompatibleTestCase(query=_Query(text="input")))

    assert type(result) is _TestCase
    assert result.answer == _Answer(output="done")
    provider.chat_completion.assert_not_called()


def test_queryer_requires_answers_for_verified_test_cases():
    """Test verified inputs cannot omit their answers."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    incomplete = _TestCase.model_construct(
        query=_Query(text="input"), answer=None, verified=True
    )

    with raises(ValidationError):
        Queryer(_TestCase, verified_test_cases=[incomplete], provider=provider)


def test_queryer_requires_test_cases_to_be_verified():
    """Test Queryer rejects unverified test cases."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    unverified = _TestCase(query=_Query(text="input"), answer=_Answer(output="done"))

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
            query=_Query(text="input"), answer=_Answer(output="done"), few_shot=True
        )


def test_queryer_merges_identical_verified_duplicates():
    """Test identical duplicate answers merge their metadata."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
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
        _TestCase, verified_test_cases=[few_shot, verified], provider=provider
    )

    merged = queryer.verified_test_cases[verified.query.key]
    assert merged is queryer.few_shot_test_cases[few_shot.query.key]
    assert merged.difficulty == 3
    assert merged.few_shot is True
    assert merged.verified is True


def test_queryer_rejects_conflicting_verified_duplicates():
    """Test duplicate queries cannot silently choose one of two answers."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    first = _TestCase(
        query=_Query(text="input"), answer=_Answer(output="first"), verified=True
    )
    second = _TestCase(
        query=_Query(text="input"), answer=_Answer(output="second"), verified=True
    )

    with raises(
        ValueError,
        match=(
            "(?s)Conflicting verified answers.*Existing answer.*first.*"
            "Conflicting answer.*second"
        ),
    ):
        Queryer(_TestCase, verified_test_cases=[first, second], provider=provider)


def test_queryer_snapshots_verified_test_cases():
    """Test later mutation of caller-owned cases does not alter queryer state."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    verified = _TestCase(
        query=_Query(text="input"), answer=_Answer(output="original"), verified=True
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
        _TestCase, provider=provider_one, cache_root_path=tmp_path, max_attempts=1
    )
    test_case = _TestCase(query=_Query(text="input"))

    result_one = queryer_one(test_case)

    provider_two = _RecordingProvider('{"output":"two"}', model="model-two")
    queryer_two = Queryer(
        _TestCase, provider=provider_two, cache_root_path=tmp_path, max_attempts=1
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
        _TestCase, provider=provider, cache_root_path=tmp_path, max_attempts=1
    )

    first = queryer(_TestCase(query=_Query(text="input")))

    cache_paths = list((tmp_path / "llms" / "test").glob("*.json"))
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


def test_queryer_public_cache_lifecycle_normalizes_and_reuses_answer(tmp_path: Path):
    """Test public cache lookup and storage methods share normalized state.

    Arguments:
        tmp_path: temporary directory path
    """
    provider = _RecordingProvider()
    queryer = Queryer(_TestCase, provider=provider, cache_root_path=tmp_path)
    input_test_case = _CompatibleTestCase(
        query=_Query(text="input"), answer=_Answer(output="stored")
    )

    stored = queryer.store_answered_test_case(input_test_case)

    assert type(stored) is _TestCase
    assert stored is queryer.encountered_test_cases[stored.query.key]
    assert not provider.calls

    fresh_provider = _RecordingProvider('{"output":"provider"}')
    fresh_queryer = Queryer(
        _TestCase, provider=fresh_provider, cache_root_path=tmp_path
    )
    loaded = fresh_queryer.get_known_test_case(
        _CompatibleTestCase(query=_Query(text="input"))
    )

    assert loaded is not None
    assert type(loaded) is _TestCase
    assert loaded.answer == _Answer(output="stored")
    assert loaded is fresh_queryer.encountered_test_cases[loaded.query.key]
    assert not fresh_provider.calls


def test_queryer_overwrites_matching_cache(tmp_path):
    """Test cache overwrite queries the provider and replaces the cached answer."""
    cached_provider = _RecordingProvider('{"output":"cached"}')
    test_case = _TestCase(query=_Query(text="input"))
    Queryer(
        _TestCase, provider=cached_provider, cache_root_path=tmp_path, max_attempts=1
    )(test_case)

    fresh_provider = _RecordingProvider('{"output":"fresh"}')
    result = Queryer(
        _TestCase,
        provider=fresh_provider,
        cache_root_path=tmp_path,
        max_attempts=1,
        overwrite_cache=True,
    )(test_case)

    cache_paths = list((tmp_path / "llms" / "test").glob("*.json"))
    assert result.answer == _Answer(output="fresh")
    assert len(fresh_provider.calls) == 1
    assert len(cache_paths) == 1
    assert json.loads(cache_paths[0].read_text(encoding="utf-8")) == {"output": "fresh"}


def test_queryer_cache_is_namespaced_by_test_case_class(tmp_path):
    """Test compatible test-case classes do not share cached answers."""
    provider_one = _RecordingProvider('{"output":"one"}')
    queryer_one = Queryer(
        _TestCase, provider=provider_one, cache_root_path=tmp_path, max_attempts=1
    )
    test_case = _TestCase(query=_Query(text="input"))

    result_one = queryer_one(test_case)

    provider_two = _RecordingProvider('{"output":"two"}')
    queryer_two = Queryer(
        _CompatibleTestCase,
        provider=provider_two,
        cache_root_path=tmp_path,
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
        _TestCase, provider=_RecordingProvider(), cache_root_path=tmp_path
    )
    queryer_two = Queryer(
        _TestCase, provider=_AlternateRecordingProvider(), cache_root_path=tmp_path
    )

    assert queryer_one._cache is not None
    assert queryer_two._cache is not None
    cache_path_one = queryer_one._cache.get_path(
        queryer_one._get_cache_identity(), "system", "[]", '{"query":"value"}'
    )
    cache_path_two = queryer_two._cache.get_path(
        queryer_two._get_cache_identity(), "system", "[]", '{"query":"value"}'
    )

    assert cache_path_one is not None
    assert cache_path_two is not None
    assert cache_path_one != cache_path_two


def test_queryer_cache_is_namespaced_by_provider_base_url(tmp_path):
    """Test OpenAI-compatible endpoints do not share cached answers."""
    provider_one = _RecordingProvider(
        '{"output":"one"}', base_url="https://one.example/v1"
    )
    provider_two = _RecordingProvider(
        '{"output":"two"}', base_url="https://two.example/v1"
    )
    test_case = _TestCase(query=_Query(text="input"))

    result_one = Queryer(
        _TestCase, provider=provider_one, cache_root_path=tmp_path, max_attempts=1
    )(test_case)
    result_two = Queryer(
        _TestCase, provider=provider_two, cache_root_path=tmp_path, max_attempts=1
    )(test_case)

    assert result_one.answer == _Answer(output="one")
    assert result_two.answer == _Answer(output="two")
    assert len(provider_one.calls) == 1
    assert len(provider_two.calls) == 1


def test_cache_path_does_not_retain_queryer(tmp_path):
    """Test calculating a cache path does not retain the Queryer instance."""
    queryer = Queryer(
        _TestCase, provider=_RecordingProvider(), cache_root_path=tmp_path
    )
    queryer_ref = ref(queryer)
    assert queryer._cache is not None
    assert (
        queryer._cache.get_path(
            queryer._get_cache_identity(), "system", "[]", '{"query":"value"}'
        )
        is not None
    )

    del queryer
    gc.collect()

    assert queryer_ref() is None


def test_processor_preserves_shared_verified_cases_from_current_unverified_case(
    tmp_path: Path,
):
    """All shared verified cases should reach the nascent Queryer."""
    shared_verified = _TestCase(
        query=_Query(text="input"), answer=_Answer(output="verified"), verified=True
    )
    current_unverified = _TestCase(
        query=_Query(text="input"), answer=_Answer(output="unverified")
    )
    current_test_cases_path = tmp_path / "test_cases.json"
    save_test_cases_to_json(current_test_cases_path, [current_unverified], _Manager)

    processor = _Processor(
        prompt=_PROMPT,
        shared_test_cases=[shared_verified],
        current_test_cases_path=current_test_cases_path,
        provider=Mock(
            spec=LLMProvider,
            cache_identity={"implementation": "test"},
            completion_metrics=[],
        ),
    )

    loaded = processor.queryer.verified_test_cases[shared_verified.query.key]
    assert loaded.answer == shared_verified.answer


def test_processor_rejects_conflicting_shared_and_current_verified_cases(
    tmp_path: Path,
):
    """Conflicting shared and current verified answers should abort construction."""
    shared = _TestCase(
        query=_Query(text="input"), answer=_Answer(output="shared"), verified=True
    )
    current = _TestCase(
        query=_Query(text="input"), answer=_Answer(output="current"), verified=True
    )
    current_test_cases_path = tmp_path / "test_cases.json"
    save_test_cases_to_json(current_test_cases_path, [current], _Manager)

    with raises(ValueError, match="(?s)Existing answer.*shared.*Conflicting.*current"):
        _Processor(
            prompt=_PROMPT,
            shared_test_cases=[shared],
            current_test_cases_path=current_test_cases_path,
            provider=Mock(
                spec=LLMProvider,
                cache_identity={"implementation": "test"},
                completion_metrics=[],
            ),
        )


def test_processor_saves_encountered_cases_to_current_json(tmp_path: Path):
    """Encountered cases should be saved to the current configuration's JSON."""
    shared = _TestCase(
        query=_Query(text="input"), answer=_Answer(output="verified"), verified=True
    )
    current_test_cases_path = tmp_path / "test_cases.json"
    processor = _Processor(
        prompt=_PROMPT,
        shared_test_cases=[shared],
        current_test_cases_path=current_test_cases_path,
        provider=Mock(
            spec=LLMProvider,
            cache_identity={"implementation": "test"},
            completion_metrics=[],
        ),
    )

    processor.queryer(_TestCase(query=_Query(text="input")))
    processor.save_encountered_test_cases()

    saved = load_test_cases_from_json(current_test_cases_path, _Manager, _PROMPT)
    assert len(saved) == 1
    assert saved[0].model_dump(mode="json") == shared.model_dump(mode="json")


def test_processor_merges_test_cases_saved_by_another_instance(tmp_path: Path):
    """Processor saves should merge cases saved by another instance."""
    existing = _TestCase(query=_Query(text="existing"), answer=_Answer(output="old"))
    untouched = _TestCase(
        query=_Query(text="untouched"), answer=_Answer(output="retained")
    )
    current_test_cases_path = tmp_path / "test_cases.json"
    save_test_cases_to_json(current_test_cases_path, [existing, untouched], _Manager)
    processors = [
        _Processor(
            prompt=_PROMPT,
            current_test_cases_path=current_test_cases_path,
            provider=Mock(
                spec=LLMProvider,
                cache_identity={"implementation": "test"},
                completion_metrics=[],
            ),
        )
        for _ in range(2)
    ]
    updated = _TestCase(query=_Query(text="existing"), answer=_Answer(output="new"))
    added = _TestCase(query=_Query(text="added"), answer=_Answer(output="new case"))

    processors[0].queryer.log_encountered_test_case(updated)
    processors[0].save_encountered_test_cases()
    processors[1].queryer.log_encountered_test_case(added)
    processors[1].save_encountered_test_cases()

    saved = load_test_cases_from_json(current_test_cases_path, _Manager, _PROMPT)
    assert [(test_case.query.text, test_case.answer.output) for test_case in saved] == [
        ("existing", "new"),
        ("untouched", "retained"),
        ("added", "new case"),
    ]


def test_processor_passes_injected_provider_to_queryer():
    """Test processor wires injected providers into its queryer."""
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    processor = _Processor(prompt=_PROMPT, provider=provider)

    assert processor.queryer.provider is provider
