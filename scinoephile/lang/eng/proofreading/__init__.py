#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to English proofreading."""

from __future__ import annotations

from logging import getLogger
from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.subtitles import Series
from scinoephile.llms.base import TestCase
from scinoephile.llms.base.default_test_cases import (
    load_default_test_cases_from_repo_data,
)
from scinoephile.llms.mono_block import MonoBlockProcessor, MonoBlockPrompt
from scinoephile.llms.mono_block.manager import MonoBlockManager

from .prompts import EngProofreadingPrompt

__all__ = [
    "EngProofreadingPrompt",
    "EngProofreadingProcessKwargs",
    "EngProofreadingProcessorKwargs",
    "get_default_eng_proofreading_test_cases",
    "get_eng_proofread",
    "get_eng_proofreader",
]


logger = getLogger(__name__)

_ENG_PROOFREADING_JSON_PATHS = [
    Path("kob/lang/eng/proofreading/eng_ocr.json"),
    Path("kob/lang/eng/proofreading/eng_srt.json"),
    Path("mlamd/lang/eng/proofreading.json"),
    Path("mnt/lang/eng/proofreading.json"),
    Path("t/lang/eng/proofreading.json"),
]


class EngProofreadingProcessKwargs(TypedDict, total=False):
    """Keyword arguments for MonoBlockProcessor.process."""

    stop_at_idx: int | None


class EngProofreadingProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for MonoBlockProcessor initialization."""

    test_case_path: Path | None
    auto_verify: bool


def get_default_eng_proofreading_test_cases(
    prompt_cls: type[MonoBlockPrompt] = MonoBlockPrompt,
) -> list[TestCase]:
    """Get default test cases included with package.

    Arguments:
        prompt_cls: text for LLM correspondence
    Returns:
        default test cases
    """
    return load_default_test_cases_from_repo_data(
        MonoBlockManager,
        prompt_cls,
        _ENG_PROOFREADING_JSON_PATHS,
    )


def get_eng_proofread(
    series: Series,
    processor: MonoBlockProcessor | None = None,
    **kwargs: Unpack[EngProofreadingProcessKwargs],
) -> Series:
    """Get English series proofread.

    Arguments:
        series: Series to proofread
        processor: MonoBlockProcessor to use
        **kwargs: additional keyword arguments for MonoBlockProcessor.process
    Returns:
        proofread Series
    """
    if processor is None:
        processor = get_eng_proofreader()
    return processor.process(series, **kwargs)


def get_eng_proofreader(
    prompt_cls: type[EngProofreadingPrompt] = EngProofreadingPrompt,
    test_cases: list[TestCase] | None = None,
    **kwargs: Unpack[EngProofreadingProcessorKwargs],
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
        test_cases = get_default_eng_proofreading_test_cases(prompt_cls)
    return MonoBlockProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        **kwargs,
    )
