#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Provider registry for default LLM providers."""

from __future__ import annotations

import importlib
from collections.abc import Callable

from scinoephile.core.abcs.llm_provider import LLMProvider
from scinoephile.core.exceptions import ScinoephileError

__all__ = ["get_default_provider", "register_default_provider"]


class _ProviderRegistry:
    def __init__(self):
        self.factory: Callable[[], LLMProvider] | None = None


_provider_registry = _ProviderRegistry()


def register_default_provider(
    factory: Callable[[], LLMProvider], *, override: bool = False
):
    """Register a factory to create the default LLM provider.

    Arguments:
        factory: Callable that returns an :class:`LLMProvider` instance.
        override: If True, replace an existing default provider factory.
    """
    if _provider_registry.factory is None or override:
        _provider_registry.factory = factory


def get_default_provider() -> LLMProvider:
    """Return the default LLM provider.

    Returns:
        Registered default :class:`LLMProvider` instance.

    Raises:
        ScinoephileError: If no default provider factory has been registered.
    """
    if _provider_registry.factory is None:
        try:
            importlib.import_module("scinoephile.openai")
        except ImportError:
            pass

    if _provider_registry.factory is None:
        raise ScinoephileError("No default LLMProvider has been registered.")
    return _provider_registry.factory()
