#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for README translation."""

from __future__ import annotations

from typing import Literal

from pydantic import Field

from scinoephile.core.abcs import Query


class ReadmeTranslationQuery(Query):
    """Query for README translation."""

    updated_english: str = Field(..., description="Updated English README.")
    outdated_chinese: str = Field(..., description="Out-of-date Chinese README.")
    language: Literal["zhongwen", "yuewen"] = Field(
        ..., description="Target language: 'zhongwen' or 'yuewen'."
    )
