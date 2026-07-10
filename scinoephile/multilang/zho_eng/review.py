#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Prompts for reviewing standard Chinese using English."""

from __future__ import annotations

from scinoephile.core import Language
from scinoephile.lang.zho.review import (
    GuidedReviewPromptZhoHans,
    GuidedReviewPromptZhoHant,
    PairwiseReviewPromptZhoHans,
    PairwiseReviewPromptZhoHant,
)
from scinoephile.llms.guided_review import GuidedReviewPrompt
from scinoephile.llms.pairwise_review import PairwiseReviewPrompt
from scinoephile.llms.prompt_definition import define_prompt

__all__ = [
    "ZhoEngGuidedReviewPromptZhoHans",
    "ZhoEngGuidedReviewPromptZhoHant",
    "ZhoEngPairwiseReviewPromptZhoHans",
    "ZhoEngPairwiseReviewPromptZhoHant",
]


@define_prompt(
    GuidedReviewPrompt,
    Language.zho_hant,
    parent=GuidedReviewPromptZhoHant,
)
class ZhoEngGuidedReviewPromptZhoHant:
    """Prompt for guided review of traditional Chinese using English."""


@define_prompt(
    GuidedReviewPrompt,
    Language.zho_hans,
    parent=GuidedReviewPromptZhoHans,
)
class ZhoEngGuidedReviewPromptZhoHans:
    """Prompt for guided review of simplified Chinese using English."""


@define_prompt(
    PairwiseReviewPrompt,
    Language.zho_hant,
    parent=PairwiseReviewPromptZhoHant,
)
class ZhoEngPairwiseReviewPromptZhoHant:
    """Prompt for pairwise review of traditional Chinese using English."""


@define_prompt(
    PairwiseReviewPrompt,
    Language.zho_hans,
    parent=PairwiseReviewPromptZhoHans,
)
class ZhoEngPairwiseReviewPromptZhoHans:
    """Prompt for pairwise review of simplified Chinese using English."""
