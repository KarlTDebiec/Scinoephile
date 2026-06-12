#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English gapped translation using written Cantonese."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import OperationSpec, TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    ENG_YUE_GAPPED_TRANSLATION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_n_minus_m_to_n import (
    DualNMinusMToNManager,
    DualNMinusMToNProcessor,
)
from scinoephile.llms.providers.registry import get_provider

from .prompts import EngGappedTranslationVsYuePrompt

__all__ = [
    "ENG_YUE_GAPPED_TRANSLATION_OPERATION_SPEC",
    "EngGappedTranslationVsYuePrompt",
    "EngVsYueGappedTranslationProcessKwargs",
    "EngVsYueGappedTranslationProcessorKwargs",
    "get_eng_gapped_translated_vs_yue",
    "get_eng_vs_yue_gapped_translator",
]

ENG_YUE_GAPPED_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="eng-yue-gapped-translation",
    test_case_table_name="test_cases__eng_yue__gapped_translation",
    manager_cls=DualNMinusMToNManager,
    prompt_cls=EngGappedTranslationVsYuePrompt,
)
"""Operation specification for English gapped translation from written Cantonese."""


class EngVsYueGappedTranslationProcessKwargs(TypedDict, total=False):
    """Keyword arguments for DualNMinusMToNProcessor.process."""

    stop_at_idx: int | None
    """Exclusive block index at which to stop processing."""


class EngVsYueGappedTranslationProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for DualNMinusMToNProcessor initialization."""

    test_case_path: Path | None
    """Path where encountered test cases are persisted."""
    additional_context: str | None
    """Additional context to include in the system prompt."""
    auto_verify: bool
    """Whether generated test cases should be marked verified automatically."""


def get_eng_gapped_translated_vs_yue(
    eng: Series,
    yuewen: Series,
    translator: DualNMinusMToNProcessor | None = None,
    **kwargs: Unpack[EngVsYueGappedTranslationProcessKwargs],
) -> Series:
    """Get English subtitle gaps translated using written Cantonese.

    Arguments:
        eng: English subtitles that may contain gaps
        yuewen: written Cantonese subtitles to use as reference
        translator: processor to use
        **kwargs: additional arguments for DualNMinusMToNProcessor.process
    Returns:
        English subtitles with gaps translated using written Cantonese
    """
    if translator is None:
        translator = get_eng_vs_yue_gapped_translator()
    return translator.process(eng, yuewen, **kwargs)


def get_eng_vs_yue_gapped_translator(
    prompt_cls: type[EngGappedTranslationVsYuePrompt] = (
        EngGappedTranslationVsYuePrompt
    ),
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[EngVsYueGappedTranslationProcessorKwargs],
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
                ENG_YUE_GAPPED_TRANSLATION_JSON_PATHS,
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
