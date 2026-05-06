#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to written Cantonese vs. standard Chinese line review."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import OperationSpec, TestCase
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
from .prompts import (
    YueVsZhoYueHansLineReviewPrompt,
    YueVsZhoYueHantLineReviewPrompt,
)

__all__ = [
    "YUE_ZHO_LINE_REVIEW_OPERATION_SPEC",
    "YueVsZhoYueHansLineReviewPrompt",
    "YueVsZhoYueHantLineReviewPrompt",
    "YueZhoLineReviewManager",
    "YueZhoLineReviewProcessKwargs",
    "YueZhoLineReviewProcessor",
    "YueZhoLineReviewProcessorKwargs",
    "get_yue_line_reviewed_vs_zho",
    "get_yue_vs_zho_line_reviewer",
]

YUE_ZHO_LINE_REVIEW_OPERATION_SPEC = OperationSpec(
    operation="yue-zho-line-review",
    test_case_table_name="test_cases__yue_zho__line_review",
    manager_cls=YueZhoLineReviewManager,
    prompt_cls=YueVsZhoYueHansLineReviewPrompt,
)
"""Operation specification for written Cantonese line review."""


class YueZhoLineReviewProcessKwargs(TypedDict, total=False):
    """Keyword arguments for YueZhoLineReviewProcessor.process."""

    stop_at_idx: int | None
    """block index at which to stop processing, inclusive."""


class YueZhoLineReviewProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for YueZhoLineReviewProcessor initialization."""

    test_case_path: Path | None
    """path where review test cases are persisted."""
    auto_verify: bool
    """whether to automatically verify updated test cases."""


def get_yue_line_reviewed_vs_zho(
    yuewen: Series,
    zhongwen: Series,
    line_reviewer: YueZhoLineReviewProcessor | None = None,
    **kwargs: Unpack[YueZhoLineReviewProcessKwargs],
) -> Series:
    """Get written Cantonese subtitles line reviewed against standard Chinese subtitles.

    Arguments:
        yuewen: written Cantonese Series
        zhongwen: standard Chinese Series
        line_reviewer: line reviewer to use
        **kwargs: additional keyword arguments for YueZhoLineReviewProcessor.process
    Returns:
        line-reviewed written Cantonese subtitles
    """
    if line_reviewer is None:
        line_reviewer = get_yue_vs_zho_line_reviewer()
    return line_reviewer.process(yuewen, zhongwen, **kwargs)


def get_yue_vs_zho_line_reviewer(
    prompt_cls: type[YueVsZhoYueHansLineReviewPrompt] = YueVsZhoYueHansLineReviewPrompt,
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
        configured YueZhoLineReviewProcessor
    """
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                YueZhoLineReviewManager,
                prompt_cls,
                YUE_ZHO_LINE_REVIEW_JSON_PATHS,
            )
        )
    tool_box = None
    if use_dictionary_tool:
        tool_box = get_dictionary_tools(prompt_cls)
    if provider is None:
        provider = get_default_provider()
    return YueZhoLineReviewProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        provider=provider,
        tool_box=tool_box,
        **kwargs,
    )
