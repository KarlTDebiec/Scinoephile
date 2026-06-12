#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to written Cantonese translation from English."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import OperationSpec, TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.dictionaries.dictionary_tools import get_dictionary_tools
from scinoephile.llms.default_test_cases import (
    YUE_ENG_TRANSLATION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_n_to_m import (
    DualNToMManager,
    DualNToMProcessor,
)
from scinoephile.llms.providers.registry import get_provider

from .prompts import YueTranslationVsEngPromptYueHans, YueTranslationVsEngPromptYueHant

__all__ = [
    "YUE_ENG_TRANSLATION_OPERATION_SPEC",
    "YueTranslationVsEngPromptYueHans",
    "YueTranslationVsEngPromptYueHant",
    "YueVsEngTranslationProcessKwargs",
    "YueVsEngTranslationProcessorKwargs",
    "get_yue_eng_translator",
    "get_yue_translated_from_eng",
]

YUE_ENG_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="yue-eng-translation",
    test_case_table_name="test_cases__yue_eng__translation",
    manager_cls=DualNToMManager,
    prompt_cls=YueTranslationVsEngPromptYueHans,
)
"""Operation specification for written Cantonese translation from English."""


class YueVsEngTranslationProcessKwargs(TypedDict, total=False):
    """Keyword arguments for DualNToMProcessor.process."""

    stop_at_idx: int | None
    """Exclusive block index at which to stop processing."""


class YueVsEngTranslationProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for DualNToMProcessor initialization."""

    test_case_path: Path | None
    """Path where encountered test cases are persisted."""
    additional_context: str | None
    """Additional context to include in the system prompt."""
    auto_verify: bool
    """Whether generated test cases should be marked verified automatically."""


def get_yue_translated_from_eng(
    eng: Series,
    translator: DualNToMProcessor | None = None,
    **kwargs: Unpack[YueVsEngTranslationProcessKwargs],
) -> Series:
    """Get written Cantonese subtitles translated from English.

    Arguments:
        eng: English subtitles to translate
        translator: processor to use
        **kwargs: additional arguments for DualNToMProcessor.process
    Returns:
        written Cantonese subtitles translated from English
    """
    if translator is None:
        translator = get_yue_eng_translator()
    return translator.process(eng, Series(), **kwargs)


def get_yue_eng_translator(
    prompt_cls: type[YueTranslationVsEngPromptYueHans] = (
        YueTranslationVsEngPromptYueHans
    ),
    test_cases: list[TestCase] | None = None,
    use_dictionary_tool: bool = True,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[YueVsEngTranslationProcessorKwargs],
) -> DualNToMProcessor:
    """Get DualNToMProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        use_dictionary_tool: whether to wire the dictionary lookup tool
        provider: provider to use for queries
        **kwargs: additional arguments for DualNToMProcessor
    Returns:
        DualNToMProcessor with provided configuration
    """
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                DualNToMManager,
                prompt_cls,
                YUE_ENG_TRANSLATION_JSON_PATHS,
            )
        )
    tool_box = None
    if use_dictionary_tool:
        tool_box = get_dictionary_tools(prompt_cls)
    if provider is None:
        provider = get_provider()
    return DualNToMProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        provider=provider,
        tool_box=tool_box,
        **kwargs,
    )
