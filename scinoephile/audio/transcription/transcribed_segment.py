#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Transcribed segment."""

from __future__ import annotations

from pydantic import BaseModel, Field

from scinoephile.audio.transcription.transcribed_word import TranscribedWord


class TranscribedSegment(BaseModel):
    """Transcribed segment."""

    id: int = Field(..., description="Segment ID, usually sequential.")
    seek: int = Field(..., description="Audio seek offset where segment starts.")
    start: float = Field(..., description="Start time of segment in seconds.")
    end: float = Field(..., description="End time of the segment in seconds.")
    text: str = Field(..., description="Full transcription of segment.")
    tokens: list[int] | None = Field(None, description="Token IDs for segment.")
    temperature: float | None = Field(None, description="Sampling temperature.")
    avg_logprob: float | None = Field(None, description="Average log-probability.")
    compression_ratio: float | None = Field(None, description="Compression ratio.")
    no_speech_prob: float | None = Field(None, description="Probability of no speech.")
    words: list[TranscribedWord] | None = Field(None, description="Words in segments.")
