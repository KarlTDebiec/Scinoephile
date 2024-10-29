#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Subtitle series response."""
from __future__ import annotations

from pydantic import BaseModel

from scinoephile.core.openai.subtitle_group_response import SubtitleGroupResponse


class SubtitleSeriesResponse(BaseModel):
    explanation: str
    synchronization: list[SubtitleGroupResponse]
