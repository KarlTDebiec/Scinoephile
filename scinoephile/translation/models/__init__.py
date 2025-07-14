# Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
# and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Models for translation tasks."""

from __future__ import annotations

from scinoephile.translation.models.readme_translation_answer import (
    ReadmeTranslationAnswer,
)
from scinoephile.translation.models.readme_translation_query import (
    ReadmeTranslationQuery,
)

__all__ = [
    "ReadmeTranslationQuery",
    "ReadmeTranslationAnswer",
]
