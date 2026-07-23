#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for English/standard Chinese translation prompts."""

from __future__ import annotations

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.eng.prompts import ENG_PROMPT_FIELDS
from scinoephile.llms.gap_translation import GapTranslationPrompt
from scinoephile.llms.guided_translation import GuidedTranslationPrompt
from scinoephile.llms.translation import TranslationPrompt

__all__ = [
    "EngZhoTranslationPrompt",
    "EngZhoGapTranslationPrompt",
    "EngZhoGuidedTranslationPrompt",
]


EngZhoTranslationPrompt = TranslationPrompt(
    language=Language.eng,
    **ENG_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        You are responsible for creating English subtitles from Chinese subtitles.

        Produce one English subtitle for each Chinese subtitle. Match the meaning,
        timing granularity, dramatic intent, and speaker intent of the Chinese. Use
        natural subtitle English rather than word-for-word phrasing. Preserve names,
        proper nouns, recurring terms, and subtitle markup when they are present and
        appropriate in the generated English subtitle.

        Output only the generated English subtitle text in each output item's text
        field. Do not include notes, explanations, labels, alternate translations,
        bracketed commentary, or any text outside the subtitle itself.
        """),
    subtitles="zho",
    subtitles_desc="Chinese subtitles to translate, in order.",
    outputs="eng",
    outputs_desc=(
        "Generated English subtitles corresponding to the Chinese subtitles, in order."
    ),
    subtitle_text_desc="Chinese subtitle text to translate.",
    output_text_desc="Generated English subtitle text.",
)
"""Text for English translation from Chinese."""

EngZhoGapTranslationPrompt = GapTranslationPrompt(
    language=Language.eng,
    **ENG_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        You are responsible for filling missing English subtitle lines using the
        corresponding Chinese subtitles as reference.

        Only provide an English translation for indexes absent from the existing
        English targets. Return exactly one output for every missing target index, and
        do not return outputs for indexes that already have English content. Translate
        missing lines into natural subtitle English that matches nearby English
        wording, register, dramatic intent, and speaker intent. Use the Chinese as the
        source of meaning, but keep style and terminology consistent with the existing
        English subtitles around the gap.

        Output only the generated English subtitle text for each missing target index.
        If a missing position should not produce an English subtitle, retain its
        indexed output item with an empty text value. Do not include notes,
        explanations, labels, alternate translations, bracketed commentary, or any
        text outside the subtitle itself.
        """),
    targets="eng",
    targets_desc="Existing English subtitles, indexed by Chinese position",
    guides="zho",
    guides_desc="Complete Chinese subtitles in index order",
    outputs="eng",
    outputs_desc="English translations for indexes absent from the existing targets",
    target_text_desc="Existing English subtitle text",
    guide_text_desc="Chinese guide subtitle text",
    output_text_desc=(
        "English translation for the missing target index, or an empty string if "
        "none is needed"
    ),
)
"""Text for English gap translation using Chinese."""

EngZhoGuidedTranslationPrompt = GuidedTranslationPrompt(
    language=Language.eng,
    **ENG_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        You are responsible for creating English subtitles from Chinese subtitles. You
        will also receive original English subtitles from the same scene as reference
        material.

        Produce one English subtitle for each Chinese subtitle. Match the meaning,
        timing granularity, dramatic intent, and speaker intent of the Chinese.
        Use the original English subtitles as the source of truth for character
        names, proper nouns, recurring terms, register, and canonical phrasing when
        that wording is compatible with the Chinese. Do not invent alternate names
        or translate names literally. When the Chinese differs from the original
        English, prioritize the Chinese meaning while preserving established names
        and terms from the English reference.

        Output only the generated English subtitle text in each output item's text
        field. Do not include notes, explanations, labels, alternate translations,
        bracketed commentary, or any text outside the subtitle itself. Preserve
        subtitle markup only when it is appropriate for the generated English
        subtitle.
        """),
    subtitles="zho",
    subtitles_desc="Chinese subtitles to translate, in order",
    guides="eng_reference",
    guides_desc="Original English reference subtitles from the same block, in order",
    outputs="eng",
    outputs_desc="Generated English subtitles corresponding to the input subtitles",
    subtitle_text_desc="Chinese subtitle to translate",
    guide_text_desc="Original English reference subtitle from the same block",
    output_text_desc="Generated English subtitle corresponding to a Chinese subtitle",
)
"""Text for guided translation of English from Chinese with English guidance."""
