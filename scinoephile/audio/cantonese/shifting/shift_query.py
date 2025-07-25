#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for 粤文 shifting."""

from __future__ import annotations

from pydantic import Field, model_validator

from scinoephile.core.abcs import Query


class ShiftQuery(Query):
    """Query for 粤文 shifting."""

    one_zhongwen: str = Field(..., description="Known 中文 of text one.")
    one_yuewen: str = Field(..., description="Original 粤文 of text one.")
    two_zhongwen: str = Field(..., description="Known 中文 of text two.")
    two_yuewen: str = Field(..., description="Original 粤文 of text two.")

    @model_validator(mode="after")
    def validate_query(self) -> ShiftQuery:
        """Ensure query has minimum necessary information."""
        if not self.one_yuewen and not self.two_yuewen:
            raise ValueError("Query must have 粤文 text one, two, or both.")
        return self
