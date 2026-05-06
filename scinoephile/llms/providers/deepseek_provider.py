#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""DeepSeek LLM Provider."""

from __future__ import annotations

from scinoephile.core.llms import OpenAIProviderBase

__all__ = ["DeepSeekProvider"]


class DeepSeekProvider(OpenAIProviderBase):
    """DeepSeek LLM Provider (OpenAI-SDK compatible)."""

    model = "deepseek-v4-flash"
    """DeepSeek model identifier."""

    base_url = "https://api.deepseek.com"
    """DeepSeek API base URL."""

    api_key_env_var_name = "DEEPSEEK_API_KEY"
    """Environment variable name used for the DeepSeek API key."""

    @property
    def use_strict_tools(self) -> bool:
        """Whether DeepSeek strict tool schemas should be enabled."""
        return bool(self.base_url and self.base_url.rstrip("/").endswith("/beta"))
