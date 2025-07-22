#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Models related to Cantonese audio."""

from __future__ import annotations

from scinoephile.audio.cantonese.models.merge_answer import MergeAnswer
from scinoephile.audio.cantonese.models.merge_query import MergeQuery
from scinoephile.audio.cantonese.models.merge_test_case import MergeTestCase
from scinoephile.audio.cantonese.models.proofread_answer import ProofreadAnswer
from scinoephile.audio.cantonese.models.proofread_query import ProofreadQuery
from scinoephile.audio.cantonese.models.proofread_test_case import ProofreadTestCase
from scinoephile.audio.cantonese.models.shift_answer import ShiftAnswer
from scinoephile.audio.cantonese.models.shift_query import ShiftQuery
from scinoephile.audio.cantonese.models.shift_test_case import ShiftTestCase
from scinoephile.audio.cantonese.models.split_answer import SplitAnswer
from scinoephile.audio.cantonese.models.split_query import SplitQuery
from scinoephile.audio.cantonese.models.split_test_case import SplitTestCase

__all__ = [
    "MergeAnswer",
    "MergeQuery",
    "MergeTestCase",
    "ProofreadAnswer",
    "ProofreadQuery",
    "ProofreadTestCase",
    "ShiftAnswer",
    "ShiftQuery",
    "ShiftTestCase",
    "SplitAnswer",
    "SplitQuery",
    "SplitTestCase",
]
