#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for English OCR fusion."""

from __future__ import annotations

from pydantic import Field, model_validator

from scinoephile.core.abcs import Answer


class EnglishFusionAnswer(Answer):
    """Answer for English OCR fusion."""

    fused: str = Field(..., description="Merged subtitle text")
    note: str = Field(..., description="Explanation of changes made")

    @model_validator(mode="after")
    def validate_answer(self) -> EnglishFusionAnswer:
        """Ensure answer is internally valid."""
        if not self.fused:
            raise ValueError("Merged subtitle text is required.")
        if not self.note:
            raise ValueError("Note is required.")
        return self
