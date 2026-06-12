#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to guided written Cantonese translation from standard Chinese."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import OperationSpec, TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.dictionaries.dictionary_tools import get_dictionary_tools
from scinoephile.llms.default_test_cases import (
    YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_n_to_m import (
    DualNToMManager,
    DualNToMProcessor,
)
from scinoephile.llms.providers.registry import get_provider

from .prompts import (
    YueGuidedTranslationVsZhoPromptYueHans,
    YueGuidedTranslationVsZhoPromptYueHant,
)

__all__ = [
    "YUE_ZHO_GUIDED_TRANSLATION_OPERATION_SPEC",
    "YueGuidedTranslationVsZhoPromptYueHans",
    "YueGuidedTranslationVsZhoPromptYueHant",
    "YueVsZhoGuidedTranslationProcessKwargs",
    "YueVsZhoGuidedTranslationProcessorKwargs",
    "get_yue_translated_from_zho_with_yue_guidance",
    "get_yue_zho_guided_translator",
]

YUE_ZHO_GUIDED_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="yue-zho-guided-translation",
    test_case_table_name="test_cases__yue_zho__guided_translation",
    manager_cls=DualNToMManager,
    prompt_cls=YueGuidedTranslationVsZhoPromptYueHans,
)
"""Operation specification for guided written Cantonese translation from Chinese."""


class YueVsZhoGuidedTranslationProcessKwargs(TypedDict, total=False):
    """Keyword arguments for DualNToMProcessor.process."""

    stop_at_idx: int | None
    """Exclusive block index at which to stop processing."""


class YueVsZhoGuidedTranslationProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for DualNToMProcessor initialization."""

    test_case_path: Path | None
    """Path where encountered test cases are persisted."""
    additional_context: str | None
    """Additional context to include in the system prompt."""
    auto_verify: bool
    """Whether generated test cases should be marked verified automatically."""


def get_yue_translated_from_zho_with_yue_guidance(
    zhongwen: Series,
    yuewen: Series,
    translator: DualNToMProcessor | None = None,
    **kwargs: Unpack[YueVsZhoGuidedTranslationProcessKwargs],
) -> Series:
    """Get written Cantonese subtitles guided-translated from Chinese.

    Arguments:
        zhongwen: standard Chinese subtitles to translate
        yuewen: written Cantonese subtitles to use as reference
        translator: processor to use
        **kwargs: additional arguments for DualNToMProcessor.process
    Returns:
        written Cantonese subtitles guided-translated from Chinese
    """
    if translator is None:
        translator = get_yue_zho_guided_translator()
    return translator.process(zhongwen, yuewen, **kwargs)


def get_yue_zho_guided_translator(
    prompt_cls: type[YueGuidedTranslationVsZhoPromptYueHans] = (
        YueGuidedTranslationVsZhoPromptYueHans
    ),
    test_cases: list[TestCase] | None = None,
    use_dictionary_tool: bool = True,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[YueVsZhoGuidedTranslationProcessorKwargs],
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
                YUE_ZHO_GUIDED_TRANSLATION_JSON_PATHS,
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
