#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processor for block-level punctuation LLM queries."""

from __future__ import annotations

from scinoephile.core.llms import Processor

from .manager import BlockPunctuationManager, PositionalBlockPunctuationManager
from .prompt import BlockPunctuationPrompt, PositionalBlockPunctuationPrompt

__all__ = ["BlockPunctuationProcessor", "PositionalBlockPunctuationProcessor"]


class BlockPunctuationProcessor(Processor):
    """Processor for block-level punctuation LLM queries."""

    prompt: BlockPunctuationPrompt
    """Text for block-level punctuation."""
    manager_cls = BlockPunctuationManager
    """Manager used to construct prompt-specific models."""


class PositionalBlockPunctuationProcessor(Processor):
    """Processor for positional block-punctuation LLM queries."""

    prompt: PositionalBlockPunctuationPrompt
    """Text for positional block punctuation."""
    manager_cls = PositionalBlockPunctuationManager
    """Manager used to construct prompt-specific models."""
