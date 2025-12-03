#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to Cantonese audio transcription proofing."""

from __future__ import annotations

from .answer import ProofingAnswer
from .llm_queryer import ProofingLLMQueryer
from .prompt import ProofingPrompt
from .query import ProofingQuery
from .test_case import ProofingTestCase

__all__ = [
    "ProofingAnswer",
    "ProofingLLMQueryer",
    "ProofingPrompt",
    "ProofingQuery",
    "ProofingTestCase",
]
