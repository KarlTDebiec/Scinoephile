#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to translation of 粤文 against 中文."""

from __future__ import annotations

from logging import warning
from typing import Any

from scinoephile.core import Series
from scinoephile.core.many_to_many_blockwise import ManyToManyBlockwiseTestCase

from .prompts import YueHansTranslationPrompt, YueHantTranslationPrompt
from .translator import YueVsZhoTranslator

__all__ = [
    "YueHansTranslationPrompt",
    "YueHantTranslationPrompt",
    "YueVsZhoTranslator",
    "get_default_yue_vs_zho_translation_test_cases",
    "get_yue_vs_zho_translated",
    "get_yue_vs_zho_translator",
]


# noinspection PyUnusedImports
def get_default_yue_vs_zho_translation_test_cases(
    prompt_cls: type[YueHansTranslationPrompt] = YueHansTranslationPrompt,
) -> list[ManyToManyBlockwiseTestCase]:
    """Get default test cases included with package.

    Arguments:
        prompt_cls: text for LLM correspondence
    Returns:
        default test cases
    """
    try:
        from test.data.mlamd import (  # noqa: PLC0415
            get_mlamd_yue_translation_test_cases,
        )

        return get_mlamd_yue_translation_test_cases(prompt_cls)
    except ImportError as exc:
        warning(
            f"Default test cases not available for 粤文 vs.中文 translation:\n{exc}"
        )
    return []


def get_yue_vs_zho_translated(
    yuewen: Series,
    zhongwen: Series,
    translator: YueVsZhoTranslator | None = None,
    **kwargs: Any,
) -> Series:
    """Get 粤文 subtitles translated against 中文 subtitles.

    Arguments:
        yuewen: 粤文 Series
        zhongwen: 中文 Series
        translator: Translator to use
        **kwargs: additional arguments for Translator.translate
    Returns:
        粤文 translated against 中文
    """
    if translator is None:
        translator = get_yue_vs_zho_translator()
    return translator.translate(yuewen, zhongwen, **kwargs)


def get_yue_vs_zho_translator(
    prompt_cls: type[YueHansTranslationPrompt] = YueHansTranslationPrompt,
    default_test_cases: list[ManyToManyBlockwiseTestCase] | None = None,
    **kwargs: Any,
) -> YueVsZhoTranslator:
    """Get YueVsZhoTranslator with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        default_test_cases: default test cases
        **kwargs: additional arguments for YueVsZhoTranslator
    Returns:
        YueVsZhoTranslator with provided configuration
    """
    if default_test_cases is None:
        default_test_cases = get_default_yue_vs_zho_translation_test_cases(prompt_cls)
    return YueVsZhoTranslator(
        prompt_cls=prompt_cls,
        default_test_cases=default_test_cases,
        **kwargs,
    )
