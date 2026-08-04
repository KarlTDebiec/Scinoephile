#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OpenAI LLM Provider."""

from __future__ import annotations

from re import match
from typing import ClassVar

from scinoephile.core.llms import OpenAIProviderBase

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

    @property
    def use_explicit_prompt_caching(self) -> bool:
        """Whether the configured model supports explicit prompt caching."""
        version_match = match(r"^gpt-(\d+)(?:\.(\d+))?", self.model)
        if version_match is None:
            return False
        major = int(version_match.group(1))
        minor = int(version_match.group(2) or 0)
        return (major, minor) >= (5, 6)
