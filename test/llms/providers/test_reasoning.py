#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Offline reasoning request, provider mapping, and cache isolation tests."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock

from openai import OpenAI
from pytest import LogCaptureFixture, mark, raises

from scinoephile.core.llms import Answer, LlmCache, OpenAIProviderBase, ReasoningEffort
from scinoephile.llms.providers.deepseek_provider import DeepSeekProvider
from scinoephile.llms.providers.openai_provider import OpenAIProvider


class _Answer(Answer):
    """Structured completion fixture."""

    output: str
    """Completion output."""


class _UnsupportedProvider(OpenAIProviderBase):
    """OpenAI-compatible provider without reasoning support."""

    model = "unsupported"
    """Fixture model name."""


def _make_client() -> tuple[OpenAI, Mock]:
    """Create an offline SDK-shaped client recording actual completion arguments.

    Returns:
        fake client and its request mock
    """
    request = Mock(
        return_value=SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content='{"output":"ok"}', tool_calls=[])
                )
            ],
            usage=None,
        )
    )
    client = SimpleNamespace(
        beta=SimpleNamespace(
            chat=SimpleNamespace(completions=SimpleNamespace(parse=request))
        )
    )
    return cast(OpenAI, client), request


@mark.parametrize("effort", list(ReasoningEffort))
def test_openai_sends_requested_reasoning(effort: ReasoningEffort):
    """Send each explicit effort to the SDK's structured completion endpoint.

    Arguments:
        effort: requested effort level
    """
    client, request = _make_client()
    provider = OpenAIProvider(
        client=client, model="gpt-6-luna", reasoning_effort=effort
    )
    assert (
        provider.chat_completion([{"role": "user", "content": "input"}], _Answer)
        == '{"output":"ok"}'
    )
    assert request.call_args.kwargs["reasoning_effort"] == effort.value
    assert provider.cache_identity["reasoning"] == {"reasoning_effort": effort.value}


@mark.parametrize("provider_cls", [OpenAIProvider, DeepSeekProvider])
def test_omitted_effort_preserves_requests_and_cache(
    provider_cls: type[OpenAIProviderBase],
):
    """Keep existing API defaults and cache identity when reasoning is omitted.

    Arguments:
        provider_cls: concrete provider class
    """
    client, request = _make_client()
    provider = provider_cls(client=client)
    provider.chat_completion([{"role": "user", "content": "input"}], _Answer)
    assert "reasoning_effort" not in request.call_args.kwargs
    assert "extra_body" not in request.call_args.kwargs
    assert "reasoning" not in provider.cache_identity


@mark.parametrize(
    ("requested", "effective"),
    [
        ("none", None),
        ("minimal", "low"),
        ("low", "low"),
        ("medium", "high"),
        ("high", "high"),
        ("xhigh", "high"),
        ("max", "max"),
    ],
)
def test_deepseek_sends_effective_reasoning(
    requested: str, effective: str | None, caplog: LogCaptureFixture
):
    """Translate effort and thinking toggle, logging actual provider mappings.

    Arguments:
        requested: shared requested level
        effective: expected DeepSeek level, or disabled thinking
        caplog: captured log messages
    """
    caplog.set_level("INFO")
    client, request = _make_client()
    provider = DeepSeekProvider(client=client, reasoning_effort=requested)
    provider.chat_completion([{"role": "user", "content": "input"}], _Answer)
    options = request.call_args.kwargs
    thinking = "enabled"
    if effective is None:
        thinking = "disabled"
        assert "reasoning_effort" not in options
    else:
        assert options["reasoning_effort"] == effective
        if requested != effective:
            assert f"maps reasoning effort {requested} to {effective}" in caplog.text
    assert options["extra_body"] == {"thinking": {"type": thinking}}


def test_reasoning_cache_separates_efforts_and_reuses_equivalent_mappings(
    tmp_path: Path,
):
    """Cache hits follow effective reasoning configuration, including omission.

    Arguments:
        tmp_path: temporary cache root
    """
    cache = LlmCache(tmp_path, "review")
    low = OpenAIProvider(reasoning_effort="low")
    high = OpenAIProvider(reasoning_effort="xhigh")
    cache.save(low.cache_identity, "system", "[]", "{}", "low result")
    assert cache.load(low.cache_identity, "system", "[]", "{}") == "low result"
    assert cache.load(high.cache_identity, "system", "[]", "{}") is None
    assert cache.load(OpenAIProvider().cache_identity, "system", "[]", "{}") is None
    mapped = DeepSeekProvider(reasoning_effort="xhigh")
    canonical = DeepSeekProvider(reasoning_effort="high")
    cache.save(mapped.cache_identity, "system", "[]", "{}", "deepseek result")
    assert (
        cache.load(canonical.cache_identity, "system", "[]", "{}") == "deepseek result"
    )
    assert (
        DeepSeekProvider(reasoning_effort="none").cache_identity
        != DeepSeekProvider().cache_identity
    )


def test_invalid_effort_and_unsupported_provider_fail_before_requests():
    """Reject typos and providers that have not opted into reasoning support."""
    with raises(ValueError, match="ReasoningEffort"):
        OpenAIProvider(reasoning_effort="typo")
    with raises(ValueError, match="does not support explicit reasoning"):
        _UnsupportedProvider(reasoning_effort="high")
