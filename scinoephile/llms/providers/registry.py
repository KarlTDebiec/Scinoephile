#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factory registry for concrete LLM providers.

This layer composes provider implementations for higher-level modules without
coupling `scinoephile.core` to any specific provider.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import LLMProvider

from .deepseek import DeepSeekProvider
from .openai import OpenAIProvider

__all__ = [
    "get_default_provider",
    "get_provider",
    "register_provider_factory",
]

_DEFAULT_PROVIDER_NAME = "openai"
_PROVIDER_FACTORIES: dict[str, Callable[..., LLMProvider]] = {
    "deepseek": DeepSeekProvider,
    _DEFAULT_PROVIDER_NAME: OpenAIProvider,
}


def register_provider_factory(
    provider_name: str, provider_factory: Callable[..., LLMProvider]
):
    """Register a provider factory under a provider name.

    Arguments:
        provider_name: provider identifier
        provider_factory: callable returning an LLMProvider
    """
    _PROVIDER_FACTORIES[provider_name] = provider_factory


def get_provider(provider_name: str, **kwargs: Any) -> LLMProvider:
    """Construct and return a named provider.

    Arguments:
        provider_name: provider identifier
        **kwargs: keyword arguments forwarded to provider factory
    Returns:
        constructed provider instance
    Raises:
        ScinoephileError: provider name is not registered
    """
    provider_factory = _PROVIDER_FACTORIES.get(provider_name)
    if provider_factory is None:
        raise ScinoephileError(f"Unknown LLM provider '{provider_name}'.")
    return provider_factory(**kwargs)


def get_default_provider() -> LLMProvider:
    """Construct and return the default provider."""
    return get_provider(_DEFAULT_PROVIDER_NAME)
