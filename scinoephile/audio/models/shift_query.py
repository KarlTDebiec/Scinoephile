# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for shifting 粤文 text between adjacent subtitles."""

from __future__ import annotations

import json

from pydantic import BaseModel, Field


class ShiftQuery(BaseModel):
    """Query for shifting 粤文 text between adjacent subtitles."""

    one_zhongwen: str = Field(..., description="Known 中文 of subtitle one.")
    one_yuewen: str = Field(..., description="Original 粤文 of subtitle one.")
    two_zhongwen: str = Field(..., description="Known 中文 of subtitle two.")
    two_yuewen: str = Field(..., description="Original 粤文 of subtitle two.")

    def __str__(self) -> str:  # noqa: D401
        """Return string representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)
