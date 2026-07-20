#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for reviewing subtitles."""

from __future__ import annotations

from typing import Unpack

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.core.subtitles import Series
from scinoephile.lang.review.guided import get_guided_reviewer
from scinoephile.lang.review.standard import get_reviewer
from scinoephile.llms.guided_review import GuidedReviewProcessor, GuidedReviewPrompt
from scinoephile.llms.review import ReviewProcessor, ReviewPrompt

from .helpers import resolve_language

__all__ = [
    "review_series",
    "review_series_guided",
]


def review_series(
    series: Series,
    *,
    language: Language | None = None,
    prompt: ReviewPrompt | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    reviewer: ReviewProcessor | None = None,
    stop_at_idx: int | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> Series:
    """Review a subtitle series.

    Arguments:
        series: subtitle series to review
        language: explicit language, or None to detect it
        prompt: text for LLM correspondence
        test_cases: test cases
        provider: provider to use for queries
        reviewer: reviewer to use, or None to construct one
        stop_at_idx: exclusive block index at which to stop processing
        **kwargs: additional keyword arguments for ReviewProcessor
    Returns:
        reviewed subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or is unsupported
    """
    resolved_language = resolve_language(series, language)

    if reviewer is None:
        reviewer = get_reviewer(
            resolved_language,
            prompt,
            test_cases,
            provider,
            **kwargs,
        )
    return reviewer.process(series, stop_at_idx=stop_at_idx)


def review_series_guided(
    target: Series,
    guide: Series,
    *,
    language: Language | None = None,
    guide_language: Language | None = None,
    prompt: GuidedReviewPrompt | None = None,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    reviewer: GuidedReviewProcessor | None = None,
    stop_at_idx: int | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> Series:
    """Review a subtitle series using guide subtitles.

    Arguments:
        target: subtitle series to review
        guide: subtitle series providing block-level guidance
        language: explicit target language, or None to detect it
        guide_language: explicit guide language, or None to detect it
        prompt: text for LLM correspondence
        test_cases: test cases
        provider: provider to use for queries
        reviewer: reviewer to use, or None to construct one
        stop_at_idx: exclusive block index at which to stop processing
        **kwargs: additional keyword arguments for GuidedReviewProcessor
    Returns:
        guided-reviewed subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or the pair is unsupported
    """
    resolved_language = resolve_language(target, language)
    resolved_guide_language = resolve_language(guide, guide_language)
    if reviewer is None:
        reviewer = get_guided_reviewer(
            resolved_language,
            resolved_guide_language,
            prompt,
            test_cases,
            provider=provider,
            **kwargs,
        )
    return reviewer.process(target, guide, stop_at_idx=stop_at_idx)
