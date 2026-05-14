#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Factory registry for concrete LLM providers.

This layer composes provider implementations for higher-level modules without
coupling `scinoephile.core` to any specific provider.
"""

from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import Any, cast

from scinoephile.core import ScinoephileError
from scinoephile.core.llms import LLMProvider

__all__ = [
    "get_default_provider",
    "get_provider",
    "register_provider_factory",
]

_DEFAULT_PROVIDER_NAME = "openai"
_PROVIDER_FACTORY_IMPORTS = {
    "deepseek": ("scinoephile.llms.providers.deepseek_provider", "DeepSeekProvider"),
    _DEFAULT_PROVIDER_NAME: (
        "scinoephile.llms.providers.openai_provider",
        "OpenAIProvider",
    ),
}
_PROVIDER_FACTORIES: dict[str, Callable[..., LLMProvider]] = {}


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
        if provider_name not in _PROVIDER_FACTORY_IMPORTS:
            raise ScinoephileError(f"Unknown LLM provider '{provider_name}'.")
        provider_factory = _load_provider_factory(provider_name)
    return provider_factory(**kwargs)


def get_default_provider() -> LLMProvider:
    """Construct and return the default provider."""
    return get_provider(_DEFAULT_PROVIDER_NAME)


def _load_provider_factory(provider_name: str) -> Callable[..., LLMProvider]:
    """Load a built-in provider factory on demand.

    Arguments:
        provider_name: provider identifier
    Returns:
        provider factory
    Raises:
        ImportError: if optional LLM dependencies are missing
    """
    module_name, class_name = _PROVIDER_FACTORY_IMPORTS[provider_name]
    try:
        module = import_module(module_name)
    except ImportError as exc:
        raise ImportError(
            "LLM provider support requires optional LLM dependencies. "
            "Install scinoephile with the 'llm' extra."
        ) from exc
    provider_factory = getattr(module, class_name)
    _PROVIDER_FACTORIES[provider_name] = cast(
        Callable[..., LLMProvider],
        provider_factory,
    )
    return _PROVIDER_FACTORIES[provider_name]
