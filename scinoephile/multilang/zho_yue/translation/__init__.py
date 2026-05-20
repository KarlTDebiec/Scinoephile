#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to standard Chinese translation from written Cantonese."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import OperationSpec, TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    ZHO_YUE_TRANSLATION_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_n_to_m import (
    DualNToMManager,
    DualNToMProcessor,
)
from scinoephile.llms.providers.registry import get_provider

from .prompts import ZhoTranslationVsYuePromptZhoHans, ZhoTranslationVsYuePromptZhoHant

__all__ = [
    "ZHO_YUE_TRANSLATION_OPERATION_SPEC",
    "ZhoTranslationVsYuePromptZhoHans",
    "ZhoTranslationVsYuePromptZhoHant",
    "ZhoVsYueTranslationProcessKwargs",
    "ZhoVsYueTranslationProcessorKwargs",
    "get_zho_translated_from_yue",
    "get_zho_yue_translator",
]

ZHO_YUE_TRANSLATION_OPERATION_SPEC = OperationSpec(
    operation="zho-yue-translation",
    test_case_table_name="test_cases__zho_yue__translation",
    manager_cls=DualNToMManager,
    prompt_cls=ZhoTranslationVsYuePromptZhoHans,
)
"""Operation specification for standard Chinese translation from written Cantonese."""


class ZhoVsYueTranslationProcessKwargs(TypedDict, total=False):
    """Keyword arguments for DualNToMProcessor.process."""

    stop_at_idx: int | None
    """Exclusive block index at which to stop processing."""


class ZhoVsYueTranslationProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for DualNToMProcessor initialization."""

    test_case_path: Path | None
    """Path where encountered test cases are persisted."""
    additional_context: str | None
    """Additional context to include in the system prompt."""
    auto_verify: bool
    """Whether generated test cases should be marked verified automatically."""


def get_zho_translated_from_yue(
    yuewen: Series,
    translator: DualNToMProcessor | None = None,
    **kwargs: Unpack[ZhoVsYueTranslationProcessKwargs],
) -> Series:
    """Get standard Chinese subtitles translated from written Cantonese.

    Arguments:
        yuewen: written Cantonese subtitles to translate
        translator: processor to use
        **kwargs: additional arguments for DualNToMProcessor.process
    Returns:
        standard Chinese subtitles translated from written Cantonese
    """
    if translator is None:
        translator = get_zho_yue_translator()
    return translator.process(yuewen, Series(), **kwargs)


def get_zho_yue_translator(
    prompt_cls: type[ZhoTranslationVsYuePromptZhoHans] = (
        ZhoTranslationVsYuePromptZhoHans
    ),
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ZhoVsYueTranslationProcessorKwargs],
) -> DualNToMProcessor:
    """Get DualNToMProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
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
                ZHO_YUE_TRANSLATION_JSON_PATHS,
            )
        )
    if provider is None:
        provider = get_provider()
    return DualNToMProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        provider=provider,
        **kwargs,
    )
