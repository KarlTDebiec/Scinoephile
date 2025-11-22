#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for 中文 OCR fusion."""

from __future__ import annotations

from pydantic import Field, model_validator

from scinoephile.core.abcs import Answer


class ZhongwenFusionAnswer(Answer):
    """Answer for 中文 OCR fusion."""

    ronghe: str = Field(..., description="融合后的字幕文本")
    beizhu: str = Field(..., description="对所做更正的说明")

    @model_validator(mode="after")
    def validate_answer(self) -> ZhongwenFusionAnswer:
        """Ensure answer is internally valid."""
        if not self.ronghe:
            raise ValueError("融合后的字幕文本不能为空。")
        if not self.beizhu:
            raise ValueError("更正说明不能为空。")
        return self
