#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM provider settings shared by audit editor jobs."""

from __future__ import annotations

from scinoephile.core.llms import LLMProvider, ReasoningEffort
from scinoephile.llms.providers.registry import get_provider, get_provider_names

__all__ = ["get_job_provider"]


def get_job_provider(
    provider_name: str, model_name: str, effort: str
) -> tuple[LLMProvider, str]:
    """Validate editor settings and configure the selected LLM provider.

    Arguments:
        provider_name: registered provider identifier
        model_name: optional model override
        effort: reasoning level or blank for the provider default
    Returns:
        configured provider and normalized model override
    Raises:
        ValueError: if the provider, model override, or reasoning level is invalid
    """
    if provider_name not in get_provider_names():
        raise ValueError("Choose a supported LLM provider")
    model_name = model_name.strip()
    if len(model_name) > 200 or any(ord(char) < 32 for char in model_name):
        raise ValueError("Use a model identifier of up to 200 characters")
    options: dict[str, str | None] = {"model": model_name or None}
    if effort:
        options["reasoning_effort"] = ReasoningEffort(effort)
    return get_provider(provider_name, **options), model_name
