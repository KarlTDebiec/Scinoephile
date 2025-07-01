#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Payload for merging Cantonese subtitles."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MergePayload(BaseModel):
    """Payload for merging Cantonese subtitles."""

    zhongwen: str = Field(..., description="中文 subtitle text")
    yuewen: list[str] = Field(..., description="粤文 subtitle text")
