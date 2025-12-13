#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Base classes for proofreading subtitles."""

from __future__ import annotations

from .answer import ProofreadingAnswer
from .prompt import ProofreadingPrompt
from .proofreader import Proofreader
from .query import ProofreadingQuery
from .test_case import ProofreadingTestCase

__all__ = [
    "Proofreader",
    "ProofreadingAnswer",
    "ProofreadingPrompt",
    "ProofreadingQuery",
    "ProofreadingTestCase",
]
