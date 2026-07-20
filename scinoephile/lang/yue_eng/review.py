#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Prompts for reviewing written Cantonese using English."""

from __future__ import annotations

from scinoephile.lang.yue.review import (
    GuidedReviewPromptYueHans,
    GuidedReviewPromptYueHant,
)

__all__ = [
    "YueEngGuidedReviewPromptYueHans",
    "YueEngGuidedReviewPromptYueHant",
]


YueEngGuidedReviewPromptYueHant = GuidedReviewPromptYueHant
"""Prompt for guided review of traditional written Cantonese using English."""

YueEngGuidedReviewPromptYueHans = GuidedReviewPromptYueHans
"""Prompt for guided review of simplified written Cantonese using English."""
