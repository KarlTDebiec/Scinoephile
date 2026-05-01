#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""DeepSeek LLM Provider."""

from __future__ import annotations

from openai import OpenAI

from scinoephile.core.llms import OpenAIProviderBase

__all__ = ["DeepSeekProvider"]


class DeepSeekProvider(OpenAIProviderBase):
    """DeepSeek LLM Provider (OpenAI-SDK compatible)."""

    default_model = "deepseek-v4-flash"
    """Default DeepSeek model identifier."""

    base_url = "https://api.deepseek.com"
    """DeepSeek API base URL."""

    api_key_env_var_name = "DEEPSEEK_API_KEY"
    """Environment variable name used for the DeepSeek API key."""

    def __init__(
        self,
        client: OpenAI | None = None,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
    ):
        """Initialize.

        Arguments:
            client: synchronous OpenAI client
            api_key: DeepSeek API key; if omitted, `DEEPSEEK_API_KEY` is used
            base_url: DeepSeek base URL override
        """
        super().__init__(client=client, api_key=api_key, base_url=base_url)

    def _should_use_strict_tools(self) -> bool:
        """Return whether DeepSeek strict tool schemas should be enabled."""
        base_url = self._get_base_url()
        return bool(base_url and base_url.rstrip("/").endswith("/beta"))
