#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 粤文 vs. 中文 line review."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.dictionaries.dictionary_tools import get_dictionary_tools
from scinoephile.llms.default_test_cases import (
    YUE_ZHO_LINE_REVIEW_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.providers.registry import get_default_provider

from .manager import YueZhoLineReviewManager
from .processor import YueZhoLineReviewProcessor
from .prompts import YueZhoHansLineReviewPrompt, YueZhoHantLineReviewPrompt

__all__ = [
    "YueZhoHansLineReviewPrompt",
    "YueZhoHantLineReviewPrompt",
    "YueZhoLineReviewManager",
    "YueZhoLineReviewProcessKwargs",
    "YueZhoLineReviewProcessor",
    "YueZhoLineReviewProcessorKwargs",
    "get_yue_line_reviewed_vs_zho",
    "get_yue_vs_zho_line_reviewer",
]


class YueZhoLineReviewProcessKwargs(TypedDict, total=False):
    """Keyword arguments for YueZhoLineReviewProcessor.process."""

    stop_at_idx: int | None


class YueZhoLineReviewProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for YueZhoLineReviewProcessor initialization."""

    test_case_path: Path | None
    auto_verify: bool


def get_yue_line_reviewed_vs_zho(
    yuewen: Series,
    zhongwen: Series,
    processor: YueZhoLineReviewProcessor | None = None,
    **kwargs: Unpack[YueZhoLineReviewProcessKwargs],
) -> Series:
    """Get 粤文 subtitles line reviewed against 中文 subtitles.

    Arguments:
        yuewen: 粤文 Series
        zhongwen: 中文 Series
        processor: processor to use
        **kwargs: additional keyword arguments for YueZhoLineReviewProcessor.process
    Returns:
        line-reviewed 粤文 subtitles
    """
    if processor is None:
        processor = get_yue_vs_zho_line_reviewer()
    return processor.process(yuewen, zhongwen, **kwargs)


def get_yue_vs_zho_line_reviewer(
    prompt_cls: type[YueZhoHansLineReviewPrompt] = YueZhoHansLineReviewPrompt,
    test_cases: list[TestCase] | None = None,
    use_dictionary_tool: bool = True,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[YueZhoLineReviewProcessorKwargs],
) -> YueZhoLineReviewProcessor:
    """Get YueZhoLineReviewProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        use_dictionary_tool: whether to wire the dictionary lookup tool
        provider: provider to use for queries
        **kwargs: additional keyword arguments for YueZhoLineReviewProcessor
    Returns:
        YueZhoLineReviewProcessor with provided configuration
    """
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                YueZhoLineReviewManager,
                prompt_cls,
                YUE_ZHO_LINE_REVIEW_JSON_PATHS,
            )
        )
    tools = None
    tool_handlers = None
    if use_dictionary_tool:
        tools, tool_handlers = get_dictionary_tools(prompt_cls)
    if provider is None:
        provider = get_default_provider()
    return YueZhoLineReviewProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        provider=provider,
        tools=tools,
        tool_handlers=tool_handlers,
        **kwargs,
    )
