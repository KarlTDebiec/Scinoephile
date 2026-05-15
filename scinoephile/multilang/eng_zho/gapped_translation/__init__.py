#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English gapped translation using Chinese."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import OperationSpec, TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    ENG_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_n_minus_m_to_n import (
    DualNMinusMToNManager,
    DualNMinusMToNProcessor,
)
from scinoephile.llms.providers.registry import get_provider

from .prompts import EngGappedTranslationVsZhoPrompt

__all__ = [
    "ENG_ZHO_GAPPED_TRANSLATION_OPERATION_SPEC",
    "EngGappedTranslationVsZhoPrompt",
    "EngVsZhoGappedTranslationProcessKwargs",
    "EngVsZhoGappedTranslationProcessorKwargs",
    "get_eng_gapped_translated_vs_zho",
    "get_eng_vs_zho_gapped_translator",
]

ENG_ZHO_GAPPED_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="eng-zho-gapped-translation",
    test_case_table_name="test_cases__eng_zho__gapped_translation",
    manager_cls=DualNMinusMToNManager,
    prompt_cls=EngGappedTranslationVsZhoPrompt,
)
"""Operation specification for English gapped translation from Chinese."""


class EngVsZhoGappedTranslationProcessKwargs(TypedDict, total=False):
    """Keyword arguments for DualNMinusMToNProcessor.process."""

    stop_at_idx: int | None
    """Exclusive block index at which to stop processing."""


class EngVsZhoGappedTranslationProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for DualNMinusMToNProcessor initialization."""

    test_case_path: Path | None
    """Path where encountered test cases are persisted."""
    additional_context: str | None
    """Additional context to include in the system prompt."""
    auto_verify: bool
    """Whether generated test cases should be marked verified automatically."""


def get_eng_gapped_translated_vs_zho(
    eng: Series,
    zho: Series,
    translator: DualNMinusMToNProcessor | None = None,
    **kwargs: Unpack[EngVsZhoGappedTranslationProcessKwargs],
) -> Series:
    """Get English subtitle gaps translated using Chinese.

    Arguments:
        eng: English subtitles that may contain gaps
        zho: Chinese subtitles to use as reference
        translator: processor to use
        **kwargs: additional arguments for DualNMinusMToNProcessor.process
    Returns:
        English subtitles with gaps translated using Chinese
    """
    if translator is None:
        translator = get_eng_vs_zho_gapped_translator()
    return translator.process(eng, zho, **kwargs)


def get_eng_vs_zho_gapped_translator(
    prompt_cls: type[EngGappedTranslationVsZhoPrompt] = EngGappedTranslationVsZhoPrompt,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[EngVsZhoGappedTranslationProcessorKwargs],
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
                ENG_ZHO_GAPPED_TRANSLATION_JSON_PATHS,
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
