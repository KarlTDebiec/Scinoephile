#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English translation from Cantonese with English guidance."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import OperationSpec, TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    ENG_FROM_YUE_TRANSLATION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_block_cardinality import (
    DualBlockCardinalityManager,
    DualBlockCardinalityProcessor,
)
from scinoephile.llms.providers.registry import get_default_provider

from .prompts import EngVsYueTranslationPrompt

__all__ = [
    "ENG_YUE_TRANSLATION_OPERATION_SPEC",
    "EngFromYueTranslationProcessKwargs",
    "EngFromYueTranslationProcessorKwargs",
    "EngVsYueTranslationPrompt",
    "get_eng_translated_vs_yue",
    "get_eng_vs_yue_translator",
]

ENG_YUE_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="eng-yue-translation",
    test_case_table_name="test_cases__eng_yue__translation",
    manager_cls=DualBlockCardinalityManager,
    prompt_cls=EngVsYueTranslationPrompt,
)
"""Operation specification for English translation from Cantonese."""


class EngFromYueTranslationProcessKwargs(TypedDict, total=False):
    """Keyword arguments for DualBlockCardinalityProcessor.process."""

    stop_at_idx: int | None
    """Subtitle block index at which to stop processing, inclusive."""


class EngFromYueTranslationProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for DualBlockCardinalityProcessor initialization."""

    test_case_path: Path | None
    """Path where encountered test cases are persisted."""
    auto_verify: bool
    """Whether generated test cases should be marked verified automatically."""


def get_eng_translated_vs_yue(
    yue: Series,
    eng: Series,
    translator: DualBlockCardinalityProcessor | None = None,
    **kwargs: Unpack[EngFromYueTranslationProcessKwargs],
) -> Series:
    """Get English subtitles translated from Cantonese with English guidance.

    Arguments:
        yue: Cantonese subtitles to translate
        eng: original English subtitles to use as reference
        translator: processor to use
        **kwargs: additional arguments for DualBlockCardinalityProcessor.process
    Returns:
        English subtitles translated from Cantonese
    """
    if translator is None:
        translator = get_eng_vs_yue_translator()
    return translator.process(yue, eng, **kwargs)


def get_eng_vs_yue_translator(
    prompt_cls: type[EngVsYueTranslationPrompt] = EngVsYueTranslationPrompt,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[EngFromYueTranslationProcessorKwargs],
) -> DualBlockCardinalityProcessor:
    """Get DualBlockCardinalityProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        provider: provider to use for queries
        **kwargs: additional arguments for DualBlockCardinalityProcessor
    Returns:
        DualBlockCardinalityProcessor with provided configuration
    """
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                DualBlockCardinalityManager,
                prompt_cls,
                ENG_FROM_YUE_TRANSLATION_JSON_PATHS,
            )
        )
    if provider is None:
        provider = get_default_provider()
    return DualBlockCardinalityProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        provider=provider,
        **kwargs,
    )
