#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for English gapped translation using written Cantonese."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.eng.prompts import PromptEng
from scinoephile.llms.dual_n_minus_m_to_n import DualNMinusMToNPrompt

__all__ = ["EngGappedTranslationVsYuePrompt"]


class EngGappedTranslationVsYuePrompt(DualNMinusMToNPrompt, PromptEng):
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
