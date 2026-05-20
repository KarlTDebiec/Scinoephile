#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to audio.

This module may import from: common, core, lang

Hierarchy within module (lower may import from higher)::
* transcription
* speech_activity
* subtitles
"""

from __future__ import annotations

from .speech_activity import (
    SileroSpeechActivityDetector,
    SpeechActivityDetector,
    SpeechInterval,
    WhisperSpeechActivityDetector,
)

__all__ = [
    "SileroSpeechActivityDetector",
    "SpeechActivityDetector",
    "SpeechInterval",
    "WhisperSpeechActivityDetector",
]
