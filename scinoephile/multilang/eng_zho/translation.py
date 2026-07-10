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

        Output only the generated English subtitle text in each answer field. Do not
        include notes, explanations, labels, alternate translations, bracketed
        commentary, or any text outside the subtitle itself.
        """),
    input_pfx="zho_",
    input_desc_tpl="Chinese subtitle {idx} to translate",
    output_pfx="eng_",
    output_desc_tpl=(
        "Generated English subtitle {idx} corresponding to Chinese subtitle {idx}"
    ),
)
"""Text for English translation from Chinese."""

EngZhoGapTranslationPrompt = GapTranslationPrompt(
    language=Language.eng,
    **ENG_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        You are responsible for filling missing English subtitle lines using the
        corresponding Chinese subtitles as reference.

        Only provide an English translation when the existing English subtitle line is
        missing. If a line already has English content, do not revise it; output an
        empty string for that line. Translate missing lines into natural subtitle
        English that matches nearby English wording, register, dramatic intent, and
        speaker intent. Use the Chinese as the source of meaning, but keep style and
        terminology consistent with the existing English subtitles around the gap.

        Output only the generated English subtitle text in each answer field. If no
        translation is needed for a line, output an empty string. Do not include notes,
        explanations, labels, alternate translations, bracketed commentary, or any text
        outside the subtitle itself.
        """),
    src_1_pfx="eng_",
    src_1_desc_tpl=(
        "Existing English subtitle {idx}; missing entries require translation"
    ),
    src_2_pfx="zho_",
    src_2_desc_tpl="Chinese subtitle {idx} corresponding to line {idx}",
    output_pfx="eng_",
    output_desc_tpl=(
        'English subtitle {idx} for a missing line, or "" if no translation is needed'
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

        Output only the generated English subtitle text in each answer field. Do not
        include notes, explanations, labels, alternate translations, bracketed
        commentary, or any text outside the subtitle itself. Preserve subtitle markup
        only when it is appropriate for the generated English subtitle.
        """),
    src_1_pfx="zho_",
    src_1_desc_tpl="Chinese subtitle {idx} to translate",
    src_2_pfx="eng_reference_",
    src_2_desc_tpl="Original English reference subtitle {idx} from the same block",
    output_pfx="eng_",
    output_desc_tpl=(
        "Generated English subtitle {idx} corresponding to Chinese subtitle {idx}"
    ),
)
"""Text for guided translation of English from Chinese with English guidance."""
