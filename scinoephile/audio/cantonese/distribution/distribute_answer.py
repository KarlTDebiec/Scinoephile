#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for 粤文 distribution."""

from __future__ import annotations

from pydantic import Field, model_validator

from scinoephile.core.abcs import Answer


class DistributeAnswer(Answer):
    """Answer for 粤文 distribution."""

    yuewen_1_to_append: str = Field(
        ..., description="粤文 text to append to 粤文 subtitle 1."
    )
    yuewen_2_to_prepend: str = Field(
        ..., description="粤文 text to prepend to 粤文 subtitle 2."
    )

    @model_validator(mode="after")
    def validate_answer(self) -> DistributeAnswer:
        """Ensure answer is internally valid."""
        if not self.yuewen_1_to_append and not self.yuewen_2_to_prepend:
            raise ValueError(
                "Answer must have 粤文 1 to append, 粤文 2 to prepend, or both."
            )
        return self
