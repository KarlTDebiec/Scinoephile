#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for reviewing subtitles."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Unpack

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.core.subtitles import Series
from scinoephile.lang.review.guided import get_guided_reviewer
from scinoephile.lang.review.multi import get_multi_reviewer
from scinoephile.lang.review.standard import get_reviewer
from scinoephile.llms.guided_review import GuidedReviewProcessor, GuidedReviewPrompt
from scinoephile.llms.multi_review import MultiReviewProcessor, MultiReviewPrompt
from scinoephile.llms.review import ReviewProcessor, ReviewPrompt

from .helpers import resolve_language

__all__ = ["review_series", "review_series_guided", "review_series_multi"]


def review_series(
    series: Series,
    *,
    language: Language | None = None,
    prompt: ReviewPrompt | None = None,
    shared_test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    reviewer: ReviewProcessor | None = None,
    start_at_idx: int = 0,
    stop_at_idx: int | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> Series:
    """Review a subtitle series.

    Arguments:
        series: subtitle series to review
        language: explicit language, or None to detect it
        prompt: text for LLM correspondence
        shared_test_cases: shared test cases
        provider: provider to use for queries
        reviewer: reviewer to use, or None to construct one
        start_at_idx: inclusive zero-based block index at which to start processing
        stop_at_idx: exclusive zero-based block index at which to stop processing
        **kwargs: additional keyword arguments for ReviewProcessor
    Returns:
        reviewed subtitle series
    Raises:
        ScinoephileError: if a language cannot be resolved or is unsupported
    """
    resolved_language = resolve_language(series, language)

    if reviewer is None:
        reviewer = get_reviewer(
            resolved_language, prompt, shared_test_cases, provider, **kwargs
        )
    return reviewer.process(series, stop_at_idx=stop_at_idx, start_at_idx=start_at_idx)


def review_series_guided(
    target: Series,
    guide: Series,
    *,
    language: Language | None = None,
    guide_language: Language | None = None,
    prompt: GuidedReviewPrompt | None = None,
    shared_test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    reviewer: GuidedReviewProcessor | None = None,
    start_at_idx: int = 0,
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
        shared_test_cases: shared test cases
        provider: provider to use for queries
        reviewer: reviewer to use, or None to construct one
        start_at_idx: inclusive zero-based block index at which to start processing
        stop_at_idx: exclusive zero-based block index at which to stop processing
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
            shared_test_cases,
            provider=provider,
            **kwargs,
        )
    return reviewer.process(
        target, guide, stop_at_idx=stop_at_idx, start_at_idx=start_at_idx
    )


def review_series_multi(
    sources: Mapping[str, Series],
    guide: Series,
    *,
    language: Language | None = None,
    guide_language: Language | None = None,
    prompt: MultiReviewPrompt | None = None,
    shared_test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    reviewer: MultiReviewProcessor | None = None,
    start_at_idx: int = 0,
    stop_at_idx: int | None = None,
    boundary_aware: bool = False,
    **kwargs: Unpack[ProcessorKwargs],
) -> Series:
    """Review multiple equal-status subtitle sources using a complete guide.

    Arguments:
        sources: named subtitle sources to review jointly
        guide: complete subtitle series providing timing and semantic guidance
        language: explicit source and output language, or None to detect it
        guide_language: explicit guide language, or None to detect it
        prompt: text for LLM correspondence
        shared_test_cases: shared test cases
        provider: provider to use for queries
        reviewer: reviewer to use, or None to construct one
        start_at_idx: inclusive zero-based block index at which to start processing
        stop_at_idx: exclusive zero-based block index at which to stop processing
        boundary_aware: whether to reconcile provisional source boundaries across
            each complete block
        **kwargs: additional keyword arguments for MultiReviewProcessor
    Returns:
        reviewed subtitle series using guide timing
    Raises:
        ScinoephileError: if fewer than two sources are provided, source languages
          differ, or the language pair is unsupported
    """
    if len(sources) < 2:
        raise ScinoephileError("Multi-review requires at least two subtitle sources.")

    resolved_languages = {
        resolve_language(source, language) for source in sources.values()
    }
    if len(resolved_languages) != 1:
        language_codes = ", ".join(
            sorted(resolved_language.code for resolved_language in resolved_languages)
        )
        raise ScinoephileError(
            f"Multi-review source languages must match; got {language_codes}."
        )
    resolved_language = resolved_languages.pop()
    resolved_guide_language = resolve_language(guide, guide_language)
    if reviewer is None:
        reviewer = get_multi_reviewer(
            resolved_language,
            resolved_guide_language,
            prompt,
            shared_test_cases,
            provider=provider,
            boundary_aware=boundary_aware,
            **kwargs,
        )
    return reviewer.process(
        sources, guide, stop_at_idx=stop_at_idx, start_at_idx=start_at_idx
    )
