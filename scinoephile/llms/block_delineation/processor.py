#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Processor for block-level delineation LLM queries."""

from __future__ import annotations

from scinoephile.core.llms import Processor

from .manager import (
    AdvisoryBlockDelineationManager,
    BlockDelineationManager,
    CandidateBlockDelineationManager,
)
from .prompt import (
    AdvisoryBlockDelineationPrompt,
    BlockDelineationPrompt,
    CandidateBlockDelineationPrompt,
)

__all__ = [
    "AdvisoryBlockDelineationProcessor",
    "BlockDelineationProcessor",
    "CandidateBlockDelineationProcessor",
]


class AdvisoryBlockDelineationProcessor(Processor):
    """Processor for block delineation with advisory timing suggestions."""

    prompt: AdvisoryBlockDelineationPrompt
    """Text for advisory block delineation."""
    manager_cls = AdvisoryBlockDelineationManager
    """Manager used to construct prompt-specific models."""


class BlockDelineationProcessor(Processor):
    """Processor for block-level delineation LLM queries."""

    prompt: BlockDelineationPrompt
    """Text for block-level delineation."""
    manager_cls = BlockDelineationManager
    """Manager used to construct prompt-specific models."""


class CandidateBlockDelineationProcessor(Processor):
    """Processor for candidate block-delineation LLM queries."""

    prompt: CandidateBlockDelineationPrompt
    """Text for candidate block delineation."""
    manager_cls = CandidateBlockDelineationManager
    """Manager used to construct prompt-specific models."""
