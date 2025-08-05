#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for 粤文 shifting."""

from __future__ import annotations

from pydantic import Field, model_validator

from scinoephile.core.abcs import Answer


class ShiftAnswer(Answer):
    """Answer for 粤文 shifting."""

    yuewen_1_shifted: str = Field(..., description="Shifted 粤文 of subtitle 1.")
    yuewen_2_shifted: str = Field(..., description="Shifted 粤文 of subtitle 2.")

    @model_validator(mode="after")
    def validate_answer(self) -> ShiftAnswer:
        """Ensure answer is internally valid."""
        if not self.yuewen_1_shifted and not self.yuewen_2_shifted:
            raise ValueError(
                "Answer must have 粤文 1 shifted, 粤文 2 shifted, or both."
            )
        return self
