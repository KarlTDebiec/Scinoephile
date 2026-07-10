#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for English/written Cantonese translation prompts."""

from __future__ import annotations

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.eng.prompts import PromptEng
from scinoephile.llms.gap_translation import GapTranslationPrompt
from scinoephile.llms.guided_translation import GuidedTranslationPrompt
from scinoephile.llms.translation import TranslationPrompt

__all__ = [
    "EngYueTranslationPrompt",
    "EngYueGapTranslationPrompt",
    "EngYueGuidedTranslationPrompt",
]


EngYueTranslationPrompt = TranslationPrompt(
    language=Language.eng,
    schema_intro=PromptEng.schema_intro,
    few_shot_intro=PromptEng.few_shot_intro,
    few_shot_query_intro=PromptEng.few_shot_query_intro,
    few_shot_answer_intro=PromptEng.few_shot_answer_intro,
    answer_invalid_pre=PromptEng.answer_invalid_pre,
    answer_invalid_post=PromptEng.answer_invalid_post,
    difficulty_description=PromptEng.difficulty_description,
    few_shot_description=PromptEng.few_shot_description,
    verified_description=PromptEng.verified_description,
    test_case_invalid_pre=PromptEng.test_case_invalid_pre,
    test_case_invalid_post=PromptEng.test_case_invalid_post,
    base_system_prompt=dedent_and_compact("""
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
        """),
    input_pfx="yuewen_",
    input_desc_tpl="Written Cantonese subtitle {idx} to translate",
    output_pfx="eng_",
    output_desc_tpl=(
        "Generated English subtitle {idx} corresponding to written Cantonese "
        "subtitle {idx}"
    ),
)
"""Text for English translation from written Cantonese."""

EngYueGapTranslationPrompt = GapTranslationPrompt(
    language=Language.eng,
    schema_intro=PromptEng.schema_intro,
    few_shot_intro=PromptEng.few_shot_intro,
    few_shot_query_intro=PromptEng.few_shot_query_intro,
    few_shot_answer_intro=PromptEng.few_shot_answer_intro,
    answer_invalid_pre=PromptEng.answer_invalid_pre,
    answer_invalid_post=PromptEng.answer_invalid_post,
    difficulty_description=PromptEng.difficulty_description,
    few_shot_description=PromptEng.few_shot_description,
    verified_description=PromptEng.verified_description,
    test_case_invalid_pre=PromptEng.test_case_invalid_pre,
    test_case_invalid_post=PromptEng.test_case_invalid_post,
    base_system_prompt=dedent_and_compact("""
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
        """),
    src_1_pfx="eng_",
    src_1_desc_tpl=(
        "Existing English subtitle {idx}; missing entries require translation"
    ),
    src_2_pfx="yuewen_",
    src_2_desc_tpl="Written Cantonese subtitle {idx} corresponding to line {idx}",
    output_pfx="eng_",
    output_desc_tpl=(
        'English subtitle {idx} for a missing line, or "" if no translation is needed'
    ),
)
"""Text for English gap translation using written Cantonese."""

EngYueGuidedTranslationPrompt = GuidedTranslationPrompt(
    language=Language.eng,
    schema_intro=PromptEng.schema_intro,
    few_shot_intro=PromptEng.few_shot_intro,
    few_shot_query_intro=PromptEng.few_shot_query_intro,
    few_shot_answer_intro=PromptEng.few_shot_answer_intro,
    answer_invalid_pre=PromptEng.answer_invalid_pre,
    answer_invalid_post=PromptEng.answer_invalid_post,
    difficulty_description=PromptEng.difficulty_description,
    few_shot_description=PromptEng.few_shot_description,
    verified_description=PromptEng.verified_description,
    test_case_invalid_pre=PromptEng.test_case_invalid_pre,
    test_case_invalid_post=PromptEng.test_case_invalid_post,
    base_system_prompt=dedent_and_compact("""
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
        """),
    src_1_pfx="yuewen_",
    src_1_desc_tpl="Written Cantonese subtitle {idx} to translate",
    src_2_pfx="eng_reference_",
    src_2_desc_tpl="Original English reference subtitle {idx} from the same block",
    output_pfx="eng_",
    output_desc_tpl=(
        "Generated English subtitle {idx} corresponding to written Cantonese "
        "subtitle {idx}"
    ),
)
"""Text for guided translation of English from written Cantonese."""
