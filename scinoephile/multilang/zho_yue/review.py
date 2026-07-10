#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Prompts for reviewing standard Chinese using written Cantonese."""

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
    "ZhoYueGuidedReviewPromptZhoHans",
    "ZhoYueGuidedReviewPromptZhoHant",
    "ZhoYuePairwiseReviewPromptZhoHans",
    "ZhoYuePairwiseReviewPromptZhoHant",
]


@define_prompt(
    GuidedReviewPrompt,
    Language.zho_hant,
    parent=GuidedReviewPromptZhoHant,
)
class ZhoYueGuidedReviewPromptZhoHant:
    """Prompt for guided review of traditional Chinese using written Cantonese."""


@define_prompt(
    GuidedReviewPrompt,
    Language.zho_hans,
    parent=GuidedReviewPromptZhoHans,
)
class ZhoYueGuidedReviewPromptZhoHans:
    """Prompt for guided review of simplified Chinese using written Cantonese."""


@define_prompt(
    PairwiseReviewPrompt,
    Language.zho_hant,
    parent=PairwiseReviewPromptZhoHant,
)
class ZhoYuePairwiseReviewPromptZhoHant:
    """Prompt for pairwise review of traditional Chinese using written Cantonese."""


@define_prompt(
    PairwiseReviewPrompt,
    Language.zho_hans,
    parent=PairwiseReviewPromptZhoHans,
)
class ZhoYuePairwiseReviewPromptZhoHans:
    """Prompt for pairwise review of simplified Chinese using written Cantonese."""
