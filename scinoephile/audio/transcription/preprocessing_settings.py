#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Transcription preprocessing settings."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

__all__ = [
    "DemucsMode",
    "TranscriptionPreprocessingSettings",
    "VADMode",
]


class DemucsMode(StrEnum):
    """Demucs preprocessing modes for transcription."""

    AUTO = "auto"
    """Run Demucs first and retry the original audio when needed."""
    ON = "on"
    """Run Demucs preprocessing without an original-audio fallback."""
    OFF = "off"
    """Skip Demucs preprocessing."""


class VADMode(StrEnum):
    """Voice activity detection modes for transcription."""

    AUTO = "auto"
    """Use VAD first and retry without it when needed."""
    ON = "on"
    """Use VAD without a non-VAD fallback."""
    OFF = "off"
    """Skip VAD."""


@dataclass(frozen=True, slots=True)
class TranscriptionPreprocessingSettings:
    """Demucs and VAD settings for one transcription configuration."""

    use_demucs: bool
    """Whether Demucs preprocessing is applied."""

    use_vad: bool
    """Whether voice activity detection is enabled."""
