#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factory registry for concrete LLM providers.

This layer composes provider implementations for higher-level modules without
coupling `scinoephile.core` to any specific provider.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from inspect import getdoc
from typing import Any

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import LLMProvider

from .deepseek_provider import DeepSeekProvider
from .openai_provider import OpenAIProvider

__all__ = [
    "get_default_provider",
    "get_default_provider_name",
    "get_provider",
    "get_provider_description",
    "get_provider_names",
    "register_provider_factory",
]

_DEFAULT_PROVIDER_NAME = "openai"
_PROVIDER_FACTORIES: dict[str, Callable[..., LLMProvider]] = {
    "deepseek": DeepSeekProvider,
    _DEFAULT_PROVIDER_NAME: OpenAIProvider,
}


def get_default_provider() -> LLMProvider:
    """Construct and return the default provider."""
    return get_provider(_DEFAULT_PROVIDER_NAME)


def get_default_provider_name() -> str:
    """Get the default provider name.

    Returns:
        default provider name
    """
    return _DEFAULT_PROVIDER_NAME


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
    provider_factory = _get_provider_factory(provider_name)
    return provider_factory(**kwargs)


def get_provider_description(provider_name: str, locale_name: str = "en") -> str:
    """Get a registered provider's localized description.

    Arguments:
        provider_name: provider identifier
        locale_name: locale name to use for description lookup
    Returns:
        localized provider description when available, otherwise English description
    Raises:
        ScinoephileError: provider name is not registered
    """
    provider_factory = _get_provider_factory(provider_name)
    if locale_name != "en":
        localizations = getattr(provider_factory, "description_localizations", {})
        if isinstance(localizations, Mapping):
            description = localizations.get(locale_name)
            if isinstance(description, str):
                return description

    description = getdoc(provider_factory)
    if description is None:
        return ""
    return " ".join(description.split())


def get_provider_names() -> tuple[str, ...]:
    """Get registered provider names.

    Returns:
        sorted registered provider names
    """
    return tuple(sorted(_PROVIDER_FACTORIES))


def register_provider_factory(
    provider_name: str, provider_factory: Callable[..., LLMProvider]
):
    """Register a provider factory under a provider name.

    Arguments:
        provider_name: provider identifier
        provider_factory: callable returning an LLMProvider
    """
    _PROVIDER_FACTORIES[provider_name] = provider_factory


def _get_provider_factory(provider_name: str) -> Callable[..., LLMProvider]:
    """Get a registered provider factory.

    Arguments:
        provider_name: provider identifier
    Returns:
        provider factory
    Raises:
        ScinoephileError: provider name is not registered
    """
    provider_factory = _PROVIDER_FACTORIES.get(provider_name)
    if provider_factory is None:
        raise ScinoephileError(f"Unknown LLM provider '{provider_name}'.")
    return provider_factory
