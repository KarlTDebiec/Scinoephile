#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for 粤文 distribution."""

from __future__ import annotations

from pydantic import Field, model_validator

from scinoephile.core import ScinoephileError
from scinoephile.core.abcs import Answer


class DistributeAnswer(Answer):
    """Answer for 粤文 distribution."""

    one_yuewen_to_append: str = Field(
        ..., description="粤文 to append to 粤文 text one."
    )
    two_yuewen_to_prepend: str = Field(
        ..., description="粤文 to prepend to 粤文 text two."
    )

    @model_validator(mode="after")
    def validate_answer(self) -> DistributeAnswer:
        """Ensure answer is internally valid."""
        if not self.one_yuewen_to_append and not self.two_yuewen_to_prepend:
            raise ScinoephileError("Answer must have 粤文 text to append or prepend.")
        return self
