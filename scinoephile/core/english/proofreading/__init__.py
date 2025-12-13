#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English proofreading."""

from __future__ import annotations

from collections.abc import Sequence
from logging import warning
from pathlib import Path
from typing import Any

from scinoephile.core.english.proofreading.prompt import EnglishProofreadingPrompt
from scinoephile.core.proofreading import Proofreader, ProofreadingTestCase
from scinoephile.core.series import Series

__all__ = [
    "EnglishProofreadingPrompt",
    "get_default_english_proofreading_test_cases",
    "get_english_proofread",
    "get_english_proofreader",
]


def get_default_english_proofreading_test_cases() -> list[ProofreadingTestCase]:
    """Get default test cases included with package.

    Returns:
        Test cases configured with the English proofreading prompt.
    """
    try:
        from test.data.kob import get_kob_eng_proofreading_test_cases
        from test.data.mlamd import get_mlamd_eng_proofreading_test_cases
        from test.data.mnt import get_mnt_eng_proofreading_test_cases
        from test.data.t import get_t_eng_proofreading_test_cases

        return (
            get_kob_eng_proofreading_test_cases(prompt_cls=EnglishProofreadingPrompt)
            + get_mlamd_eng_proofreading_test_cases(
                prompt_cls=EnglishProofreadingPrompt
            )
            + get_mnt_eng_proofreading_test_cases(prompt_cls=EnglishProofreadingPrompt)
            + get_t_eng_proofreading_test_cases(prompt_cls=EnglishProofreadingPrompt)
        )
    except ImportError as exc:
        warning(
            "Default test cases not available for English proofreading, "
            f"encountered Exception:\n{exc}"
        )
    return []


def get_english_proofreader(
    test_cases: Sequence[ProofreadingTestCase] | None = None,
    test_case_path: Path | None = None,
    auto_verify: bool = False,
) -> Proofreader:
    """Create a proofreader configured for English subtitles.

    Arguments:
        test_cases: test cases
        test_case_path: path to file containing test cases
        auto_verify: automatically verify test cases if they meet selected criteria
    Returns:
        Configured proofreader instance.
    """
    return Proofreader(
        prompt_cls=EnglishProofreadingPrompt,
        test_cases=test_cases,
        test_case_path=test_case_path,
        auto_verify=auto_verify,
        get_default_test_cases=get_default_english_proofreading_test_cases,
    )


def get_english_proofread(
    series: Series, proofreader: Proofreader | None = None, **kwargs: Any
) -> Series:
    """Get English series proofread.

    Arguments:
        series: Series to proofread
        proofreader: proofreader to use
        kwargs: additional keyword arguments for proofreader.proofread
    Returns:
        Proofread Series
    """
    if proofreader is None:
        proofreader = get_english_proofreader()

    return proofreader.proofread(series, **kwargs)
