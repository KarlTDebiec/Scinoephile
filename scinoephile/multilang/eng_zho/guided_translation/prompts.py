#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for guided translation of English from Chinese with English guidance."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.eng.prompts import PromptEng
from scinoephile.llms.dual_block_cardinality import DualBlockCardinalityPrompt

__all__ = ["EngVsZhoGuidedTranslationPrompt"]


class EngVsZhoGuidedTranslationPrompt(DualBlockCardinalityPrompt, PromptEng):
    """Text for guided translation of English from Chinese with English guidance."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        You are responsible for creating English subtitles from Chinese subtitles.
        You will also receive original English subtitles from the same scene as
        reference material.

        Produce one English subtitle for each Chinese subtitle. Match the meaning,
        timing granularity, dramatic intent, and speaker intent of the Chinese.
        Use the original English subtitles for guidance on character names, proper
        nouns, recurring terms, register, and canonical phrasing when that wording is
        compatible with the Chinese. When the Chinese differs from the original
        English, prioritize the Chinese.

        Output only the generated English subtitle text in each answer field. Do not
        include notes, explanations, labels, alternate translations, bracketed
        commentary, or any text outside the subtitle itself. Preserve subtitle markup
        only when it is appropriate for the generated English subtitle.
        """)
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "zho_"
    """Prefix for Chinese source fields in query."""

    src_1_desc_tpl: ClassVar[str] = "Chinese subtitle {idx} to translate"
    """Description template for Chinese source fields in query."""

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
        "Generated English subtitle {idx} corresponding to Chinese subtitle {idx}"
    )
    """Description template for generated English output fields in answer."""
