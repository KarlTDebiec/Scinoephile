#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to standard Chinese block review."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import OperationSpec, ProcessorKwargs, TestCase
from scinoephile.core.llms.llm_provider import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.llms import load_default_test_cases
from scinoephile.llms.block_review import BlockReviewManager, BlockReviewProcessor
from scinoephile.llms.providers.registry import get_provider

from .prompts import BlockReviewPromptZhoHans, BlockReviewPromptZhoHant

__all__ = [
    "ZHO_BLOCK_REVIEW_OPERATION_SPEC",
    "ZhoBlockReviewProcessKwargs",
    "BlockReviewPromptZhoHans",
    "BlockReviewPromptZhoHant",
    "get_zho_block_reviewed",
    "get_zho_reviewer",
]

_ZHO_HANS_BLOCK_REVIEW_JSON_PATHS = (
    Path("mlamd/output/zho-Hans_ocr/lang/zho/block_review.json"),
    Path("mnt/output/zho-Hans_ocr/lang/zho/block_review.json"),
    Path("t/output/zho-Hans_ocr/lang/zho/block_review.json"),
)

_ZHO_HANT_BLOCK_REVIEW_JSON_PATHS = (
    Path("kob/output/zho-Hant_ocr/lang/zho/block_review.json"),
    Path("mlamd/output/zho-Hant_ocr/lang/zho/block_review.json"),
    Path("mnt/output/zho-Hant_ocr/lang/zho/block_review.json"),
    Path("t/output/zho-Hant_ocr/lang/zho/block_review.json"),
)

ZHO_BLOCK_REVIEW_OPERATION_SPEC = OperationSpec(
    operation="zho-block-review",
    test_case_table_name="test_cases__zho__block_review",
    manager_cls=BlockReviewManager,
    prompt_cls=BlockReviewPromptZhoHans,
)
"""Operation specification for standard Chinese block review."""


class ZhoBlockReviewProcessKwargs(TypedDict, total=False):
    """Keyword arguments for BlockReviewProcessor.process."""

    stop_at_idx: int | None
    """Exclusive block index at which to stop processing."""


def get_zho_block_reviewed(
    series: Series,
    processor: BlockReviewProcessor | None = None,
    **kwargs: Unpack[ZhoBlockReviewProcessKwargs],
) -> Series:
    """Get standard Chinese series block reviewed.

    Arguments:
        series: Series to block review
        processor: BlockReviewProcessor to use
        **kwargs: additional keyword arguments for BlockReviewProcessor.process
    Returns:
        block-reviewed Series
    """
    if processor is None:
        processor = get_zho_reviewer()
    return processor.process(series, **kwargs)


def get_zho_reviewer(
    prompt_cls: type[BlockReviewPromptZhoHant] = BlockReviewPromptZhoHans,
    test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> BlockReviewProcessor:
    """Get BlockReviewProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        provider: provider to use for queries
        **kwargs: additional keyword arguments for BlockReviewProcessor
    Returns:
        BlockReviewProcessor with provided configuration
    """
    if test_cases is None:
        if prompt_cls is BlockReviewPromptZhoHant:
            test_cases = list(
                load_default_test_cases(
                    BlockReviewManager,
                    prompt_cls,
                    _ZHO_HANT_BLOCK_REVIEW_JSON_PATHS,
                )
            )
        else:
            test_cases = list(
                load_default_test_cases(
                    BlockReviewManager,
                    prompt_cls,
                    _ZHO_HANS_BLOCK_REVIEW_JSON_PATHS,
                )
            )
    if provider is None:
        provider = get_provider()
    return BlockReviewProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        provider=provider,
        **kwargs,
    )
