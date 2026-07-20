#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM prompts for English review."""

from __future__ import annotations

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.llms.guided_review import GuidedReviewPrompt
from scinoephile.llms.review import ReviewPrompt

from .prompts import ENG_PROMPT_FIELDS

__all__ = [
    "GuidedReviewPromptEng",
    "ReviewPromptEng",
]


GuidedReviewPromptEng = GuidedReviewPrompt(
    language=Language.eng,
    **ENG_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        You are responsible for the final review of English subtitles.
        You will also receive guide subtitles covering the same passage, possibly in
        another language and with a different number of subtitle cues.
        Use the guide to identify clear transcription, spelling, name, or continuity
        errors, but do not translate the guide or rewrite correct English to match it.
        Do not improve style, grammar, tone, or phrasing unless the target is clearly
        erroneous. Include a revision only when a target subtitle requires a change.
        Each revision must include the target's index, its full revised text, and a
        short English note. To delete a spurious target subtitle, use the single
        replacement character "�" as its revised text. If no revisions are needed,
        return an empty revisions list."""),
    targets="english",
    targets_desc="English target subtitles to review, in order.",
    guides="references",
    guides_desc="Reference subtitles for the same passage, in order.",
    revisions="revised_english",
    revisions_desc=(
        "Revised English target subtitles; include only targets that require revision."
    ),
    target_text_desc="English target subtitle text to review.",
    guide_text_desc="Reference subtitle text.",
    revision_text_desc=(
        'Full revised English target subtitle text, or "�" to delete the target.'
    ),
    note_desc="English note explaining the target subtitle revision.",
)
"""LLM correspondence text for guided review of English subtitles."""

ReviewPromptEng = ReviewPrompt(
    language=Language.eng,
    **ENG_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        You are responsible for proofreading English subtitles.
        Return a revision only for a subtitle that requires changes. Each revision must
        include the subtitle's index, its full revised text, and an English note
        describing the changes made. If no revisions are needed, return an empty
        revisions list.
        Make changes only when necessary to correct typographical errors.

        Do not add stylistic changes or improve phrasing.

        Do not change colloquialisms or dialect such as 'gonna' or 'wanna'.

        Do not change spelling from British to American English or vice versa.

        Do not remove subtitle markup such as italics ('{\\i1}' and '{\\i0}').

        Do not remove newlines ('\\n')."""),
    subtitles_desc="English subtitles to review, in order.",
    revisions_desc=(
        "Revised English subtitles; include only subtitles that require revision."
    ),
    subtitle_text_desc="English subtitle text to review.",
    revision_text_desc="Full revised English subtitle text.",
    note_desc="English note explaining the subtitle revision.",
)
"""LLM correspondence text for English review."""
