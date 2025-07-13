#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for 粤文 merging."""

from __future__ import annotations

import json

from pydantic import BaseModel, Field


class MergeAnswer(BaseModel):
    """Answer for 粤文 merging."""

    yuewen_merged: str = Field(
        ..., description="Merged 中文 text with spacing and punctuation."
    )

    def __str__(self) -> str:
        """String representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)
