#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 中文 proofreading."""

from __future__ import annotations

from collections.abc import Sequence
from logging import warning
from pathlib import Path
from typing import Any

from scinoephile.core.proofreading import Proofreader, ProofreadingTestCase
from scinoephile.core.series import Series
from scinoephile.core.zhongwen.proofreading.prompt import ZhongwenProofreadingPrompt

__all__ = [
    "ZhongwenProofreadingPrompt",
    "get_default_zhongwen_proofreading_test_cases",
    "get_zhongwen_proofread",
    "get_zhongwen_proofreader",
]


def get_default_zhongwen_proofreading_test_cases() -> list[ProofreadingTestCase]:
    """Get default test cases included with package.

    Returns:
        Test cases configured with the 中文 proofreading prompt.
    """
    try:
        from test.data.kob import get_kob_zho_proofreading_test_cases
        from test.data.mlamd import get_mlamd_zho_proofreading_test_cases
        from test.data.mnt import get_mnt_zho_proofreading_test_cases
        from test.data.t import get_t_zho_proofreading_test_cases

        return (
            get_kob_zho_proofreading_test_cases(prompt_cls=ZhongwenProofreadingPrompt)
            + get_mlamd_zho_proofreading_test_cases(
                prompt_cls=ZhongwenProofreadingPrompt
            )
            + get_mnt_zho_proofreading_test_cases(prompt_cls=ZhongwenProofreadingPrompt)
            + get_t_zho_proofreading_test_cases(prompt_cls=ZhongwenProofreadingPrompt)
        )
    except ImportError as exc:
        warning(
            "Default test cases not available for 中文 proofreading, "
            f"encountered Exception:\n{exc}"
        )
    return []


def get_zhongwen_proofreader(
    test_cases: Sequence[ProofreadingTestCase] | None = None,
    test_case_path: Path | None = None,
    auto_verify: bool = False,
) -> Proofreader:
    """Create a proofreader configured for 中文 subtitles.

    Arguments:
        test_cases: test cases
        test_case_path: path to file containing test cases
        auto_verify: automatically verify test cases if they meet selected criteria
    Returns:
        Configured proofreader instance.
    """
    return Proofreader(
        prompt_cls=ZhongwenProofreadingPrompt,
        test_cases=test_cases,
        test_case_path=test_case_path,
        auto_verify=auto_verify,
        get_default_test_cases=get_default_zhongwen_proofreading_test_cases,
    )


def get_zhongwen_proofread(
    series: Series, proofreader: Proofreader | None = None, **kwargs: Any
) -> Series:
    """Get 中文 series proofread.

    Arguments:
        series: Series to proofread
        proofreader: proofreader to use
        kwargs: additional keyword arguments for proofreader.proofread
    Returns:
        Proofread Series
    """
    if proofreader is None:
        proofreader = get_zhongwen_proofreader()

    return proofreader.proofread(series, **kwargs)
