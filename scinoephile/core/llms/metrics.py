#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Metrics for LLM completions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict

__all__ = ["ChatCompletionMetrics", "ChatCompletionMetricsSummary"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ChatCompletionMetrics:
    """Usage and timing recorded for one provider completion."""

    operation: str | None
    """Stable LLM operation identifier, if supplied by the queryer."""
    query_key_sha256: str | None
    """SHA-256 digest of the semantic query key, if supplied by the queryer."""
    model: str
    """Model identifier."""
    query_attempt: int
    """One-based answer-validation attempt."""
    tool_round: int
    """One-based tool-calling round within the query attempt."""
    input_tokens: int | None
    """Total input tokens, if reported by the provider."""
    cached_input_tokens: int | None
    """Input tokens read from the provider prompt cache, if reported."""
    cache_write_tokens: int | None
    """Input tokens written to the provider prompt cache, if reported."""
    output_tokens: int | None
    """Total output tokens, if reported by the provider."""
    reasoning_tokens: int | None
    """Output tokens used for reasoning, if reported by the provider."""
    total_tokens: int | None
    """Total input and output tokens, if reported by the provider."""
    transport_retries: int | None
    """Transport retries taken by the provider SDK, if reported."""
    latency_seconds: float
    """Wall-clock completion latency in seconds."""
    prompt_cache_key: str | None
    """Provider prompt-cache routing key, if used."""


class ChatCompletionMetricsSummary(TypedDict):
    """Aggregate LLM completion metrics suitable for JSON serialization."""

    queries: int
    """Number of unique semantic queries sent to a provider."""
    completions: int
    """Number of successful provider completions, including tool rounds."""
    validation_retries: int
    """Number of additional answer-validation attempts after the first."""
    transport_retries: int | None
    """Total provider SDK transport retries, or None when unavailable."""
    input_tokens: int | None
    """Total input tokens, or None when unavailable."""
    cached_input_tokens: int | None
    """Total input tokens read from provider prompt caches, or None."""
    uncached_input_tokens: int | None
    """Total input tokens not read from provider prompt caches, or None."""
    cache_write_tokens: int | None
    """Total input tokens written to provider prompt caches, or None."""
    output_tokens: int | None
    """Total output tokens, or None when unavailable."""
    reasoning_tokens: int | None
    """Total output tokens used for reasoning, or None when unavailable."""
    total_tokens: int | None
    """Total input and output tokens, or None when unavailable."""
    latency_seconds: float
    """Total provider latency in seconds."""
