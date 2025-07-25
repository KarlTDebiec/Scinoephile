#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for 粤文 shifting."""

from __future__ import annotations

from pydantic import Field, model_validator

from scinoephile.core.abcs import Answer


class ShiftAnswer(Answer):
    """Answer for 粤文 shifting."""

    one_yuewen_shifted: str = Field(..., description="Shifted 粤文 of text one.")
    two_yuewen_shifted: str = Field(..., description="Shifted 粤文 of text two.")

    @model_validator(mode="after")
    def validate_answer(self) -> ShiftAnswer:
        """Ensure answer is internally valid."""
        if not self.one_yuewen_shifted and not self.two_yuewen_shifted:
            raise ValueError("Answer must have either shifted 粤文 text one or two.")
        return self
