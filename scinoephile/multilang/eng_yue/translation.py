#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for English/written Cantonese translation prompts."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.eng.prompts import PromptEng
from scinoephile.llms.dual_n_minus_m_to_n import DualNMinusMToNPrompt
from scinoephile.llms.dual_n_to_m import DualNToMPrompt

__all__ = [
    "EngYueTranslationPrompt",
    "EngYueGappedTranslationPrompt",
    "EngYueGuidedTranslationPrompt",
]


class EngYueTranslationPrompt(DualNToMPrompt, PromptEng):
    """Text for English translation from written Cantonese."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        You are responsible for creating English subtitles from written Cantonese
        subtitles.

        Produce one English subtitle for each written Cantonese subtitle. Match the
        meaning, timing granularity, dramatic intent, and speaker intent of the
        written Cantonese. Use natural subtitle English rather than word-for-word
        phrasing. Preserve names, proper nouns, recurring terms, and subtitle markup
        when they are present and appropriate in the generated English subtitle.

        Output only the generated English subtitle text in each answer field. Do not
        include notes, explanations, labels, alternate translations, bracketed
        commentary, or any text outside the subtitle itself.
        """)
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "yuewen_"
    """Prefix for written Cantonese source fields in query."""

    src_1_desc_tpl: ClassVar[str] = "Written Cantonese subtitle {idx} to translate"
    """Description template for written Cantonese source fields in query."""

    src_2_pfx: ClassVar[str] = "context_"
    """Prefix for optional context fields in query."""

    src_2_desc_tpl: ClassVar[str] = "Additional context subtitle {idx}"
    """Description template for optional context fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "eng_"
    """Prefix for generated English output fields in answer."""

    output_desc_tpl: ClassVar[str] = (
        "Generated English subtitle {idx} corresponding to written Cantonese "
        "subtitle {idx}"
    )
    """Description template for generated English output fields in answer."""


class EngYueGappedTranslationPrompt(DualNMinusMToNPrompt, PromptEng):
    """Text for English gapped translation using written Cantonese."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        You are responsible for filling missing English subtitle lines using the
        corresponding written Cantonese subtitles as reference.

        Only provide an English translation when the existing English subtitle line is
        missing. If a line already has English content, do not revise it; output an
        empty string for that line. Translate missing lines into natural subtitle
        English that matches nearby English wording, register, dramatic intent, and
        speaker intent. Use the written Cantonese as the source of meaning, but keep
        style and terminology consistent with the existing English subtitles around
        the gap.

        Output only the generated English subtitle text in each answer field. If no
        translation is needed for a line, output an empty string. Do not include notes,
        explanations, labels, alternate translations, bracketed commentary, or any text
        outside the subtitle itself.
        """)
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "eng_"
    """Prefix for existing English fields in query."""

    src_1_desc_tpl: ClassVar[str] = (
        "Existing English subtitle {idx}; missing entries require translation"
    )
    """Description template for existing English fields in query."""

    src_2_pfx: ClassVar[str] = "yuewen_"
    """Prefix for written Cantonese reference fields in query."""

    src_2_desc_tpl: ClassVar[str] = (
        "Written Cantonese subtitle {idx} corresponding to line {idx}"
    )
    """Description template for written Cantonese reference fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "eng_"
    """Prefix for generated English output fields in answer."""

    output_desc_tpl: ClassVar[str] = (
        'English subtitle {idx} for a missing line, or "" if no translation is needed'
    )
    """Description template for generated English output fields in answer."""


class EngYueGuidedTranslationPrompt(DualNToMPrompt, PromptEng):
    """Text for guided translation of English from written Cantonese."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        You are responsible for creating English subtitles from written Cantonese
        subtitles. You will also receive original English subtitles from the same
        scene as reference material.

        Produce one English subtitle for each written Cantonese subtitle. Match the
        meaning, timing granularity, dramatic intent, and speaker intent of the
        written Cantonese. Use the original English subtitles as the source of truth
        for character names, proper nouns, recurring terms, register, and canonical
        phrasing when that wording is compatible with the written Cantonese. Do not
        invent alternate names or translate names literally. When the written
        Cantonese differs from the original English, prioritize the written Cantonese
        meaning while preserving established names and terms from the English
        reference.

        Output only the generated English subtitle text in each answer field. Do not
        include notes, explanations, labels, alternate translations, bracketed
        commentary, or any text outside the subtitle itself. Preserve subtitle markup
        only when it is appropriate for the generated English subtitle.
        """)
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "yuewen_"
    """Prefix for written Cantonese source fields in query."""

    src_1_desc_tpl: ClassVar[str] = "Written Cantonese subtitle {idx} to translate"
    """Description template for written Cantonese source fields in query."""

    src_2_pfx: ClassVar[str] = "eng_reference_"
    """Prefix for English reference fields in query."""

    src_2_desc_tpl: ClassVar[str] = (
        "Original English reference subtitle {idx} from the same block"
    )
    """Description template for English reference fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "eng_"
    """Prefix for generated English output fields in answer."""

    output_desc_tpl: ClassVar[str] = (
        "Generated English subtitle {idx} corresponding to written Cantonese "
        "subtitle {idx}"
    )
    """Description template for generated English output fields in answer."""
