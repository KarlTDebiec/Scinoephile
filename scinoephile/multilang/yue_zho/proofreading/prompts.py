#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 粤文 proofreading against 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.lang.yue.prompts import YueHansPrompt
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.llms.dual_single import DualSinglePrompt

__all__ = [
    "YueZhoHansProofreadingPrompt",
    "YueZhoHantProofreadingPrompt",
]


class YueZhoHansProofreadingPrompt(DualSinglePrompt, YueHansPrompt):
    """Text for LLM correspondence for 简体粤文 proofreading against 中文."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        你负责为广东话语音嘅粤文字幕做校对。
        作为参考，你会见到对应嘅中文字幕。
        你嘅目标系纠正明显嘅转写错误，主要系听错字、写错字。
        唔好为了贴近中文字幕而改写正确嘅粤文。
        唔好调整语气、语法或者量词，除非明显系转写错误。
        只可以喺有合理嘅同音误听情况下先更正（例如：临盘 vs. 临盆）。
        如果发现粤文同中文字幕完全对唔上，说明呢行粤文系彻底误写，
        请回传字符 "�" 作为粤文，并喺备注说明无对应。

        记住：
        - 粤文转写唔需要同中文字幕逐字对应。
        - 讲者可能会用唔同嘅粤语讲法。
        - 如果唔系转写错误，意义、语气同文法嘅差异都可以接受。

        如果你有修改，请用英文一句话说明改动。
        如果冇修改，备注请回传空字串。""")
    """Base system prompt."""

    # Query fields
    src_1: ClassVar[str] = "yuewen"
    """Name of source one field in query."""

    src_1_desc: ClassVar[str] = "要校对嘅粤文字幕转写"
    """Description of source one field in query."""

    src_2: ClassVar[str] = "zhongwen"
    """Name of source two field in query."""

    src_2_desc: ClassVar[str] = "对应嘅中文字幕"
    """Description of source two field in query."""

    # Query validation errors
    src_1_missing_err: ClassVar[str] = "查询必须包含要校对嘅粤文字幕。"
    """Error when source one field is missing from query."""

    src_2_missing_err: ClassVar[str] = "查询必须包含中文字幕。"
    """Error when source two field is missing from query."""

    src_1_src_2_equal_err: ClassVar[str] = "两份来源字幕唔可以完全一样。"
    """Error when source one and two fields are equal in query."""

    # Answer fields
    output: ClassVar[str] = "xiugai"
    """Name of output field in answer."""

    output_desc: ClassVar[str] = '校对后嘅粤文字幕（如需删掉请回传 "�"）'
    """Description of output field in answer."""

    note: ClassVar[str] = "beizhu"
    """Name of note field in answer."""

    note_desc: ClassVar[str] = "改动说明（英文）"
    """Description of note field in answer."""

    # Answer validation errors
    output_missing_note_missing_err: ClassVar[str] = (
        "答案必须包含改动说明（如无改动请回传空字串）。"
    )
    """Error when output and note fields are both missing from answer."""


class YueZhoHantProofreadingPrompt(YueZhoHansProofreadingPrompt):
    """Text for LLM correspondence for 繁体粤文 proofreading against 中文."""

    opencc_config = OpenCCConfig.s2hk
    """Config with which to convert characters from 简体中文 present in parent class."""
