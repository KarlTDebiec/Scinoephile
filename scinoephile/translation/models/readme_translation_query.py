# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Query for translating README files."""

from __future__ import annotations

from pydantic import Field

from scinoephile.core.abcs import Query


class ReadmeTranslationQuery(Query):
    """Query for translating README files."""

    english_readme: str = Field(..., description="Current English README text.")
    chinese_readme: str = Field(
        ..., description="Previous README in the target language."
    )
    language: str = Field(..., description="Target language: 'zhongwen' or 'yuewen'.")
