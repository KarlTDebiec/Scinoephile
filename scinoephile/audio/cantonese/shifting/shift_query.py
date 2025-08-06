#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for 粤文 shifting."""

from __future__ import annotations

from pydantic import Field, model_validator

from scinoephile.core.abcs import Query


class ShiftQuery(Query):
    """Query for 粤文 shifting."""

    zhongwen_1: str = Field(..., description="Known 中文 of subtitle 1.")
    yuewen_1: str = Field(..., description="Transcribed 粤文 of subtitle 1.")
    zhongwen_2: str = Field(..., description="Known 中文 of subtitle 2.")
    yuewen_2: str = Field(..., description="Transcribed 粤文 of subtitle 2.")

    @model_validator(mode="after")
    def validate_query(self) -> ShiftQuery:
        """Ensure query has minimum necessary information."""
        if not self.yuewen_1 and not self.yuewen_2:
            raise ValueError(
                "Query must have 粤文 subtitle 1, 粤文 subtitle 2, or both."
            )
        return self
