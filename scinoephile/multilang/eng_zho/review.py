#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Prompts for reviewing English using standard Chinese."""

from __future__ import annotations

from scinoephile.core import Language
from scinoephile.lang.eng.review import GuidedReviewPromptEng, PairwiseReviewPromptEng
from scinoephile.llms.guided_review import GuidedReviewPrompt
from scinoephile.llms.pairwise_review import PairwiseReviewPrompt
from scinoephile.llms.prompt_definition import define_prompt

__all__ = [
    "EngZhoGuidedReviewPrompt",
    "EngZhoPairwiseReviewPrompt",
]


@define_prompt(GuidedReviewPrompt, Language.eng, parent=GuidedReviewPromptEng)
class EngZhoGuidedReviewPrompt:
    """Prompt for guided review of English using standard Chinese."""


@define_prompt(PairwiseReviewPrompt, Language.eng, parent=PairwiseReviewPromptEng)
class EngZhoPairwiseReviewPrompt:
    """Prompt for pairwise review of English using standard Chinese."""
