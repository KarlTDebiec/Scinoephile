#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to standard Chinese gapped translation using written Cantonese."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import OperationSpec, TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    ZHO_YUE_GAPPED_TRANSLATION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_n_minus_m_to_n import (
    DualNMinusMToNManager,
    DualNMinusMToNProcessor,
)
from scinoephile.llms.providers.registry import get_provider

from .prompts import (
    ZhoGappedTranslationVsYuePromptZhoHans,
    ZhoGappedTranslationVsYuePromptZhoHant,
)

__all__ = [
    "ZHO_YUE_GAPPED_TRANSLATION_OPERATION_SPEC",
    "ZhoGappedTranslationVsYuePromptZhoHans",
    "ZhoGappedTranslationVsYuePromptZhoHant",
    "ZhoVsYueGappedTranslationProcessKwargs",
    "ZhoVsYueGappedTranslationProcessorKwargs",
    "get_zho_gapped_translated_vs_yue",
    "get_zho_vs_yue_gapped_translator",
]

ZHO_YUE_GAPPED_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="zho-yue-gapped-translation",
    test_case_table_name="test_cases__zho_yue__gapped_translation",
    manager_cls=DualNMinusMToNManager,
    prompt_cls=ZhoGappedTranslationVsYuePromptZhoHans,
)
"""Operation specification for standard Chinese gapped translation."""


class ZhoVsYueGappedTranslationProcessKwargs(TypedDict, total=False):
    """Keyword arguments for DualNMinusMToNProcessor.process."""

    stop_at_idx: int | None
    """Exclusive block index at which to stop processing."""


class ZhoVsYueGappedTranslationProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for DualNMinusMToNProcessor initialization."""

    test_case_path: Path | None
    """Path where encountered test cases are persisted."""
    additional_context: str | None
    """Additional context to include in the system prompt."""
    auto_verify: bool
    """Whether generated test cases should be marked verified automatically."""


def get_zho_gapped_translated_vs_yue(
    zhongwen: Series,
    yuewen: Series,
    translator: DualNMinusMToNProcessor | None = None,
    **kwargs: Unpack[ZhoVsYueGappedTranslationProcessKwargs],
) -> Series:
    """Get standard Chinese subtitle gaps translated using written Cantonese.

    Arguments:
        zhongwen: standard Chinese Series
        yuewen: written Cantonese Series
        translator: processor to use
        **kwargs: additional arguments for DualNMinusMToNProcessor.process
    Returns:
        standard Chinese with gaps translated using written Cantonese
    """
    if translator is None:
        translator = get_zho_vs_yue_gapped_translator()
    return translator.process(zhongwen, yuewen, **kwargs)


def get_zho_vs_yue_gapped_translator(
    prompt_cls: type[ZhoGappedTranslationVsYuePromptZhoHans] = (
        ZhoGappedTranslationVsYuePromptZhoHans
    ),
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ZhoVsYueGappedTranslationProcessorKwargs],
) -> DualNMinusMToNProcessor:
    """Get DualNMinusMToNProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
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
                ZHO_YUE_GAPPED_TRANSLATION_JSON_PATHS,
            )
        )
    if provider is None:
        provider = get_provider()
    return DualNMinusMToNProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        provider=provider,
        **kwargs,
    )
