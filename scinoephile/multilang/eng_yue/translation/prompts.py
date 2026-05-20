#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for English translation from written Cantonese."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.eng.prompts import PromptEng
from scinoephile.llms.dual_n_to_m import DualNToMPrompt

__all__ = ["EngTranslationVsYuePrompt"]


class EngTranslationVsYuePrompt(DualNToMPrompt, PromptEng):
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
