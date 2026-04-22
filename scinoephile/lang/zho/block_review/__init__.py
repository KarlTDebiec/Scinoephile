#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 中文 block review."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    ZHO_HANS_BLOCK_REVIEW_JSON_PATHS,
    ZHO_HANT_BLOCK_REVIEW_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.mono_block import MonoBlockManager, MonoBlockProcessor
from scinoephile.llms.providers.registry import get_default_provider

from .prompts import ZhoHansBlockReviewPrompt, ZhoHantBlockReviewPrompt

__all__ = [
    "ZhoBlockReviewProcessKwargs",
    "ZhoBlockReviewProcessorKwargs",
    "ZhoHansBlockReviewPrompt",
    "ZhoHantBlockReviewPrompt",
    "get_zho_block_reviewed",
    "get_zho_reviewer",
]


class ZhoBlockReviewProcessKwargs(TypedDict, total=False):
    """Keyword arguments for MonoBlockProcessor.process."""

    stop_at_idx: int | None


class ZhoBlockReviewProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for MonoBlockProcessor initialization."""

    test_case_path: Path | None
    auto_verify: bool


def get_zho_block_reviewed(
    series: Series,
    processor: MonoBlockProcessor | None = None,
    **kwargs: Unpack[ZhoBlockReviewProcessKwargs],
) -> Series:
    """Get 中文 series block reviewed.

    Arguments:
        series: Series to block review
        processor: MonoBlockProcessor to use
        **kwargs: additional keyword arguments for MonoBlockProcessor.process
    Returns:
        block-reviewed Series
    """
    if processor is None:
        processor = get_zho_reviewer()
    return processor.process(series, **kwargs)


def get_zho_reviewer(
    prompt_cls: type[ZhoHansBlockReviewPrompt] = ZhoHansBlockReviewPrompt,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ZhoBlockReviewProcessorKwargs],
) -> MonoBlockProcessor:
    """Get MonoBlockProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        provider: provider to use for queries
        **kwargs: additional keyword arguments for MonoBlockProcessor
    Returns:
        MonoBlockProcessor with provided configuration
    """
    if test_cases is None:
        if prompt_cls is ZhoHantBlockReviewPrompt:
            test_cases = list(
                load_default_test_cases(
                    MonoBlockManager,
                    prompt_cls,
                    ZHO_HANT_BLOCK_REVIEW_JSON_PATHS,
                )
            )
        else:
            test_cases = list(
                load_default_test_cases(
                    MonoBlockManager,
                    prompt_cls,
                    ZHO_HANS_BLOCK_REVIEW_JSON_PATHS,
                )
            )
    if provider is None:
        provider = get_default_provider()
    return MonoBlockProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        provider=provider,
        **kwargs,
    )
