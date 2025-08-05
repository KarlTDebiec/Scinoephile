#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for 粤文 merging."""

from __future__ import annotations

from pydantic import Field, model_validator

from scinoephile.core.abcs import Query


class MergeQuery(Query):
    """Query for 粤文 merging."""

    zhongwen: str = Field(..., description="Known 中文 of subtitle.")
    yuewen_to_merge: list[str] = Field(..., description="粤文 of subtitle.")

    @model_validator(mode="after")
    def validate_query(self) -> MergeQuery:
        """Ensure query has minimum necessary information."""
        if not self.zhongwen:
            raise ValueError("Query must have 中文 subtitle.")
        if not self.yuewen_to_merge:
            raise ValueError("Query must have 粤文 subtitle to merge.")
        return self
