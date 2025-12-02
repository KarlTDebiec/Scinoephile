#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for 粤文 merging."""

from __future__ import annotations

from pydantic import Field, model_validator

from scinoephile.core.abcs import Answer


class MergingAnswer(Answer):
    """Answer for 粤文 merging."""

    yuewen_merged: str = Field(..., description="Merged 粤文 of subtitle.")

    @model_validator(mode="after")
    def validate_answer(self) -> MergingAnswer:
        """Ensure answer is internally valid."""
        if not self.yuewen_merged:
            raise ValueError("Answer must have merged 粤文 subtitle.")
        return self
