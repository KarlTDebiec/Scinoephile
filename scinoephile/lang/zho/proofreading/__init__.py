#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 中文 proofreading."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict, Unpack

from scinoephile.llms.default_test_cases import (
    ZHO_HANS_PROOFREADING_JSON_PATHS,
    ZHO_HANT_PROOFREADING_JSON_PATHS,
    load_default_test_cases_from_repo_data,
)
from scinoephile.llms.mono_block import MonoBlockManager, MonoBlockProcessor

from .prompts import ZhoHansProofreadingPrompt, ZhoHantProofreadingPrompt

if TYPE_CHECKING:
    from pathlib import Path

    from scinoephile.core.llms import TestCase
    from scinoephile.core.subtitles import Series

__all__ = [
    "ZhoHansProofreadingPrompt",
    "ZhoHantProofreadingPrompt",
    "ZhoProofreadingProcessKwargs",
    "ZhoProofreadingProcessorKwargs",
    "get_zho_proofread",
    "get_zho_proofreader",
]


class ZhoProofreadingProcessKwargs(TypedDict, total=False):
    """Keyword arguments for MonoBlockProcessor.process."""

    stop_at_idx: int | None


class ZhoProofreadingProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for MonoBlockProcessor initialization."""

    test_case_path: Path | None
    auto_verify: bool


def get_zho_proofread(
    series: Series,
    processor: MonoBlockProcessor | None = None,
    **kwargs: Unpack[ZhoProofreadingProcessKwargs],
) -> Series:
    """Get 中文 series proofread.

    Arguments:
        series: Series to proofread
        processor: MonoBlockProcessor to use
        **kwargs: additional keyword arguments for MonoBlockProcessor.process
    Returns:
        proofread Series
    """
    if processor is None:
        processor = get_zho_proofreader()
    return processor.process(series, **kwargs)


def get_zho_proofreader(
    prompt_cls: type[ZhoHansProofreadingPrompt] = ZhoHansProofreadingPrompt,
    test_cases: list[TestCase] | None = None,
    **kwargs: Unpack[ZhoProofreadingProcessorKwargs],
) -> MonoBlockProcessor:
    """Get MonoBlockProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        **kwargs: additional keyword arguments for MonoBlockProcessor
    Returns:
        MonoBlockProcessor with provided configuration
    """
    if test_cases is None:
        if prompt_cls is ZhoHantProofreadingPrompt:
            test_cases = list(
                load_default_test_cases_from_repo_data(
                    MonoBlockManager,
                    prompt_cls,
                    ZHO_HANT_PROOFREADING_JSON_PATHS,
                )
            )
        else:
            test_cases = list(
                load_default_test_cases_from_repo_data(
                    MonoBlockManager,
                    prompt_cls,
                    ZHO_HANS_PROOFREADING_JSON_PATHS,
                )
            )
    return MonoBlockProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        **kwargs,
    )
