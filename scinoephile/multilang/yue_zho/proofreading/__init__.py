#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 粤文 proofreading against 中文."""

from __future__ import annotations

from logging import warning
from typing import Any

from scinoephile.core.subtitles import Series
from scinoephile.llms.dual_single import (
    DualSingleProcessor,
    DualSinglePrompt,
    DualSingleTestCase,
)

from .prompts import YueZhoProofreadingPrompt

__all__ = [
    "YueZhoProofreadingPrompt",
    "get_default_yue_vs_zho_proofreading_test_cases",
    "get_yue_vs_zho_proofread",
    "get_yue_vs_zho_proofreader",
]


# noinspection PyUnusedImports
def get_default_yue_vs_zho_proofreading_test_cases(
    prompt_cls: type[DualSinglePrompt] = YueZhoProofreadingPrompt,
) -> list[DualSingleTestCase]:
    """Get default 粤文 proofreading test cases included with package.

    Arguments:
        prompt_cls: text for LLM correspondence
    Returns:
        default test cases
    """
    try:
        from test.data.mlamd import (  # noqa: PLC0415
            get_mlamd_yue_vs_zho_proofreading_test_cases,
        )

        return get_mlamd_yue_vs_zho_proofreading_test_cases(
            prompt_cls=prompt_cls,
            test_case_base_cls=DualSingleTestCase,
        )
    except ImportError as exc:  # pragma: no cover - test data not installed in prod
        warning(f"Default test cases not available for 粤文 proofreading:\n{exc}")
    return []


def get_yue_vs_zho_proofread(
    yuewen: Series,
    zhongwen: Series,
    processor: DualSingleProcessor | None = None,
    **kwargs: Any,
) -> Series:
    """Get 粤文 subtitles proofread against 中文 subtitles.

    Arguments:
        yuewen: 粤文 Series
        zhongwen: 中文 Series
        processor: processor to use
        **kwargs: additional arguments for DualSingleProcessor.process
    Returns:
        Proofread 粤文 subtitles
    """
    if processor is None:
        processor = get_yue_vs_zho_proofreader()
    return processor.process(yuewen, zhongwen, **kwargs)


def get_yue_vs_zho_proofreader(
    prompt_cls: type[YueZhoProofreadingPrompt] = YueZhoProofreadingPrompt,
    default_test_cases: list[DualSingleTestCase] | None = None,
    **kwargs: Any,
) -> DualSingleProcessor:
    """Get DualSingleProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        default_test_cases: default test cases
        **kwargs: additional keyword arguments for DualSingleProcessor
    Returns:
        DualSingleProcessor with provided configuration
    """
    if default_test_cases is None:
        default_test_cases = get_default_yue_vs_zho_proofreading_test_cases(prompt_cls)
    return DualSingleProcessor(
        prompt_cls=prompt_cls,
        default_test_cases=default_test_cases,
        test_case_base_cls=DualSingleTestCase,
        **kwargs,
    )
