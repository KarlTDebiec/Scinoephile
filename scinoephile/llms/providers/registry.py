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
    "DEFAULT_PROVIDER_NAME",
    "get_provider_api_key_env_var_name",
    "get_provider_default_model",
    "get_provider",
    "get_provider_description",
    "get_provider_names",
    "register_provider_factory",
]

DEFAULT_PROVIDER_NAME = "openai"
"""Default LLM provider name."""

_PROVIDER_FACTORIES: dict[str, Callable[..., LLMProvider]] = {
    "deepseek": DeepSeekProvider,
    DEFAULT_PROVIDER_NAME: OpenAIProvider,
}


def get_provider(
    provider_name: str = DEFAULT_PROVIDER_NAME, **kwargs: Any
) -> LLMProvider:
    """Construct and return a named provider.

    Arguments:
        provider_name: provider identifier, defaulting to DEFAULT_PROVIDER_NAME
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
    provider_factory = _PROVIDER_FACTORIES.get(provider_name)
    if provider_factory is None:
        raise ScinoephileError(f"Unknown LLM provider '{provider_name}'.")
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


def get_provider_api_key_env_var_name(provider_name: str) -> str | None:
    """Get the environment variable used for a provider's API key.

    Arguments:
        provider_name: provider identifier
    Returns:
        environment variable name, if configured
    Raises:
        ScinoephileError: provider name is not registered
    """
    provider_factory = _PROVIDER_FACTORIES.get(provider_name)
    if provider_factory is None:
        raise ScinoephileError(f"Unknown LLM provider '{provider_name}'.")
    env_var_name = getattr(provider_factory, "api_key_env_var_name", None)
    if not isinstance(env_var_name, str):
        return None
    return env_var_name


def get_provider_default_model(provider_name: str) -> str | None:
    """Get a provider's default model.

    Arguments:
        provider_name: provider identifier
    Returns:
        default model identifier, if configured
    Raises:
        ScinoephileError: provider name is not registered
    """
    provider_factory = _PROVIDER_FACTORIES.get(provider_name)
    if provider_factory is None:
        raise ScinoephileError(f"Unknown LLM provider '{provider_name}'.")
    model = getattr(provider_factory, "model", None)
    if not isinstance(model, str):
        return None
    return model


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
