#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for English proofreading."""

from __future__ import annotations

from scinoephile.core.english import EnglishPrompt
from scinoephile.core.proofreading import ProofreadingPrompt

__all__ = ["EnglishProofreadingPrompt"]


class EnglishProofreadingPrompt(ProofreadingPrompt, EnglishPrompt):
    """LLM correspondence text for English proofreading."""
