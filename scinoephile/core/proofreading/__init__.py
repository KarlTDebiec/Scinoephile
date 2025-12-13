#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Base classes for proofreading subtitles."""

from __future__ import annotations

from scinoephile.core.proofreading.answer import ProofreadingAnswer
from scinoephile.core.proofreading.prompt import ProofreadingPrompt
from scinoephile.core.proofreading.proofreader import Proofreader
from scinoephile.core.proofreading.query import ProofreadingQuery
from scinoephile.core.proofreading.test_case import ProofreadingTestCase

__all__ = [
    "Proofreader",
    "ProofreadingAnswer",
    "ProofreadingPrompt",
    "ProofreadingQuery",
    "ProofreadingTestCase",
]
