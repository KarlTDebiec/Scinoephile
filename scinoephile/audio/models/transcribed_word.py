#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Single word within a transcribed segment."""

from pydantic import BaseModel, Field


class TranscribedWord(BaseModel):
    """Single word within a transcribed segment."""

    text: str = Field(..., description="Word's transcription.")
    start: float = Field(..., description="Start time of word in seconds.")
    end: float = Field(..., description="End time of word in seconds.")
    confidence: float = Field(..., description="Confidence of transcription.")
