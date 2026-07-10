#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Prompts for reviewing standard Chinese using written Cantonese."""

from __future__ import annotations

from scinoephile.lang.zho.review import (
    GuidedReviewPromptZhoHans,
    GuidedReviewPromptZhoHant,
    PairwiseReviewPromptZhoHans,
    PairwiseReviewPromptZhoHant,
)

__all__ = [
    "ZhoYueGuidedReviewPromptZhoHans",
    "ZhoYueGuidedReviewPromptZhoHant",
    "ZhoYuePairwiseReviewPromptZhoHans",
    "ZhoYuePairwiseReviewPromptZhoHant",
]


ZhoYueGuidedReviewPromptZhoHant = GuidedReviewPromptZhoHant
"""Prompt for guided review of traditional Chinese using written Cantonese."""

ZhoYueGuidedReviewPromptZhoHans = GuidedReviewPromptZhoHans
"""Prompt for guided review of simplified Chinese using written Cantonese."""

ZhoYuePairwiseReviewPromptZhoHant = PairwiseReviewPromptZhoHant
"""Prompt for pairwise review of traditional Chinese using written Cantonese."""

ZhoYuePairwiseReviewPromptZhoHans = PairwiseReviewPromptZhoHans
"""Prompt for pairwise review of simplified Chinese using written Cantonese."""
