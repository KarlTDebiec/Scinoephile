#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for block-reviewing subtitles."""

from __future__ import annotations

from typing import Unpack

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.core.subtitles import Series
from scinoephile.lang.block_review import get_block_reviewer
from scinoephile.llms.block_review import BlockReviewProcessor, BlockReviewPrompt

from .helpers import resolve_language

__all__ = ["block_review_series"]


def block_review_series(
    series: Series,
    *,
    language: Language | None = None,
    prompt_cls: type[BlockReviewPrompt] | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    reviewer: BlockReviewProcessor | None = None,
    stop_at_idx: int | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> Series:
    """Block-review a subtitle series.

    Arguments:
        series: subtitle series to review
        language: explicit language, or None to detect it
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        provider: provider to use for queries
        reviewer: reviewer to use, or None to construct one
        stop_at_idx: exclusive block index at which to stop processing
        **kwargs: additional keyword arguments for BlockReviewProcessor
    Returns:
        block-reviewed subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or is unsupported
    """
    resolved_language = resolve_language(series, language)

    if reviewer is None:
        reviewer = get_block_reviewer(
            resolved_language,
            prompt_cls,
            test_cases,
            provider,
            **kwargs,
        )
    return reviewer.process(series, stop_at_idx=stop_at_idx)
