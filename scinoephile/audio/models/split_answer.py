#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for 粤文 splitting."""

from __future__ import annotations

import json

from pydantic import BaseModel, Field


class SplitAnswer(BaseModel):
    """Answer for 粤文 splitting."""

    one_yuewen_to_append: str = Field(
        ..., description="粤文 to append to 粤文 text one."
    )
    two_yuewen_to_prepend: str = Field(
        ..., description="粤文 to prepend to 粤文 text two."
    )

    def __str__(self):
        """String representation."""
        return json.dumps(self.model_dump(), indent=2, ensure_ascii=False)
