#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""OpenAI LLM Provider."""

from __future__ import annotations

from typing import override

from openai import OpenAI

from scinoephile.core.llms import OpenAIProviderBase

__all__ = ["OpenAIProvider"]


class OpenAIProvider(OpenAIProviderBase):
    """OpenAI LLM Provider."""

    default_model = "gpt-5.4"
    """Default OpenAI model identifier."""

    def __init__(self, client: OpenAI | None = None):
        """Initialize.

        Arguments:
            client: synchronous OpenAI client
        """
        super().__init__(client=client)

    @property
    @override
    def sync_client(self) -> OpenAI:
        """Synchronous OpenAI client."""
        if self._sync_client is None:
            self._sync_client = OpenAI()
        return self._sync_client
