#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OpenAI LLM Provider."""

from __future__ import annotations

from typing import Any, ClassVar

from scinoephile.core.llms import OpenAIProviderBase, ReasoningEffort

__all__ = ["OpenAIProvider"]


class OpenAIProvider(OpenAIProviderBase):
    """OpenAI LLM Provider."""

    description_localizations: ClassVar[dict[str, str]] = {
        "zh-hans": "OpenAI LLM 提供商。",
        "zh-hant": "OpenAI LLM 提供商。",
    }
    """Provider description translations keyed by locale."""

    model = "gpt-5.6-luna"
    """OpenAI model identifier."""

    api_key_env_var_name = "OPENAI_API_KEY"
    """Environment variable name used for the OpenAI API key."""

    explicit_prompt_caching = True
    """Whether requests should mark and route a stable cached prefix."""

    def _get_reasoning_options(self, effort: ReasoningEffort | None) -> dict[str, Any]:
        """Translate OpenAI reasoning effort without overriding omitted defaults.

        Arguments:
            effort: requested reasoning level, or None for the API default
        Returns:
            OpenAI completion parameters; model-specific support is API-validated
        """
        if effort is None:
            return {}
        return {"reasoning_effort": effort.value}
