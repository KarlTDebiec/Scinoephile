#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for 粤文 distribution."""

from __future__ import annotations

from pydantic import Field, model_validator

from scinoephile.core import ScinoephileError
from scinoephile.core.abcs import Query


class DistributeQuery(Query):
    """Query for 粤文 distribution."""

    one_zhongwen: str = Field(..., description="Known 中文 of text one.")
    one_yuewen_start: str = Field(..., description="Known 粤文 start of text one.")
    two_zhongwen: str = Field(..., description="Known 中文 of text two.")
    two_yuewen_end: str = Field(..., description="Known 粤文 end of text two.")
    yuewen_to_distribute: str = Field(
        ...,
        description="粤文 to distribute, with start appended to 粤文 text one and end "
        "prepended to 粤文 text two.",
    )

    @model_validator(mode="after")
    def validate_query(self) -> DistributeQuery:
        """Ensure query has minimum necessary information."""
        if not self.one_zhongwen:
            raise ScinoephileError("Query must have corresponding 中文 text one.")
        if not self.two_zhongwen:
            raise ScinoephileError("Query must have corresponding 中文 text two.")
        if not self.yuewen_to_distribute:
            raise ScinoephileError("Query must have 粤文 text.")
        return self
