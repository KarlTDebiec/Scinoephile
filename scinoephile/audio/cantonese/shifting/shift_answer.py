#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for 粤文 shifting."""

from __future__ import annotations

from pydantic import Field

from scinoephile.core.abcs import Answer


class ShiftAnswer(Answer):
    """Answer for 粤文 shifting."""

    yuewen_1_shifted: str = Field("", description="Shifted 粤文 of subtitle 1.")
    yuewen_2_shifted: str = Field("", description="Shifted 粤文 of subtitle 2.")
