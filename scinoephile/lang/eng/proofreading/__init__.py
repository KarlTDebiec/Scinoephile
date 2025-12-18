#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English proofreading."""

from __future__ import annotations

from logging import warning
from typing import Any

from scinoephile.core.subtitles import Series
from scinoephile.llms.blockwise import (
    BlockwisePrompt,
    BlockwiseReviewer,
    BlockwiseTestCase,
)

from .prompts import EngProofreadingPrompt

__all__ = [
    "EngProofreadingPrompt",
    "get_default_eng_proofreading_test_cases",
    "get_eng_proofread",
    "get_eng_proofreader",
]


# noinspection PyUnusedImports
def get_default_eng_proofreading_test_cases(
    prompt_cls: type[BlockwisePrompt] = BlockwisePrompt,
) -> list[BlockwiseTestCase]:
    """Get default English proofreading test cases included with package.

    Arguments:
        prompt_cls: text for LLM correspondence
    Returns:
        default test cases
    """
    try:
        from test.data.kob import get_kob_eng_proofreading_test_cases  # noqa: PLC0415
        from test.data.mlamd import (  # noqa: PLC0415
            get_mlamd_eng_proofreading_test_cases,
        )
        from test.data.mnt import get_mnt_eng_proofreading_test_cases  # noqa: PLC0415
        from test.data.t import get_t_eng_proofreading_test_cases  # noqa: PLC0415

        return (
            get_kob_eng_proofreading_test_cases(prompt_cls)
            + get_mlamd_eng_proofreading_test_cases(prompt_cls)
            + get_mnt_eng_proofreading_test_cases(prompt_cls)
            + get_t_eng_proofreading_test_cases(prompt_cls)
        )
    except ImportError as exc:
        warning(f"Default test cases not available for English proofreading:\n{exc}")
    return []


def get_eng_proofread(
    series: Series,
    reviewer: BlockwiseReviewer | None = None,
    **kwargs: Any,
) -> Series:
    """Get English series proofread.

    Arguments:
        series: Series to proofread
        reviewer: reviewer to use
        kwargs: additional keyword arguments for BlockwiseReviewer.review
    Returns:
        proofread Series
    """
    if reviewer is None:
        reviewer = get_eng_proofreader()
    return reviewer.review(series, **kwargs)


def get_eng_proofreader(
    prompt_cls: type[EngProofreadingPrompt] = EngProofreadingPrompt,
    default_test_cases: list[BlockwiseTestCase] | None = None,
    **kwargs: Any,
) -> BlockwiseReviewer:
    """Get a BlockwiseReviewer with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        default_test_cases: default test cases
        kwargs: additional keyword arguments for BlockwiseReviewer
    Returns:
        BlockwiseReviewer with provided configuration
    """
    if default_test_cases is None:
        default_test_cases = get_default_eng_proofreading_test_cases(prompt_cls)
    return BlockwiseReviewer(
        prompt_cls=prompt_cls,
        default_test_cases=default_test_cases,
        **kwargs,
    )
