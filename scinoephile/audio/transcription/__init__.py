#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to audio transcription."""

from __future__ import annotations

from .transcribed_segment import TranscribedSegment
from .transcribed_word import TranscribedWord

__all__ = [
    "TranscribedSegment",
    "TranscribedWord",
]
