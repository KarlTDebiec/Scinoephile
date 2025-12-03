#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for 粤文 proofing."""

from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from scinoephile.core.abcs import Query


class ProofingQuery(Query):
    """Query for 粤文 proofing."""

    zhongwen: str = Field(..., description="Known 中文 of subtitle。")
    yuewen: str = Field(..., description="Transcribed 粤文 of subtitle to proofread.")

    @model_validator(mode="after")
    def validate_query(self) -> Self:
        """Ensure query is internally valid."""
        if not self.zhongwen:
            raise ValueError("Query must have 中文 subtitle.")
        if not self.yuewen:
            raise ValueError("Query must have 粤文 subtitle to proofread.")
        return self
