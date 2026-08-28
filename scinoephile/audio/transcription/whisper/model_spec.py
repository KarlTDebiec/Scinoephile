#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Whisper speech-to-text model specifications."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.language import Language
from scinoephile.core.ml import ModelSpec

__all__ = ["WHISPER_LARGE_V3_CANTONESE_MODEL", "WhisperModelSpec"]


@dataclass(frozen=True, slots=True)
class WhisperModelSpec(ModelSpec):
    """Complete specification of one Whisper speech-to-text model."""

    languages: dict[Language, str]
    """Whisper language codes keyed by Scinoephile language."""


WHISPER_LARGE_V3_CANTONESE_MODEL = WhisperModelSpec(
    name="khleeloo/whisper-large-v3-cantonese",
    revision="f48a890f78c7b6acf723f25d8c81e232ac7469ca",
    languages={Language.yue_hans: "yue", Language.yue_hant: "yue"},
)
"""Default Whisper large-v3 Cantonese model."""
