#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to translation of 粤文 from 中文."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.subtitles import Series
from scinoephile.llms.base import TestCase
from scinoephile.llms.default_test_cases import (
    YUE_FROM_ZHO_TRANSLATION_JSON_PATHS,
    load_default_test_cases_from_repo_data,
)
from scinoephile.llms.dual_block_gapped import (
    DualBlockGappedManager,
    DualBlockGappedProcessor,
)

from .prompts import YueHansFromZhoTranslationPrompt, YueHantFromZhoTranslationPrompt

__all__ = [
    "YueHansFromZhoTranslationPrompt",
    "YueHantFromZhoTranslationPrompt",
    "YueFromZhoTranslationProcessKwargs",
    "YueFromZhoTranslationProcessorKwargs",
    "get_yue_from_zho_translated",
    "get_yue_from_zho_translator",
]


class YueFromZhoTranslationProcessKwargs(TypedDict, total=False):
    """Keyword arguments for DualBlockGappedProcessor.process."""

    stop_at_idx: int | None


class YueFromZhoTranslationProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for DualBlockGappedProcessor initialization."""

    test_case_path: Path | None
    auto_verify: bool


def get_yue_from_zho_translated(
    yuewen: Series,
    zhongwen: Series,
    translator: DualBlockGappedProcessor | None = None,
    **kwargs: Unpack[YueFromZhoTranslationProcessKwargs],
) -> Series:
    """Get 粤文 subtitles translated from 中文 subtitles.

    Arguments:
        yuewen: 粤文 Series
        zhongwen: 中文 Series
        translator: processor to use
        **kwargs: additional arguments for DualBlockGappedProcessor.process
    Returns:
        粤文 translated from 中文
    """
    if translator is None:
        translator = get_yue_from_zho_translator()
    return translator.process(yuewen, zhongwen, **kwargs)


def get_yue_from_zho_translator(
    prompt_cls: type[YueHansFromZhoTranslationPrompt] = YueHansFromZhoTranslationPrompt,
    test_cases: list[TestCase] | None = None,
    **kwargs: Unpack[YueFromZhoTranslationProcessorKwargs],
) -> DualBlockGappedProcessor:
    """Get DualBlockGappedProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        **kwargs: additional arguments for DualBlockGappedProcessor
    Returns:
        DualBlockGappedProcessor with provided configuration
    """
    if test_cases is None:
        test_cases = list(
            load_default_test_cases_from_repo_data(
                DualBlockGappedManager,
                prompt_cls,
                YUE_FROM_ZHO_TRANSLATION_JSON_PATHS,
            )
        )
    return DualBlockGappedProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        **kwargs,
    )
