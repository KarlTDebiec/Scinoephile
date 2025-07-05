#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Models related to audio."""

from __future__ import annotations

from scinoephile.audio.models.merge_payload import MergePayload
from scinoephile.audio.models.transcribed_segment import TranscribedSegment
from scinoephile.audio.models.transcribed_word import TranscribedWord
from scinoephile.audio.models.transcription_payload import TranscriptionPayload

__all__ = [
    "MergePayload",
    "TranscribedWord",
    "TranscribedSegment",
    "TranscriptionPayload",
]
