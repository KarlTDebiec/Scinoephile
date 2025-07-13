#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for 粤文 shifting."""

from __future__ import annotations

import json

from pydantic import BaseModel, Field


class ShiftQuery(BaseModel):
    """Query for 粤文 shifting."""

    one_zhongwen: str = Field(..., description="Known 中文 of text one.")
    one_yuewen: str = Field(..., description="Original 粤文 of text one.")
    two_zhongwen: str = Field(..., description="Known 中文 of text two.")
    two_yuewen: str = Field(..., description="Original 粤文 of text two.")

    def __str__(self) -> str:
        """String representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)
