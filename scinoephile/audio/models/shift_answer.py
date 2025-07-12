# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for shifting 粤文 text between adjacent subtitles."""

from __future__ import annotations

import json

from pydantic import BaseModel, Field


class ShiftAnswer(BaseModel):
    """Answer for shifting 粤文 text between adjacent subtitles."""

    one_yuewen_shifted: str = Field(
        ..., description="粤文 of subtitle one after shifting text from subtitle two."
    )
    two_yuewen_shifted: str = Field(
        ..., description="粤文 of subtitle two after shifting text to subtitle one."
    )

    def __str__(self) -> str:  # noqa: D401
        """Return string representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)
