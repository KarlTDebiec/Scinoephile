#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 中文 proofreading."""

from __future__ import annotations

from logging import warning
from typing import Any

from scinoephile.core.subtitles import Series
from scinoephile.llms.base import TestCase
from scinoephile.llms.mono_block import MonoBlockProcessor, MonoBlockPrompt

from .prompts import ZhoHansProofreadingPrompt, ZhoHantProofreadingPrompt

__all__ = [
    "ZhoHansProofreadingPrompt",
    "ZhoHantProofreadingPrompt",
    "get_default_zho_proofreading_test_cases",
    "get_zho_proofread",
    "get_zho_proofreader",
]


# noinspection PyUnusedImports
def get_default_zho_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = MonoBlockPrompt,
) -> list[TestCase]:
    """Get default test cases included with package.

    Arguments:
        prompt_cls: text for LLM correspondence
    Returns:
        default test cases
    """
    try:
        from test.data.kob import (  # noqa: PLC0415
            get_kob_zho_hant_proofreading_test_cases,
        )
        from test.data.mlamd import (  # noqa: PLC0415
            get_mlamd_zho_hans_proofreading_test_cases,
            get_mlamd_zho_hant_proofreading_test_cases,
        )
        from test.data.mnt import (  # noqa: PLC0415
            get_mnt_zho_hans_proofreading_test_cases,
            get_mnt_zho_hant_proofreading_test_cases,
        )
        from test.data.t import (  # noqa: PLC0415
            get_t_zho_hans_proofreading_test_cases,
            get_t_zho_hant_proofreading_test_cases,
        )

        if prompt_cls is ZhoHantProofreadingPrompt:
            return (
                get_kob_zho_hant_proofreading_test_cases(prompt_cls)
                + get_mlamd_zho_hant_proofreading_test_cases(prompt_cls)
                + get_mnt_zho_hant_proofreading_test_cases(prompt_cls)
                + get_t_zho_hant_proofreading_test_cases(prompt_cls)
            )

        return (
            get_mlamd_zho_hans_proofreading_test_cases(prompt_cls)
            + get_mnt_zho_hans_proofreading_test_cases(prompt_cls)
            + get_t_zho_hans_proofreading_test_cases(prompt_cls)
        )
    except ImportError as exc:
        warning(f"Default test cases not available:\n{exc}")
    return []


def get_zho_proofread(
    series: Series,
    processor: MonoBlockProcessor | None = None,
    **kwargs: Any,
) -> Series:
    """Get 中文 series proofread.

    Arguments:
        series: Series to proofread
        processor: MonoBlockProcessor to use
        **kwargs: additional keyword arguments for MonoBlockProcessor.process
    Returns:
        proofread Series
    """
    if processor is None:
        processor = get_zho_proofreader()
    return processor.process(series, **kwargs)


def get_zho_proofreader(
    prompt_cls: type[ZhoHansProofreadingPrompt] = ZhoHansProofreadingPrompt,
    test_cases: list[TestCase] | None = None,
    **kwargs: Any,
) -> MonoBlockProcessor:
    """Get MonoBlockProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        **kwargs: additional keyword arguments for MonoBlockProcessor
    Returns:
        MonoBlockProcessor with provided configuration
    """
    if test_cases is None:
        test_cases = get_default_zho_proofreading_test_cases(prompt_cls)
    return MonoBlockProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        **kwargs,
    )
