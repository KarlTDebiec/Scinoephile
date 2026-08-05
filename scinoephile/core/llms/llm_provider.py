#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, TypedDict, Unpack

from pydantic import JsonValue

from .answer import Answer
from .tool_box import ToolBox

__all__ = ["ChatCompletionKwargs", "ChatCompletionMetrics", "LLMProvider"]


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


class ChatCompletionKwargs(TypedDict, total=False):
    """Keyword arguments for LLM chat completion methods.

    These correspond to common parameters accepted by chat-completion style APIs.
    """

    temperature: float
    """Sampling temperature."""

    max_tokens: int
    """Maximum number of tokens to generate."""

    top_p: float
    """Nucleus sampling cutoff."""

    frequency_penalty: float
    """Penalty for repeated token frequency."""

    presence_penalty: float
    """Penalty for repeated token presence."""

    stop: str | list[str]
    """Stop sequence or sequences."""

    seed: int
    """Deterministic sampling seed."""


class LLMProvider(ABC):
    """ABC for LLM providers."""

    @property
    def cache_identity(self) -> dict[str, JsonValue]:
        """Stable, non-secret configuration affecting completion behavior.

        Configurable provider implementations must extend this identity with all
        behavior-affecting settings while excluding credentials.
        """
        return {"implementation": f"{type(self).__module__}.{type(self).__qualname__}"}

    @abstractmethod
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
        """Return chat completion text synchronously.

        Arguments:
            messages: messages to send
            response_format: structured response format
            tool_box: available tools
            operation: stable LLM operation identifier
            query_key_sha256: SHA-256 digest of the semantic query key
            query_attempt: one-based answer-validation attempt
            **kwargs: provider-specific keyword arguments
        Returns:
            completion text from the model
        Raises:
            ScinoephileError: Error during chat completion
        """
        raise NotImplementedError()

    def get_completion_metrics(self) -> tuple[ChatCompletionMetrics, ...]:
        """Get completion metrics recorded by this provider instance.

        Returns:
            immutable snapshot of recorded completion metrics
        """
        return ()
