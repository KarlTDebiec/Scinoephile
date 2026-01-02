#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to translation of 粤文 from 中文."""

from __future__ import annotations

from logging import warning
from typing import Any

from scinoephile.core.subtitles import Series
from scinoephile.llms.base import TestCase
from scinoephile.llms.dual_block_gapped import DualBlockGappedProcessor

from .prompts import YueHansFromZhoTranslationPrompt, YueHantFromZhoTranslationPrompt

__all__ = [
    "YueHansFromZhoTranslationPrompt",
    "YueHantFromZhoTranslationPrompt",
    "get_default_yue_from_zho_translation_test_cases",
    "get_yue_from_zho_translated",
    "get_yue_from_zho_translator",
]


# noinspection PyUnusedImports
def get_default_yue_from_zho_translation_test_cases(
    prompt_cls: type[YueHansFromZhoTranslationPrompt] = YueHansFromZhoTranslationPrompt,
) -> list[TestCase]:
    """Get default test cases included with package.

    Arguments:
        prompt_cls: text for LLM correspondence
    Returns:
        default test cases
    """
    try:
        from test.data.mlamd import (  # noqa: PLC0415
            get_mlamd_yue_from_zho_translation_test_cases,
        )

        return get_mlamd_yue_from_zho_translation_test_cases(prompt_cls)
    except ImportError as exc:
        warning(f"Default test cases not available:\n{exc}")
    return []


def get_yue_from_zho_translated(
    yuewen: Series,
    zhongwen: Series,
    translator: DualBlockGappedProcessor | None = None,
    **kwargs: Any,
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
    default_test_cases: list[TestCase] | None = None,
    **kwargs: Any,
) -> DualBlockGappedProcessor:
    """Get DualBlockGappedProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        default_test_cases: default test cases
        **kwargs: additional arguments for DualBlockGappedProcessor
    Returns:
        DualBlockGappedProcessor with provided configuration
    """
    if default_test_cases is None:
        default_test_cases = get_default_yue_from_zho_translation_test_cases(prompt_cls)
    return DualBlockGappedProcessor(
        prompt_cls=prompt_cls,
        default_test_cases=default_test_cases,
        **kwargs,
    )
