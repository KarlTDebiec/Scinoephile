#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to standard Chinese block review."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import OperationSpec, TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    ZHO_HANS_BLOCK_REVIEW_JSON_PATHS,
    ZHO_HANT_BLOCK_REVIEW_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.mono_n import MonoNManager, MonoNProcessor
from scinoephile.llms.providers.registry import get_provider

from .prompts import BlockReviewPromptZhoHans, BlockReviewPromptZhoHant

__all__ = [
    "ZHO_BLOCK_REVIEW_OPERATION_SPEC",
    "ZhoBlockReviewProcessKwargs",
    "ZhoBlockReviewProcessorKwargs",
    "BlockReviewPromptZhoHans",
    "BlockReviewPromptZhoHant",
    "get_zho_block_reviewed",
    "get_zho_reviewer",
]

ZHO_BLOCK_REVIEW_OPERATION_SPEC = OperationSpec(
    operation="zho-block-review",
    test_case_table_name="test_cases__zho__block_review",
    manager_cls=MonoNManager,
    prompt_cls=BlockReviewPromptZhoHans,
)
"""Operation specification for standard Chinese block review."""


class ZhoBlockReviewProcessKwargs(TypedDict, total=False):
    """Keyword arguments for MonoNProcessor.process."""

    stop_at_idx: int | None
    """Subtitle index at which to stop processing, inclusive."""


class ZhoBlockReviewProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for MonoNProcessor initialization."""

    test_case_path: Path | None
    """Path where encountered test cases are persisted."""
    additional_context: str | None
    """Additional context to include in the system prompt."""
    auto_verify: bool
    """Whether generated test cases should be marked verified automatically."""


def get_zho_block_reviewed(
    series: Series,
    processor: MonoNProcessor | None = None,
    **kwargs: Unpack[ZhoBlockReviewProcessKwargs],
) -> Series:
    """Get standard Chinese series block reviewed.

    Arguments:
        series: Series to block review
        processor: MonoNProcessor to use
        **kwargs: additional keyword arguments for MonoNProcessor.process
    Returns:
        block-reviewed Series
    """
    if processor is None:
        processor = get_zho_reviewer()
    return processor.process(series, **kwargs)


def get_zho_reviewer(
    prompt_cls: type[BlockReviewPromptZhoHans] = BlockReviewPromptZhoHans,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ZhoBlockReviewProcessorKwargs],
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
        if prompt_cls is BlockReviewPromptZhoHant:
            test_cases = list(
                load_default_test_cases(
                    MonoNManager,
                    prompt_cls,
                    ZHO_HANT_BLOCK_REVIEW_JSON_PATHS,
                )
            )
        else:
            test_cases = list(
                load_default_test_cases(
                    MonoNManager,
                    prompt_cls,
                    ZHO_HANS_BLOCK_REVIEW_JSON_PATHS,
                )
            )
    if provider is None:
        provider = get_provider()
    return MonoNProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        provider=provider,
        **kwargs,
    )
