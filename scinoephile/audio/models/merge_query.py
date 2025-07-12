#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for 粤文 merging."""

from __future__ import annotations

import json

from pydantic import BaseModel, Field


class MergeQuery(BaseModel):
    """Query for 粤文 merging."""

    zhongwen: str = Field(
        ..., description="Known 中文 text including punctuation and spacing."
    )
    yuewen_to_merge: list[str] = Field(
        ..., description="Known 粤文 texts to merge with punctuation and spacing."
    )

    def __str__(self):
        """String representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)
