#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to translation of written Cantonese from standard Chinese."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import OperationSpec, TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.dictionaries.dictionary_tools import get_dictionary_tools
from scinoephile.llms.default_test_cases import (
    YUE_FROM_ZHO_TRANSLATION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_block_gapped import (
    DualBlockGappedManager,
    DualBlockGappedProcessor,
)
from scinoephile.llms.providers.registry import get_default_provider

from .prompts import (
    YueVsZhoYueHansTranslationPrompt,
    YueVsZhoYueHantTranslationPrompt,
)

__all__ = [
    "YUE_ZHO_TRANSLATION_OPERATION_SPEC",
    "YueVsZhoYueHansTranslationPrompt",
    "YueVsZhoYueHantTranslationPrompt",
    "YueFromZhoTranslationProcessKwargs",
    "YueFromZhoTranslationProcessorKwargs",
    "get_yue_translated_vs_zho",
    "get_yue_vs_zho_translator",
]

YUE_ZHO_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="yue-zho-translation",
    test_case_table_name="test_cases__yue_zho__translation",
    manager_cls=DualBlockGappedManager,
    prompt_cls=YueVsZhoYueHansTranslationPrompt,
)
"""Operation specification for written Cantonese translation."""


class YueFromZhoTranslationProcessKwargs(TypedDict, total=False):
    """Keyword arguments for DualBlockGappedProcessor.process."""

    stop_at_idx: int | None
    """Subtitle index at which to stop processing, inclusive."""


class YueFromZhoTranslationProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for DualBlockGappedProcessor initialization."""

    test_case_path: Path | None
    """Path where encountered test cases are persisted."""
    auto_verify: bool
    """Whether generated test cases should be marked verified automatically."""


def get_yue_translated_vs_zho(
    yuewen: Series,
    zhongwen: Series,
    translator: DualBlockGappedProcessor | None = None,
    **kwargs: Unpack[YueFromZhoTranslationProcessKwargs],
) -> Series:
    """Get written Cantonese subtitles translated from standard Chinese subtitles.

    Arguments:
        yuewen: written Cantonese Series
        zhongwen: standard Chinese Series
        translator: processor to use
        **kwargs: additional arguments for DualBlockGappedProcessor.process
    Returns:
        written Cantonese translated from standard Chinese
    """
    if translator is None:
        translator = get_yue_vs_zho_translator()
    return translator.process(yuewen, zhongwen, **kwargs)


def get_yue_vs_zho_translator(
    prompt_cls: type[YueVsZhoYueHansTranslationPrompt] = (
        YueVsZhoYueHansTranslationPrompt
    ),
    test_cases: list[TestCase] | None = None,
    use_dictionary_tool: bool = True,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[YueFromZhoTranslationProcessorKwargs],
) -> DualBlockGappedProcessor:
    """Get DualBlockGappedProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        use_dictionary_tool: whether to wire the dictionary lookup tool
        provider: provider to use for queries
        **kwargs: additional arguments for DualBlockGappedProcessor
    Returns:
        DualBlockGappedProcessor with provided configuration
    """
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                DualBlockGappedManager,
                prompt_cls,
                YUE_FROM_ZHO_TRANSLATION_JSON_PATHS,
            )
        )
    tool_box = None
    if use_dictionary_tool:
        tool_box = get_dictionary_tools(prompt_cls)
    if provider is None:
        provider = get_default_provider()
    return DualBlockGappedProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        provider=provider,
        tool_box=tool_box,
        **kwargs,
    )
