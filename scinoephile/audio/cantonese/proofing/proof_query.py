#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for 粤文 proofing."""

from __future__ import annotations

from pydantic import Field, model_validator

from scinoephile.core import ScinoephileError
from scinoephile.core.abcs import Query


class ProofQuery(Query):
    """Query for 粤文 proofing."""

    zhongwen: str = Field(..., description="Known 中文 text")
    yuewen: str = Field(..., description="Transcribed 粤文 text to proofread.")

    @model_validator(mode="after")
    def validate_query(self) -> ProofQuery:
        """Ensure query has minimum necessary information."""
        if not self.zhongwen:
            raise ScinoephileError("Query must have corresponding 中文 text.")
        if not self.yuewen:
            raise ScinoephileError("Query must have 粤文 text.")
        return self
