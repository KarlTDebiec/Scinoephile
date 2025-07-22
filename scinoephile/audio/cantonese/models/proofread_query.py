#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for 粤文 proofreading."""

from __future__ import annotations

from pydantic import Field

from scinoephile.core.abcs import Query


class ProofreadQuery(Query):
    """Query for 粤文 proofreading."""

    zhongwen: str = Field(..., description="Known 中文 text")
    yuewen: str = Field(..., description="Transcribed 粤文 text to proofread.")
