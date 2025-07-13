#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Models related to audio."""

from __future__ import annotations

from scinoephile.audio.models.merge_answer import MergeAnswer
from scinoephile.audio.models.merge_query import MergeQuery
from scinoephile.audio.models.shift_answer import ShiftAnswer
from scinoephile.audio.models.shift_query import ShiftQuery
from scinoephile.audio.models.split_answer import SplitAnswer
from scinoephile.audio.models.split_query import SplitQuery
from scinoephile.audio.models.transcribed_segment import TranscribedSegment
from scinoephile.audio.models.transcribed_word import TranscribedWord

__all__ = [
    "MergeAnswer",
    "MergeQuery",
    "ShiftAnswer",
    "ShiftQuery",
    "SplitAnswer",
    "SplitQuery",
    "TranscribedWord",
    "TranscribedSegment",
]
