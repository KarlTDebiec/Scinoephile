#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Result types used by Whisper speech recognition."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.audio.transcription.transcribed_segment import TranscribedSegment

__all__ = ["WhisperNativeResult"]


@dataclass(frozen=True, slots=True)
class WhisperNativeResult:
    """Result of native Whisper recognition without word timestamps."""

    text: str
    """Complete recognized text."""

    segments: list[TranscribedSegment]
    """Native Whisper segments carrying recognition quality signals."""
