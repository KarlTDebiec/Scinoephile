#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for 粤文 splitting."""

from __future__ import annotations

from pydantic import BaseModel, Field


class SplitQuery(BaseModel):
    """Query for 粤文 splitting."""

    one_zhongwen: str = Field(..., description="Known 中文 of text one.")
    one_yuewen_start: str = Field(..., description="Known 粤文 start of text one.")
    two_zhongwen: str = Field(..., description="Known 中文 of text two.")
    two_yuewen_end: str = Field(..., description="Known 粤文 end of text two.")
    yuewen_to_split: str = Field(
        ...,
        description="粤文 to be split, with start appended to 粤文 text one and end "
        "prepended to 粤文 text two.",
    )
