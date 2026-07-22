#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processor for punctuation LLM queries."""

from __future__ import annotations

from scinoephile.core.llms import Processor

from .manager import PunctuationManager
from .prompt import PunctuationPrompt

__all__ = ["PunctuationProcessor"]


class PunctuationProcessor(Processor):
    """Processor for punctuation LLM queries."""

    prompt: PunctuationPrompt
    """Text for LLM correspondence."""

    manager_cls = PunctuationManager
    """Manager class used to construct test case models."""
