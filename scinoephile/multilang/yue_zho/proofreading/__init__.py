#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 粤文 vs. 中文 proofreading."""

from __future__ import annotations

from logging import warning
from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.subtitles import Series
from scinoephile.llms.base import TestCase
from scinoephile.llms.dual_single import DualSinglePrompt

from .manager import YueZhoProofreadingManager
from .processor import YueZhoProofreadingProcessor
from .prompts import YueZhoHansProofreadingPrompt, YueZhoHantProofreadingPrompt

__all__ = [
    "YueZhoHansProofreadingPrompt",
    "YueZhoHantProofreadingPrompt",
    "YueZhoProofreadingManager",
    "YueZhoProofreadingProcessKwargs",
    "YueZhoProofreadingProcessorKwargs",
    "get_default_yue_vs_zho_proofreading_test_cases",
    "get_yue_vs_zho_proofread",
    "get_yue_vs_zho_proofreader",
    "YueZhoProofreadingProcessor",
]


class YueZhoProofreadingProcessKwargs(TypedDict, total=False):
    """Keyword arguments for YueZhoProofreadingProcessor.process."""

    stop_at_idx: int | None


class YueZhoProofreadingProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for YueZhoProofreadingProcessor initialization."""

    test_case_path: Path | None
    auto_verify: bool


# noinspection PyUnusedImports
def get_default_yue_vs_zho_proofreading_test_cases(
    prompt_cls: type[DualSinglePrompt] = YueZhoHansProofreadingPrompt,
) -> list[TestCase]:
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
    **kwargs: Unpack[YueZhoProofreadingProcessKwargs],
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
    test_cases: list[TestCase] | None = None,
    **kwargs: Unpack[YueZhoProofreadingProcessorKwargs],
) -> YueZhoProofreadingProcessor:
    """Get YueZhoProofreadingProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        **kwargs: additional keyword arguments for YueZhoProofreadingProcessor
    Returns:
        YueZhoProofreadingProcessor with provided configuration
    """
    if test_cases is None:
        test_cases = get_default_yue_vs_zho_proofreading_test_cases(prompt_cls)
    return YueZhoProofreadingProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        **kwargs,
    )
