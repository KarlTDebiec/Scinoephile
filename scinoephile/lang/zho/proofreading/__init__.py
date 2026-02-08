#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 中文 proofreading."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.subtitles import Series
from scinoephile.llms.base import TestCase
from scinoephile.llms.mono_block import MonoBlockProcessor, MonoBlockPrompt
from scinoephile.llms.mono_block.manager import MonoBlockManager
from scinoephile.testing.default_test_cases import (
    ZHO_HANS_PROOFREADING_JSON_PATHS,
    ZHO_HANT_PROOFREADING_JSON_PATHS,
    load_default_test_cases_from_repo_data,
)

from .prompts import ZhoHansProofreadingPrompt, ZhoHantProofreadingPrompt

__all__ = [
    "ZhoHansProofreadingPrompt",
    "ZhoHantProofreadingPrompt",
    "ZhoProofreadingProcessKwargs",
    "ZhoProofreadingProcessorKwargs",
    "get_default_zho_proofreading_test_cases",
    "get_zho_proofread",
    "get_zho_proofreader",
]


logger = getLogger(__name__)


class ZhoProofreadingProcessKwargs(TypedDict, total=False):
    """Keyword arguments for MonoBlockProcessor.process."""

    stop_at_idx: int | None


class ZhoProofreadingProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for MonoBlockProcessor initialization."""

    test_case_path: Path | None
    auto_verify: bool


def get_default_zho_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = MonoBlockPrompt,
) -> list[TestCase]:
    """Get default test cases included with package.

    Arguments:
        prompt_cls: text for LLM correspondence
    Returns:
        default test cases
    """
    if prompt_cls is ZhoHantProofreadingPrompt:
        return load_default_test_cases_from_repo_data(
            MonoBlockManager,
            prompt_cls,
            ZHO_HANT_PROOFREADING_JSON_PATHS,
        )
    return load_default_test_cases_from_repo_data(
        MonoBlockManager,
        prompt_cls,
        ZHO_HANS_PROOFREADING_JSON_PATHS,
    )


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
        test_cases = get_default_zho_proofreading_test_cases(prompt_cls)
    return MonoBlockProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        **kwargs,
    )
