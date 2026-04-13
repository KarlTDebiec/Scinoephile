#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Code related to 粤文 vs. 中文 proofreading."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.core.llms import TestCase
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    YUE_ZHO_PROOFREADING_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.multilang.dictionaries.dictionary_tools import get_dictionary_tooling

from .manager import YueZhoProofreadingManager
from .processor import YueZhoProofreadingProcessor
from .prompts import YueZhoHansProofreadingPrompt, YueZhoHantProofreadingPrompt

__all__ = [
    "YueZhoHansProofreadingPrompt",
    "YueZhoHantProofreadingPrompt",
    "YueZhoProofreadingManager",
    "YueZhoProofreadingProcessKwargs",
    "YueZhoProofreadingProcessor",
    "YueZhoProofreadingProcessorKwargs",
    "get_yue_vs_zho_proofread",
    "get_yue_vs_zho_proofreader",
]


class YueZhoProofreadingProcessKwargs(TypedDict, total=False):
    """Keyword arguments for YueZhoProofreadingProcessor.process."""

    stop_at_idx: int | None


class YueZhoProofreadingProcessorKwargs(TypedDict, total=False):
    """Keyword arguments for YueZhoProofreadingProcessor initialization."""

    test_case_path: Path | None
    auto_verify: bool


def get_yue_vs_zho_proofread(
    yuewen: Series,
    zhongwen: Series,
    processor: YueZhoProofreadingProcessor | None = None,
    **kwargs: Unpack[YueZhoProofreadingProcessKwargs],
) -> Series:
    """Get 粤文 subtitles proofread against 中文 subtitles.

    Arguments:
        yuewen: 粤文 Series
        zhongwen: 中文 Series
        processor: processor to use
        **kwargs: additional keyword arguments for YueZhoProofreadingProcessor.process
    Returns:
        proofread 粤文 subtitles
    """
    if processor is None:
        processor = get_yue_vs_zho_proofreader()
    return processor.process(yuewen, zhongwen, **kwargs)


def get_yue_vs_zho_proofreader(
    prompt_cls: type[YueZhoHansProofreadingPrompt] = YueZhoHansProofreadingPrompt,
    test_cases: list[TestCase] | None = None,
    use_dictionary_tool: bool = True,
    **kwargs: Unpack[YueZhoProofreadingProcessorKwargs],
) -> YueZhoProofreadingProcessor:
    """Get YueZhoProofreadingProcessor with provided configuration.

    Arguments:
        prompt_cls: text for LLM correspondence
        test_cases: test cases
        use_dictionary_tool: whether to wire the dictionary lookup tool
        **kwargs: additional keyword arguments for YueZhoProofreadingProcessor
    Returns:
        YueZhoProofreadingProcessor with provided configuration
    """
    if test_cases is None:
        test_cases = list(
            load_default_test_cases(
                YueZhoProofreadingManager,
                prompt_cls,
                YUE_ZHO_PROOFREADING_JSON_PATHS,
            )
        )
    tools = None
    tool_handlers = None
    if use_dictionary_tool:
        tools, tool_handlers = get_dictionary_tooling()
    return YueZhoProofreadingProcessor(
        prompt_cls=prompt_cls,
        test_cases=test_cases,
        tools=tools,
        tool_handlers=tool_handlers,
        **kwargs,
    )
