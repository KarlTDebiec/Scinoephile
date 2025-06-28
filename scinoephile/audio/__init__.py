#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to audio."""

from __future__ import annotations

from scinoephile.audio.audio_block import AudioBlock
from scinoephile.audio.audio_series import AudioSeries
from scinoephile.audio.audio_subtitle import AudioSubtitle
from scinoephile.audio.hanzi_converter import HanziConverter
from scinoephile.audio.transcribed_segment import TranscribedSegment
from scinoephile.audio.transcribed_word import TranscribedWord
from scinoephile.audio.transcriber import Transcriber
from scinoephile.audio.transcription_manager import TranscriptionManager
from scinoephile.audio.transcription_payload import TranscriptionPayload

__all__ = [
    "AudioBlock",
    "AudioSeries",
    "AudioSubtitle",
    "HanziConverter",
    "TranscribedWord",
    "TranscribedSegment",
    "Transcriber",
    "TranscriptionManager",
    "TranscriptionPayload",
]
