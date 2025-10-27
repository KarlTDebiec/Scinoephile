#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Abstract base classes related to English proofing."""

from __future__ import annotations

from scinoephile.core.english.proofing.abcs.english_proof_answer import (
    EnglishProofAnswer,
)
from scinoephile.core.english.proofing.abcs.english_proof_query import EnglishProofQuery
from scinoephile.core.english.proofing.abcs.english_proof_test_case import (
    EnglishProofTestCase,
)

__all__ = [
    "EnglishProofAnswer",
    "EnglishProofQuery",
    "EnglishProofTestCase",
]
