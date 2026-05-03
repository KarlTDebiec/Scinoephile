#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to block review of 粤文 against 中文."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.dictionaries.dictionary_tools import get_dictionary_tools
from scinoephile.llms.default_test_cases import (
    YUE_ZHO_BLOCK_REVIEW_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_block import DualBlockManager, DualBlockProcessor
from scinoephile.llms.providers.registry import get_default_provider

from .prompts import (
    YueVsZhoYueHansBlockReviewPrompt,
    YueVsZhoYueHantBlockReviewPrompt,
)

__all__ = [
    "YueVsZhoYueHansBlockReviewPrompt",
    "YueVsZhoYueHantBlockReviewPrompt",
    "YueZhoBlockReviewProcessKwargs",
    "YueZhoBlockReviewProcessorKwargs",
    "get_yue_block_reviewed_vs_zho",
    "get_yue_vs_zho_block_reviewer",
]


class YueZhoBlockReviewProcessKwargs(TypedDict, total=False):
    """Keyword arguments for DualBlockProcessor.process."""

    stop_at_idx: int | None
    """Subtitle index at which to stop processing, inclusive."""


class YueZhoBlockReviewProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for DualBlockProcessor initialization."""

    test_case_path: Path | None
    """Path where encountered test cases are persisted."""
    auto_verify: bool
    """Whether generated test cases should be marked verified automatically."""


def get_yue_block_reviewed_vs_zho(
    yuewen: Series,
    zhongwen: Series,
    reviewer: DualBlockProcessor | None = None,
    **kwargs: Unpack[YueZhoBlockReviewProcessKwargs],
) -> Series:
    """Get 粤文 subtitles block reviewed against 中文 subtitles.

    Arguments:
        yuewen: 粤文 Series
        zhongwen: 中文 Series
        reviewer: processor to use
        **kwargs: additional arguments for DualBlockProcessor.process
    Returns:
        粤文 block reviewed against 中文
    """
    if reviewer is None:
        reviewer = get_yue_vs_zho_block_reviewer()
    return reviewer.process(yuewen, zhongwen, **kwargs)


def get_yue_vs_zho_block_reviewer(
    prompt_cls: type[YueVsZhoYueHansBlockReviewPrompt] = (
        YueVsZhoYueHansBlockReviewPrompt
    ),
    test_cases: list[TestCase] | None = None,
    use_dictionary_tool: bool = True,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[YueZhoBlockReviewProcessorKwargs],
) -> DualBlockProcessor:
    """Get DualBlockProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        use_dictionary_tool: whether to wire the dictionary lookup tool
        provider: provider to use for queries
        **kwargs: additional arguments for DualBlockProcessor
    Returns:
        DualBlockProcessor with provided configuration
    """
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                DualBlockManager,
                prompt_cls,
                YUE_ZHO_BLOCK_REVIEW_JSON_PATHS,
            )
        )
    tool_box = None
    if use_dictionary_tool:
        tool_box = get_dictionary_tools(prompt_cls)
    if provider is None:
        provider = get_default_provider()
    return DualBlockProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        provider=provider,
        tool_box=tool_box,
        **kwargs,
    )
