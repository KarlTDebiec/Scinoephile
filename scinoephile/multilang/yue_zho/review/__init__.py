#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to review of 粤文 against 中文."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.subtitles import Series
from scinoephile.llms.base import TestCase
from scinoephile.llms.dual_block import DualBlockProcessor
from scinoephile.llms.dual_block.manager import DualBlockManager
from scinoephile.testing.default_test_cases import (
    YUE_ZHO_REVIEW_JSON_PATHS,
    load_default_test_cases_from_repo_data,
)

from .prompts import YueHansReviewPrompt, YueHantReviewPrompt

__all__ = [
    "YueHansReviewPrompt",
    "YueHantReviewPrompt",
    "YueZhoReviewProcessKwargs",
    "YueZhoReviewProcessorKwargs",
    "get_default_yue_vs_zho_test_cases",
    "get_yue_vs_zho_reviewed",
    "get_yue_vs_zho_processor",
]


logger = getLogger(__name__)


class YueZhoReviewProcessKwargs(TypedDict, total=False):
    """Keyword arguments for DualBlockProcessor.process."""

    stop_at_idx: int | None


class YueZhoReviewProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for DualBlockProcessor initialization."""

    test_case_path: Path | None
    auto_verify: bool


def get_default_yue_vs_zho_test_cases(
    prompt_cls: type[YueHansReviewPrompt] = YueHansReviewPrompt,
) -> list[TestCase]:
    """Get default test cases included with package.

    Arguments:
        prompt_cls: text for LLM correspondence
    Returns:
        default test cases
    """
    return load_default_test_cases_from_repo_data(
        DualBlockManager,
        prompt_cls,
        YUE_ZHO_REVIEW_JSON_PATHS,
    )


def get_yue_vs_zho_reviewed(
    yuewen: Series,
    zhongwen: Series,
    processor: DualBlockProcessor | None = None,
    **kwargs: Unpack[YueZhoReviewProcessKwargs],
) -> Series:
    """Get 粤文 subtitles reviewed against 中文 subtitles.

    Arguments:
        yuewen: 粤文 Series
        zhongwen: 中文 Series
        processor: processor to use
        **kwargs: additional arguments for DualBlockProcessor.process
    Returns:
        粤文 reviewed against 中文
    """
    if processor is None:
        processor = get_yue_vs_zho_processor()
    return processor.process(yuewen, zhongwen, **kwargs)


def get_yue_vs_zho_processor(
    prompt_cls: type[YueHansReviewPrompt] = YueHansReviewPrompt,
    test_cases: list[TestCase] | None = None,
    **kwargs: Unpack[YueZhoReviewProcessorKwargs],
) -> DualBlockProcessor:
    """Get DualBlockProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        **kwargs: additional arguments for DualBlockProcessor
    Returns:
        DualBlockProcessor with provided configuration
    """
    if test_cases is None:
        test_cases = get_default_yue_vs_zho_test_cases(prompt_cls)
    return DualBlockProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        **kwargs,
    )
