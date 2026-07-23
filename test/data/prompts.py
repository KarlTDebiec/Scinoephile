#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Test-data-specific prompts."""

from __future__ import annotations

from dataclasses import replace

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.eng_zho.translation import (
    EngZhoGuidedTranslationPrompt,
)

__all__ = ["EngZhoYueGuidedTranslationPrompt"]

EngZhoYueGuidedTranslationPrompt = replace(
    EngZhoGuidedTranslationPrompt,
    base_system_prompt=dedent_and_compact("""
            You are responsible for creating English subtitles from Chinese subtitles
            for Cantonese/Yue audio. You will also receive original English subtitles
            from the same scene as reference material.

            Produce one English subtitle for each Chinese subtitle. Match the meaning,
            timing granularity, dramatic intent, and speaker intent of the Cantonese
            source. Use the original English subtitles as the source of truth for
            character names, proper nouns, recurring terms, register, and canonical
            phrasing when that wording is compatible with the Cantonese source. Do not
            invent alternate names or translate names literally. When the Cantonese
            source differs from the original English, prioritize the Cantonese source
            meaning while preserving established names and terms from the English
            reference.

            Output only the generated English subtitle text in each output item's text
            field. Do not include notes, explanations, labels, alternate translations,
            bracketed commentary, or any text outside the subtitle itself. Preserve
            subtitle markup only when it is appropriate for the generated English
            subtitle.
            """),
    subtitle_text_desc="Chinese subtitle of Cantonese/Yue source to translate",
    output_text_desc=(
        "Generated English subtitle corresponding to a Chinese subtitle of "
        "Cantonese/Yue source"
    ),
)
"""Text for guided English translation from Chinese subtitles of Yue source."""
