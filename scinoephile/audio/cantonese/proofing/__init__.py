#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to proofing Cantonese audio transcription."""

from __future__ import annotations

from scinoephile.audio.cantonese.proofing.proof_answer import ProofAnswer
from scinoephile.audio.cantonese.proofing.proof_query import ProofQuery
from scinoephile.audio.cantonese.proofing.proof_test_case import ProofTestCase
from scinoephile.audio.cantonese.proofing.proofer import Proofer

__all__ = [
    "ProofAnswer",
    "ProofQuery",
    "ProofTestCase",
    "Proofer",
]
