#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for block-reviewing subtitles."""

from __future__ import annotations

from pathlib import Path

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, TestCase, ToolBox
from scinoephile.core.subtitles import Series
from scinoephile.lang.block_review import get_block_reviewer
from scinoephile.llms.block_review import BlockReviewProcessor, BlockReviewPrompt

from .helpers import resolve_series_language

__all__ = ["review_series_blocks"]


def review_series_blocks(
    series: Series,
    *,
    language: Language | None = None,
    prompt_cls: type[BlockReviewPrompt] | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    additional_context: str | None = None,
    reviewer: BlockReviewProcessor | None = None,
    test_case_path: Path | None = None,
    auto_verify: bool = False,
    tool_box: ToolBox | None = None,
    stop_at_idx: int | None = None,
) -> Series:
    """Block-review a subtitle series.

    Arguments:
        series: subtitle series to review
        language: explicit language, or None to detect it
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        provider: provider to use for queries
        additional_context: additional context to include in prompts
        reviewer: reviewer to use, or None to construct one
        test_case_path: path where encountered test cases are persisted
        auto_verify: whether generated test cases should be marked verified
        tool_box: available tools and handlers
        stop_at_idx: exclusive block index at which to stop processing
    Returns:
        block-reviewed subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or is unsupported
    """
    resolved_language = resolve_series_language(series, language)

    if reviewer is None:
        reviewer = get_block_reviewer(
            resolved_language,
            prompt_cls=prompt_cls,
            test_cases=test_cases,
            provider=provider,
            additional_context=additional_context,
            test_case_path=test_case_path,
            auto_verify=auto_verify,
            tool_box=tool_box,
        )
    return reviewer.process(series, stop_at_idx=stop_at_idx)
