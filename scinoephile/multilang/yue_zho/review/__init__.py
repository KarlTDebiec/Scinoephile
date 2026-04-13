#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to review of 粤文 against 中文."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import TestCase
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    YUE_ZHO_REVIEW_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_block import DualBlockManager, DualBlockProcessor
from scinoephile.multilang.dictionaries.dictionary_tools import get_dictionary_tooling

from .prompts import YueHansReviewPrompt, YueHantReviewPrompt

__all__ = [
    "YueHansReviewPrompt",
    "YueHantReviewPrompt",
    "YueZhoReviewProcessKwargs",
    "YueZhoReviewProcessorKwargs",
    "get_yue_vs_zho_reviewed",
    "get_yue_vs_zho_processor",
]


class YueZhoReviewProcessKwargs(TypedDict, total=False):
    """Keyword arguments for DualBlockProcessor.process."""

    stop_at_idx: int | None


class YueZhoReviewProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for DualBlockProcessor initialization."""

    test_case_path: Path | None
    auto_verify: bool


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
    use_dictionary_tool: bool = True,
    **kwargs: Unpack[YueZhoReviewProcessorKwargs],
) -> DualBlockProcessor:
    """Get DualBlockProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        use_dictionary_tool: whether to wire the dictionary lookup tool
        **kwargs: additional arguments for DualBlockProcessor
    Returns:
        DualBlockProcessor with provided configuration
    """
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                DualBlockManager,
                prompt_cls,
                YUE_ZHO_REVIEW_JSON_PATHS,
            )
        )
    tools = None
    tool_handlers = None
    if use_dictionary_tool:
        tools, tool_handlers = get_dictionary_tooling()
    return DualBlockProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        tools=tools,
        tool_handlers=tool_handlers,
        **kwargs,
    )
