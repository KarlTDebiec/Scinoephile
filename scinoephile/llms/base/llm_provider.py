#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Compatibility wrapper for LLM provider interfaces."""

from __future__ import annotations

from scinoephile.core.llms import llm_provider as _llm_provider
from scinoephile.core.llms.llm_provider import LLMProvider

ChatCompletionKwargs = _llm_provider.ChatCompletionKwargs

__all__ = ["ChatCompletionKwargs", "LLMProvider"]
