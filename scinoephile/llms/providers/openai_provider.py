#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OpenAI LLM Provider."""

from __future__ import annotations

from scinoephile.core.llms import OpenAIProviderBase

__all__ = ["OpenAIProvider"]


class OpenAIProvider(OpenAIProviderBase):
    """OpenAI LLM Provider."""

    model = "gpt-5.4"
    """OpenAI model identifier."""
