#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Whisper speech-to-text model definitions."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.language import Language

__all__ = ["CANTONESE_MODEL", "WhisperModel"]


@dataclass
class WhisperModel:
    """Complete definition of one Whisper speech-to-text model."""

    model_name: str
    """Hugging Face model name or local model path."""
    languages: dict[Language, str]
    """Whisper language codes keyed by Scinoephile language."""


CANTONESE_MODEL = WhisperModel(
    model_name="khleeloo/whisper-large-v3-cantonese",
    languages={Language.yue_hans: "yue", Language.yue_hant: "yue"},
)
"""Default Cantonese Whisper model."""
