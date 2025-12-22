#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 粤文 vs. 中文 proofreading."""

from __future__ import annotations

from logging import warning
from typing import Any

from scinoephile.core.subtitles import Series
from scinoephile.llms.dual_single import DualSinglePrompt

from .processor import YueZhoProofreadingProcessor
from .prompts import YueZhoHansProofreadingPrompt, YueZhoHantProofreadingPrompt
from .test_case import YueZhoProofreadingTestCase

__all__ = [
    "YueZhoHansProofreadingPrompt",
    "YueZhoHantProofreadingPrompt",
    "YueZhoProofreadingTestCase",
    "get_default_yue_vs_zho_proofreading_test_cases",
    "get_yue_vs_zho_proofread",
    "get_yue_vs_zho_proofreader",
    "YueZhoProofreadingProcessor",
]


# noinspection PyUnusedImports
def get_default_yue_vs_zho_proofreading_test_cases(
    prompt_cls: type[DualSinglePrompt] = YueZhoHansProofreadingPrompt,
) -> list[YueZhoProofreadingTestCase]:
    """Get default 粤文 vs. 中文 proofreading test cases included with package.

    Arguments:
        prompt_cls: text for LLM correspondence
    Returns:
        default test cases
    """
    try:
        from test.data.mlamd import (  # noqa: PLC0415
            get_mlamd_yue_vs_zho_proofreading_test_cases,
        )

        return get_mlamd_yue_vs_zho_proofreading_test_cases(prompt_cls)
    except ImportError as exc:
        warning(f"Default test cases not available:\n{exc}")
    return []


def get_yue_vs_zho_proofread(
    yuewen: Series,
    zhongwen: Series,
    processor: YueZhoProofreadingProcessor | None = None,
    **kwargs: Any,
) -> Series:
    """Get 粤文 subtitles proofread against 中文 subtitles.

    Arguments:
        yuewen: 粤文 Series
        zhongwen: 中文 Series
        processor: processor to use
        **kwargs: additional keyword arguments for YueZhoProofreadingProcessor.process
    Returns:
        proofread 粤文 subtitles
    """
    if processor is None:
        processor = get_yue_vs_zho_proofreader()
    return processor.process(yuewen, zhongwen, **kwargs)


def get_yue_vs_zho_proofreader(
    prompt_cls: type[YueZhoHansProofreadingPrompt] = YueZhoHansProofreadingPrompt,
    default_test_cases: list[YueZhoProofreadingTestCase] | None = None,
    **kwargs: Any,
) -> YueZhoProofreadingProcessor:
    """Get YueZhoProofreadingProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        default_test_cases: default test cases
        **kwargs: additional keyword arguments for YueZhoProofreadingProcessor
    Returns:
        YueZhoProofreadingProcessor with provided configuration
    """
    if default_test_cases is None:
        default_test_cases = get_default_yue_vs_zho_proofreading_test_cases(prompt_cls)
    return YueZhoProofreadingProcessor(
        prompt_cls=prompt_cls,
        default_test_cases=default_test_cases,
        **kwargs,
    )
