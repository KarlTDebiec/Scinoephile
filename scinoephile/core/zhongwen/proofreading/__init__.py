#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 中文 proofreading."""

from __future__ import annotations

from logging import warning
from typing import Any

from scinoephile.core import Series
from scinoephile.core.proofreading import (
    Proofreader,
    ProofreadingPrompt,
    ProofreadingTestCase,
)

from .prompt import ZhongwenSimpProofreadingPrompt, ZhongwenTradProofreadingPrompt

__all__ = [
    "ZhongwenSimpProofreadingPrompt",
    "ZhongwenTradProofreadingPrompt",
    "get_default_zho_proofreading_test_cases",
    "get_zho_proofread",
    "get_zho_proofreader",
]


# noinspection PyUnusedImports
def get_default_zho_proofreading_test_cases(
    prompt_cls: type[ProofreadingPrompt] = ProofreadingPrompt,
) -> list[ProofreadingTestCase]:
    """Get default test cases included with package.

    Arguments:
        prompt_cls: prompt class to use for test cases
    Returns:
        default test cases
    """
    try:
        from test.data.kob import get_kob_zho_proofreading_test_cases
        from test.data.mlamd import get_mlamd_zho_proofreading_test_cases
        from test.data.mnt import get_mnt_zho_proofreading_test_cases
        from test.data.t import get_t_zho_proofreading_test_cases

        return (
            get_kob_zho_proofreading_test_cases(prompt_cls)
            + get_mlamd_zho_proofreading_test_cases(prompt_cls)
            + get_mnt_zho_proofreading_test_cases(prompt_cls)
            + get_t_zho_proofreading_test_cases(prompt_cls)
        )
    except ImportError as exc:
        warning(f"Default test cases not available for 中文 proofreading:\n{exc}")
    return []


def get_zho_proofread(
    series: Series,
    proofreader: Proofreader | None = None,
    **kwargs: Any,
) -> Series:
    """Get 中文 series proofread.

    Arguments:
        series: Series to proofread
        proofreader: Proofreader to use
        kwargs: additional keyword arguments for Proofreader.proofread
    Returns:
        proofread Series
    """
    if proofreader is None:
        proofreader = get_zho_proofreader()
    return proofreader.proofread(series, **kwargs)


def get_zho_proofreader(
    prompt_cls: type[ZhongwenSimpProofreadingPrompt] = ZhongwenSimpProofreadingPrompt,
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
        default_test_cases = get_default_zho_proofreading_test_cases(prompt_cls)
    return Proofreader(
        prompt_cls=prompt_cls,
        default_test_cases=default_test_cases,
        **kwargs,
    )
