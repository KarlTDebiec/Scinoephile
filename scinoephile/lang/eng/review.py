#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM prompts for English review."""

from __future__ import annotations

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.eng.prompts import PromptEng
from scinoephile.llms.guided_review import GuidedReviewPrompt
from scinoephile.llms.pairwise_review import PairwiseReviewPrompt
from scinoephile.llms.review import ReviewPrompt

__all__ = [
    "GuidedReviewPromptEng",
    "PairwiseReviewPromptEng",
    "ReviewPromptEng",
]


GuidedReviewPromptEng = GuidedReviewPrompt(
    language=Language.eng,
    **PromptEng.localization_kwargs,
    base_system_prompt=dedent_and_compact("""
        You are responsible for the final review of English subtitles.
        You will also receive guide subtitles covering the same passage, possibly in
        another language and with a different number of subtitle cues.
        Use the guide to identify clear transcription, spelling, name, or continuity
        errors, but do not translate the guide or rewrite correct English to match it.
        Do not improve style, grammar, tone, or phrasing unless the target is clearly
        erroneous. For each target subtitle, return the full revision and a short note
        only when a change is necessary. Otherwise return empty strings."""),
    target_pfx="english_",
    target_desc_tpl="English target subtitle {idx}",
    guide_pfx="reference_",
    guide_desc_tpl="Reference subtitle {idx}",
    output_pfx="revised_english_",
)
"""LLM correspondence text for guided review of English subtitles."""

PairwiseReviewPromptEng = PairwiseReviewPrompt(
    language=Language.eng,
    **PromptEng.localization_kwargs,
    base_system_prompt=dedent_and_compact("""
        Review one English subtitle against one corresponding reference subtitle,
        which may be in another language. Correct only clear transcription, spelling,
        or name errors supported by the reference. Do not translate the reference or
        rewrite correct English to mirror its wording. If a revision is necessary,
        return the full revised English subtitle and a short note. If no revision is
        necessary, return empty strings. Return "�" only when the English subtitle has
        no corresponding content and should be removed."""),
    target="english",
    target_desc="English subtitle to review",
    reference="reference",
    reference_desc="Corresponding reference subtitle",
    output="revised_english",
)
"""LLM correspondence text for pairwise review of English subtitles."""

ReviewPromptEng = ReviewPrompt(
    language=Language.eng,
    **PromptEng.localization_kwargs,
    base_system_prompt=dedent_and_compact("""
        You are responsible for proofreading English subtitles.
        For each subtitle, you are to provide revised subtitle only if revisions are
        necessary.
        If revisions are needed, return the full revised subtitle, and a note describing
        the changes made.
        If no revisions are needed, return an empty string for the revised subtitle and
        its note.
        Make changes only when necessary to correct typographical errors.

        Do not add stylistic changes or improve phrasing.

        Do not change colloquialisms or dialect such as 'gonna' or 'wanna'.

        Do not change spelling from British to American English or vice versa.

        Do not remove subtitle markup such as italics ('{\\i1}' and '{\\i0}').

        Do not remove newlines ('\\n')."""),
    input_pfx="subtitle_",
    input_desc_tpl="Subtitle {idx}",
    output_pfx="revised_",
    output_desc_tpl=(
        "Subtitle {idx} revised, or an empty string if no revision is necessary."
    ),
    note_desc_tpl=(
        "Note concerning revisions to subtitle {idx}, or an empty string if no "
        "revision is necessary."
    ),
    output_unmodified_err_tpl=(
        "Answer's revised text {idx} is not modified relative to query's text {idx}, "
        "if no revision is needed an empty string must be provided."
    ),
    note_missing_err_tpl=(
        "Answer's text {idx} is modified relative to query's text {idx}, but no note "
        "is provided, if revision is needed a note must be provided."
    ),
    output_missing_err_tpl=(
        "Answer's text {idx} is not modified relative to query's text {idx}, but a "
        "note is provided, if no revisions are needed an empty string must be provided."
    ),
)
"""LLM correspondence text for English review."""
