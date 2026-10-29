#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""DeepSeek LLM Provider."""

from __future__ import annotations

from logging import getLogger
from typing import Any, ClassVar

from scinoephile.core.llms import OpenAIProviderBase, ReasoningEffort

__all__ = ["DeepSeekProvider"]

logger = getLogger(__name__)


class DeepSeekProvider(OpenAIProviderBase):
    """DeepSeek LLM Provider (OpenAI-SDK compatible)."""

    description_localizations: ClassVar[dict[str, str]] = {
        "zh-hans": "DeepSeek LLM 提供商（兼容 OpenAI SDK）。",
        "zh-hant": "DeepSeek LLM 提供商（相容 OpenAI SDK）。",
    }
    """Provider description translations keyed by locale."""

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

    def _get_reasoning_options(self, effort: ReasoningEffort | None) -> dict[str, Any]:
        """Translate requested levels to DeepSeek's documented thinking controls.

        Arguments:
            effort: requested reasoning level, or None for the API default
        Returns:
            effective DeepSeek thinking toggle and reasoning effort
        """
        if effort is None:
            return {}
        if effort == ReasoningEffort.none:
            return {"extra_body": {"thinking": {"type": "disabled"}}}
        effective = effort
        if effort == ReasoningEffort.minimal:
            effective = ReasoningEffort.low
        elif effort in {ReasoningEffort.medium, ReasoningEffort.xhigh}:
            effective = ReasoningEffort.high
        if effective != effort:
            logger.info(f"DeepSeek maps reasoning effort {effort} to {effective}")
        return {
            "reasoning_effort": effective.value,
            "extra_body": {"thinking": {"type": "enabled"}},
        }
