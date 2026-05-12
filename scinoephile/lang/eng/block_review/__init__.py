#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English block review."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import OperationSpec, TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    ENG_BLOCK_REVIEW_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.mono_n import MonoNManager, MonoNProcessor
from scinoephile.llms.providers.registry import get_default_provider

from .prompts import BlockReviewPromptEng

__all__ = [
    "ENG_BLOCK_REVIEW_OPERATION_SPEC",
    "EngBlockReviewProcessKwargs",
    "EngBlockReviewProcessorKwargs",
    "BlockReviewPromptEng",
    "get_eng_block_reviewed",
    "get_eng_block_reviewer",
]

ENG_BLOCK_REVIEW_OPERATION_SPEC = OperationSpec(
    operation="eng-block-review",
    test_case_table_name="test_cases__eng__block_review",
    manager_cls=MonoNManager,
    prompt_cls=BlockReviewPromptEng,
)
"""Operation specification for English block review."""


class EngBlockReviewProcessKwargs(TypedDict, total=False):
    """Keyword arguments for MonoNProcessor.process."""

    stop_at_idx: int | None
    """subtitle index at which to stop processing, inclusive."""


class EngBlockReviewProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for MonoNProcessor initialization."""

    test_case_path: Path | None
    """path where encountered or verified test cases are persisted."""
    auto_verify: bool
    """whether to automatically verify model outputs against expected cases."""


def get_eng_block_reviewed(
    series: Series,
    processor: MonoNProcessor | None = None,
    **kwargs: Unpack[EngBlockReviewProcessKwargs],
) -> Series:
    """Get English series block reviewed.

    Arguments:
        series: Series to block review
        processor: MonoNProcessor to use
        **kwargs: additional keyword arguments for MonoNProcessor.process
    Returns:
        block-reviewed Series
    """
    if processor is None:
        processor = get_eng_block_reviewer()
    return processor.process(series, **kwargs)


def get_eng_block_reviewer(
    prompt_cls: type[BlockReviewPromptEng] = BlockReviewPromptEng,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[EngBlockReviewProcessorKwargs],
) -> MonoNProcessor:
    """Get MonoNProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        provider: provider to use for queries
        **kwargs: additional keyword arguments for MonoNProcessor
    Returns:
        MonoNProcessor with provided configuration
    """
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                MonoNManager,
                prompt_cls,
                ENG_BLOCK_REVIEW_JSON_PATHS,
            )
        )
    if provider is None:
        provider = get_default_provider()
    return MonoNProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        provider=provider,
        **kwargs,
    )
