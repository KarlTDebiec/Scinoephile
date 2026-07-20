#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Prompts for reviewing standard Chinese using English."""

from __future__ import annotations

from scinoephile.lang.zho.review import (
    GuidedReviewPromptZhoHans,
    GuidedReviewPromptZhoHant,
)

__all__ = [
    "ZhoEngGuidedReviewPromptZhoHans",
    "ZhoEngGuidedReviewPromptZhoHant",
]


ZhoEngGuidedReviewPromptZhoHant = GuidedReviewPromptZhoHant
"""Prompt for guided review of traditional Chinese using English."""

ZhoEngGuidedReviewPromptZhoHans = GuidedReviewPromptZhoHans
"""Prompt for guided review of simplified Chinese using English."""
