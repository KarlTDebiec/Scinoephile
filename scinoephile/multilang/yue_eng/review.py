#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Prompts for reviewing written Cantonese using English."""

from __future__ import annotations

from scinoephile.core import Language
from scinoephile.lang.yue.review import (
    GuidedReviewPromptYueHans,
    GuidedReviewPromptYueHant,
    PairwiseReviewPromptYueHans,
    PairwiseReviewPromptYueHant,
)
from scinoephile.llms.guided_review import GuidedReviewPrompt
from scinoephile.llms.pairwise_review import PairwiseReviewPrompt
from scinoephile.llms.prompt_definition import define_prompt

__all__ = [
    "YueEngGuidedReviewPromptYueHans",
    "YueEngGuidedReviewPromptYueHant",
    "YueEngPairwiseReviewPromptYueHans",
    "YueEngPairwiseReviewPromptYueHant",
]


@define_prompt(
    GuidedReviewPrompt,
    Language.yue_hant,
    parent=GuidedReviewPromptYueHant,
)
class YueEngGuidedReviewPromptYueHant:
    """Prompt for guided review of traditional written Cantonese using English."""


@define_prompt(
    GuidedReviewPrompt,
    Language.yue_hans,
    parent=GuidedReviewPromptYueHans,
)
class YueEngGuidedReviewPromptYueHans:
    """Prompt for guided review of simplified written Cantonese using English."""


@define_prompt(
    PairwiseReviewPrompt,
    Language.yue_hant,
    parent=PairwiseReviewPromptYueHant,
)
class YueEngPairwiseReviewPromptYueHant:
    """Prompt for pairwise review of traditional written Cantonese using English."""


@define_prompt(
    PairwiseReviewPrompt,
    Language.yue_hans,
    parent=PairwiseReviewPromptYueHans,
)
class YueEngPairwiseReviewPromptYueHans:
    """Prompt for pairwise review of simplified written Cantonese using English."""
