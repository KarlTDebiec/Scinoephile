#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for 粤文 distribution."""

from __future__ import annotations

from pydantic import Field, model_validator

from scinoephile.core.abcs import Query


class DistributeQuery(Query):
    """Query for 粤文 distribution."""

    zhongwen_1: str = Field(..., description="Known 中文 of subtitle 1.")
    yuewen_1_start: str = Field(
        ..., description="Transcribed 粤文 start of subtitle 1."
    )
    zhongwen_2: str = Field(..., description="Known 中文 of subtitle 2.")
    yuewen_2_end: str = Field(..., description="Transcribed 粤文 end of subtitle 2.")
    yuewen_to_distribute: str = Field(
        ...,
        description="Transcribed 粤文 to distribute, with start appended to 粤文 "
        "subtitle 1 and end prepended to 粤文 subtitle 2.",
    )

    @model_validator(mode="after")
    def validate_query(self) -> DistributeQuery:
        """Ensure query has minimum necessary information."""
        if not self.zhongwen_1:
            raise ValueError("Query must have corresponding 中文 subtitle 1.")
        if not self.zhongwen_2:
            raise ValueError("Query must have corresponding 中文 subtitle 2.")
        if not self.yuewen_to_distribute:
            raise ValueError("Query must have 粤文 to distribute.")
        return self
