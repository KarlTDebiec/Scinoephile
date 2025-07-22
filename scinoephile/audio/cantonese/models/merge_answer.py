#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for 粤文 merging."""

from __future__ import annotations

from pydantic import Field

from scinoephile.core.abcs import Answer


class MergeAnswer(Answer):
    """Answer for 粤文 merging."""

    yuewen_merged: str = Field(
        ..., description="Merged 粤文 text with spacing and punctuation."
    )
