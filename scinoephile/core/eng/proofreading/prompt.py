#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for English proofreading."""

from __future__ import annotations

from scinoephile.core.eng import EngPrompt
from scinoephile.core.proofreading import ProofreadingPrompt

__all__ = ["EngProofreadingPrompt"]


class EngProofreadingPrompt(ProofreadingPrompt, EngPrompt):
    """LLM correspondence text for English proofreading."""
