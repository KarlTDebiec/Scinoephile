#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Cantonese audio transcription proofing."""

from __future__ import annotations

from scinoephile.audio.cantonese.proofing.proofing_answer import ProofingAnswer
from scinoephile.audio.cantonese.proofing.proofing_llm_queryer import ProofingLLMQueryer
from scinoephile.audio.cantonese.proofing.proofing_llm_text import ProofingLLMText
from scinoephile.audio.cantonese.proofing.proofing_query import ProofingQuery
from scinoephile.audio.cantonese.proofing.proofing_test_case import ProofingTestCase

__all__ = [
    "ProofingAnswer",
    "ProofingLLMQueryer",
    "ProofingLLMText",
    "ProofingQuery",
    "ProofingTestCase",
]
