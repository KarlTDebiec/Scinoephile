#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to review of 粤文 against 中文."""

from __future__ import annotations

from logging import warning
from typing import Any

from scinoephile.core.subtitles import Series
from scinoephile.llms.dual_block import DualBlockTestCase

from .prompts import YueHansReviewPrompt, YueHantReviewPrompt
from .reviewer import YueVsZhoReviewer

__all__ = [
    "YueHansReviewPrompt",
    "YueHantReviewPrompt",
    "YueVsZhoReviewer",
    "get_default_yue_vs_zho_test_cases",
    "get_yue_vs_zho_reviewed",
    "get_yue_vs_zho_reviewer",
]


# noinspection PyUnusedImports
def get_default_yue_vs_zho_test_cases(
    prompt_cls: type[YueHansReviewPrompt] = YueHansReviewPrompt,
) -> list[DualBlockTestCase]:
    """Get default test cases included with package.

    Arguments:
        prompt_cls: text for LLM correspondence
    Returns:
        default test cases
    """
    try:
        from test.data.mlamd import (  # noqa: PLC0415
            get_mlamd_yue_vs_zho_review_test_cases,
        )

        return get_mlamd_yue_vs_zho_review_test_cases(prompt_cls)
    except ImportError as exc:
        warning(f"Default test cases not available for 粤文 vs.中文 review:\n{exc}")
    return []


def get_yue_vs_zho_reviewed(
    yuewen: Series,
    zhongwen: Series,
    reviewer: YueVsZhoReviewer | None = None,
    **kwargs: Any,
) -> Series:
    """Get 粤文 subtitles reviewed against 中文 subtitles.

    Arguments:
        yuewen: 粤文 Series
        zhongwen: 中文 Series
        reviewer: Reviewer to use
        **kwargs: additional arguments for Reviewer.review
    Returns:
        粤文 reviewed against 中文
    """
    if reviewer is None:
        reviewer = get_yue_vs_zho_reviewer()
    return reviewer.review(yuewen, zhongwen, **kwargs)


def get_yue_vs_zho_reviewer(
    prompt_cls: type[YueHansReviewPrompt] = YueHansReviewPrompt,
    default_test_cases: list[DualBlockTestCase] | None = None,
    **kwargs: Any,
) -> YueVsZhoReviewer:
    """Get YueZhoReviewer with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        default_test_cases: default test cases
        **kwargs: additional arguments for YueZhoReviewer
    Returns:
        YueZhoReviewer with provided configuration
    """
    if default_test_cases is None:
        default_test_cases = get_default_yue_vs_zho_test_cases(prompt_cls)
    return YueVsZhoReviewer(
        prompt_cls=prompt_cls,
        default_test_cases=default_test_cases,
        **kwargs,
    )
