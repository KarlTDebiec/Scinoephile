#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to written Cantonese gapped translation using standard Chinese."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import OperationSpec, TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.dictionaries.dictionary_tools import get_dictionary_tools
from scinoephile.llms.default_test_cases import (
    YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_n_minus_m_to_n import (
    DualNMinusMToNManager,
    DualNMinusMToNProcessor,
)
from scinoephile.llms.providers.registry import get_provider

from .prompts import (
    YueGappedTranslationVsZhoPromptYueHans,
    YueGappedTranslationVsZhoPromptYueHant,
)

__all__ = [
    "YUE_ZHO_GAPPED_TRANSLATION_OPERATION_SPEC",
    "YueGappedTranslationVsZhoPromptYueHans",
    "YueGappedTranslationVsZhoPromptYueHant",
    "YueVsZhoGappedTranslationProcessKwargs",
    "YueVsZhoGappedTranslationProcessorKwargs",
    "get_yue_gapped_translated_vs_zho",
    "get_yue_vs_zho_gapped_translator",
]

YUE_ZHO_GAPPED_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="yue-zho-gapped-translation",
    test_case_table_name="test_cases__yue_zho__gapped_translation",
    manager_cls=DualNMinusMToNManager,
    prompt_cls=YueGappedTranslationVsZhoPromptYueHans,
)
"""Operation specification for written Cantonese gapped translation."""


class YueVsZhoGappedTranslationProcessKwargs(TypedDict, total=False):
    """Keyword arguments for DualNMinusMToNProcessor.process."""

    stop_at_idx: int | None
    """Exclusive block index at which to stop processing."""


class YueVsZhoGappedTranslationProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for DualNMinusMToNProcessor initialization."""

    test_case_path: Path | None
    """Path where encountered test cases are persisted."""
    auto_verify: bool
    """Whether generated test cases should be marked verified automatically."""


def get_yue_gapped_translated_vs_zho(
    yuewen: Series,
    zhongwen: Series,
    translator: DualNMinusMToNProcessor | None = None,
    **kwargs: Unpack[YueVsZhoGappedTranslationProcessKwargs],
) -> Series:
    """Get written Cantonese subtitle gaps translated using standard Chinese.

    Arguments:
        yuewen: written Cantonese Series
        zhongwen: standard Chinese Series
        translator: processor to use
        **kwargs: additional arguments for DualNMinusMToNProcessor.process
    Returns:
        written Cantonese with gaps translated using standard Chinese
    """
    if translator is None:
        translator = get_yue_vs_zho_gapped_translator()
    return translator.process(yuewen, zhongwen, **kwargs)


def get_yue_vs_zho_gapped_translator(
    prompt_cls: type[YueGappedTranslationVsZhoPromptYueHans] = (
        YueGappedTranslationVsZhoPromptYueHans
    ),
    test_cases: list[TestCase] | None = None,
    use_dictionary_tool: bool = True,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[YueVsZhoGappedTranslationProcessorKwargs],
) -> DualNMinusMToNProcessor:
    """Get DualNMinusMToNProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        use_dictionary_tool: whether to wire the dictionary lookup tool
        provider: provider to use for queries
        **kwargs: additional arguments for DualNMinusMToNProcessor
    Returns:
        DualNMinusMToNProcessor with provided configuration
    """
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                DualNMinusMToNManager,
                prompt_cls,
                YUE_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
            )
        )
    tool_box = None
    if use_dictionary_tool:
        tool_box = get_dictionary_tools(prompt_cls)
    if provider is None:
        provider = get_provider()
    return DualNMinusMToNProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        provider=provider,
        tool_box=tool_box,
        **kwargs,
    )
