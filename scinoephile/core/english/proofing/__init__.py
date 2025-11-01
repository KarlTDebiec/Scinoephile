#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English proofing."""

from __future__ import annotations

from scinoephile.core.english.proofing.english_proof_llm_queryer import (
    EnglishProofLLMQueryer,
)
from scinoephile.core.english.proofing.english_proofer import EnglishProofer

__all__ = [
    "EnglishProofLLMQueryer",
    "EnglishProofer",
]
