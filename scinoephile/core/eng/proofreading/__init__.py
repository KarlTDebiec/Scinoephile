#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English proofreading."""

from __future__ import annotations

from logging import warning
from typing import Any

from scinoephile.core import Series
from scinoephile.core.proofreading import (
    Proofreader,
    ProofreadingPrompt,
    ProofreadingTestCase,
)

from .prompt import EngProofreadingPrompt

__all__ = [
    "EngProofreadingPrompt",
    "get_default_eng_proofreading_test_cases",
    "get_eng_proofread",
    "get_eng_proofreader",
]


# noinspection PyUnusedImports
def get_default_eng_proofreading_test_cases(
    prompt_cls: type[ProofreadingPrompt] = ProofreadingPrompt,
) -> list[ProofreadingTestCase]:
    """Get default English proofreading test cases included with package.

    Arguments:
        prompt_cls: prompt class to use for test cases
    Returns:
        default test cases
    """
    try:
        from test.data.kob import get_kob_eng_proofreading_test_cases
        from test.data.mlamd import get_mlamd_eng_proofreading_test_cases
        from test.data.mnt import get_mnt_eng_proofreading_test_cases
        from test.data.t import get_t_eng_proofreading_test_cases

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
    proofreader: Proofreader | None = None,
    **kwargs: Any,
) -> Series:
    """Get English series proofread.

    Arguments:
        series: Series to proofread
        proofreader: Proofreader to use
        kwargs: additional keyword arguments for Proofreader.proofread
    Returns:
        proofread Series
    """
    if proofreader is None:
        proofreader = get_eng_proofreader()
    return proofreader.proofread(series, **kwargs)


def get_eng_proofreader(
    prompt_cls: type[EngProofreadingPrompt] = EngProofreadingPrompt,
    default_test_cases: list[ProofreadingTestCase] | None = None,
    **kwargs: Any,
) -> Proofreader:
    """Get a Proofreader with provided configuration.

    Arguments:
        prompt_cls: prompt
        default_test_cases: default test cases
        kwargs: additional keyword arguments for Proofreader
    Returns:
        Proofreader with provided configuration
    """
    if default_test_cases is None:
        default_test_cases = get_default_eng_proofreading_test_cases(prompt_cls)
    return Proofreader(
        prompt_cls=prompt_cls,
        default_test_cases=default_test_cases,
        **kwargs,
    )
