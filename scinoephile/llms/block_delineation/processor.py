#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processor for block-level delineation LLM queries."""

from __future__ import annotations

from scinoephile.core.llms import Processor

from .manager import BlockDelineationManager
from .prompt import BlockDelineationPrompt

__all__ = ["BlockDelineationProcessor"]


class BlockDelineationProcessor(Processor):
    """Processor for block-level delineation LLM queries."""

    prompt: BlockDelineationPrompt
    """Text for block-level delineation."""
    manager_cls = BlockDelineationManager
    """Manager used to construct prompt-specific models."""
