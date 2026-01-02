#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English proofreading."""

from __future__ import annotations

from logging import warning
from typing import Any

from scinoephile.core.subtitles import Series
from scinoephile.llms.base import TestCase
from scinoephile.llms.mono_block import MonoBlockProcessor, MonoBlockPrompt

from .prompts import EngProofreadingPrompt

__all__ = [
    "EngProofreadingPrompt",
    "get_default_eng_proofreading_test_cases",
    "get_eng_proofread",
    "get_eng_proofreader",
]


# noinspection PyUnusedImports
def get_default_eng_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = MonoBlockPrompt,
) -> list[TestCase]:
    """Get default test cases included with package.

    Arguments:
        prompt_cls: text for LLM correspondence
    Returns:
        default test cases
    """
    try:
        from test.data.kob import get_kob_eng_proofreading_test_cases  # noqa: PLC0415
        from test.data.mlamd import (  # noqa: PLC0415
            get_mlamd_eng_proofreading_test_cases,
        )
        from test.data.mnt import get_mnt_eng_proofreading_test_cases  # noqa: PLC0415
        from test.data.t import get_t_eng_proofreading_test_cases  # noqa: PLC0415

        return (
            get_kob_eng_proofreading_test_cases(prompt_cls)
            + get_mlamd_eng_proofreading_test_cases(prompt_cls)
            + get_mnt_eng_proofreading_test_cases(prompt_cls)
            + get_t_eng_proofreading_test_cases(prompt_cls)
        )
    except ImportError as exc:
        warning(f"Default test cases not available:\n{exc}")
    return []


def get_eng_proofread(
    series: Series,
    processor: MonoBlockProcessor | None = None,
    **kwargs: Any,
) -> Series:
    """Get English series proofread.

    Arguments:
        series: Series to proofread
        processor: MonoBlockProcessor to use
        **kwargs: additional keyword arguments for MonoBlockProcessor.process
    Returns:
        proofread Series
    """
    if processor is None:
        processor = get_eng_proofreader()
    return processor.process(series, **kwargs)


def get_eng_proofreader(
    prompt_cls: type[EngProofreadingPrompt] = EngProofreadingPrompt,
    default_test_cases: list[TestCase] | None = None,
    **kwargs: Any,
) -> MonoBlockProcessor:
    """Get MonoBlockProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        default_test_cases: default test cases
        **kwargs: additional keyword arguments for MonoBlockProcessor
    Returns:
        MonoBlockProcessor with provided configuration
    """
    if default_test_cases is None:
        default_test_cases = get_default_eng_proofreading_test_cases(prompt_cls)
    return MonoBlockProcessor(
        prompt_cls=prompt_cls,
        default_test_cases=default_test_cases,
        **kwargs,
    )
