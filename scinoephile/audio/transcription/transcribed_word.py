#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Single word within a transcribed segment."""

from __future__ import annotations

from pydantic import BaseModel, Field

__all__ = ["TranscribedWord"]


class TranscribedWord(BaseModel):
    """Single word within a transcribed segment."""

    text: str = Field(..., description="Word's transcription.")
    """Word transcription."""
    start: float = Field(..., description="Start time of word in seconds.")
    """Start time of the word in seconds."""
    end: float = Field(..., description="End time of word in seconds.")
    """End time of the word in seconds."""
    confidence: float = Field(..., description="Confidence of transcription.")
    """Transcription confidence."""
    following_voice_activity_score: float | None = Field(
        None,
        ge=0,
        le=1,
        description=("Mean VAD model score between this word and the following word."),
    )
    """Mean VAD model score in the following inter-word gap, when available."""
    voice_activity_coverage: float | None = Field(
        None,
        ge=0,
        le=1,
        description="Fraction of the word duration meeting the VAD threshold.",
    )
    """Fraction of the word duration meeting the configured VAD threshold."""
    voice_activity_peak: float | None = Field(
        None, ge=0, le=1, description="Peak VAD model score during this word."
    )
    """Peak VAD model score during this word, when available."""
    voice_activity_score: float | None = Field(
        None, ge=0, le=1, description="Mean VAD model score during this word."
    )
    """Mean VAD model score during this word, when available."""
