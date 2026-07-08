#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test-data-specific prompt classes."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.multilang.eng_zho.translation import (
    EngZhoGuidedTranslationPrompt,
)

__all__ = ["EngZhoOfYueGuidedTranslationPrompt"]


class EngZhoOfYueGuidedTranslationPrompt(EngZhoGuidedTranslationPrompt):
    """Text for guided English translation from Chinese subtitles of Yue source."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        You are responsible for creating English subtitles from Chinese subtitles for
        Cantonese/Yue audio. You will also receive original English subtitles from the
        same scene as reference material.

        Produce one English subtitle for each Chinese subtitle. Match the meaning,
        timing granularity, dramatic intent, and speaker intent of the Cantonese
        source. Use the original English subtitles as the source of truth for character
        names, proper nouns, recurring terms, register, and canonical phrasing when
        that wording is compatible with the Cantonese source. Do not invent alternate
        names or translate names literally. When the Cantonese source differs from the
        original English, prioritize the Cantonese source meaning while preserving
        established names and terms from the English reference.

        Output only the generated English subtitle text in each answer field. Do not
        include notes, explanations, labels, alternate translations, bracketed
        commentary, or any text outside the subtitle itself. Preserve subtitle markup
        only when it is appropriate for the generated English subtitle.
        """)
    """Base system prompt."""

    # Query fields
    src_1_desc_tpl: ClassVar[str] = (
        "Chinese subtitle {idx} of Cantonese/Yue source to translate"
    )
    """Description template for Chinese source fields in query."""

    # Answer fields
    output_desc_tpl: ClassVar[str] = (
        "Generated English subtitle {idx} corresponding to Chinese subtitle {idx} "
        "of Cantonese/Yue source"
    )
    """Description template for generated English output fields in answer."""
