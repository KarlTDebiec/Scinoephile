#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Answer for README translation."""

from __future__ import annotations

from pydantic import Field

from scinoephile.core.abcs import Answer


class ReadmeTranslationAnswer(Answer):
    """Answer for README translation."""

    updated_chinese: str = Field(..., description="Updated Chinese README.")
