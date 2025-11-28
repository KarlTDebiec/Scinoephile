#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for 中文 OCR fusion."""

from __future__ import annotations

from abc import ABC

from pydantic import Field, model_validator

from scinoephile.core.abcs import Query


class ZhongwenFusionQuery(Query, ABC):
    """Query for 中文 OCR fusion."""

    lens: str = Field(..., description="Google Lens 提取的字幕文本")
    paddle: str = Field(..., description="PaddleOCR 提取的字幕文本")

    @model_validator(mode="after")
    def validate_query(self) -> ZhongwenFusionQuery:
        """Ensure query is internally valid."""
        if not self.lens:
            raise ValueError("缺少 Google Lens 的中文字幕文本。")
        if not self.paddle:
            raise ValueError("缺少 PaddleOCR 的中文字幕文本。")
        if self.lens == self.paddle:
            raise ValueError("Google Lens 与 PaddleOCR 的字幕文本不能完全相同。")
        return self
