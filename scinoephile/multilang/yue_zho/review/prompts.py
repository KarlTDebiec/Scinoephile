#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM correspondence text for 粤文 review against 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.many_to_many_blockwise import ManyToManyBlockwisePrompt
from scinoephile.core.text import get_dedented_and_compacted_multiline_text
from scinoephile.lang.yue.prompts import YueHansPrompt
from scinoephile.lang.zho.conversion import OpenCCConfig

__all__ = [
    "YueHansReviewPrompt",
    "YueHantReviewPrompt",
]


class YueHansReviewPrompt(ManyToManyBlockwisePrompt, YueHansPrompt):
    """LLM correspondence text for 简体粤文 review against 中文."""

    # Prompt
    base_system_prompt: ClassVar[str] = get_dedented_and_compacted_multiline_text("""
        你负责为广东话语音嘅粤文字幕做最后审核。
        每一条粤文字幕都已经同对应嘅中文字幕逐条校对过，而喺该对字幕入面出现嘅差异亦已经处理好。
        你而家要专注处理一啲可能喺单独对照时未必察觉到、但喺通盘检视成套字幕时会显现出嚟嘅粤文字幕问题。
        你唔需要评审写作质素、文法或者风格，只需要确保粤文转写嘅正确性。
        请记住，粤文字幕系广东话口语嘅转写，而中文字幕唔需要同粤文逐字对应。
        对于每一条粤文字幕，如果你认为需要修改，请回传修订后嘅完整粤文字幕。
        如果某条粤文字幕唔需要修改，请为该字幕回传空字串。
        如果有修改，请同时用英文附上一段备注，解释你作出咗啲乜嘢改动。
        如果冇需要修改，备注栏同样回传空字串。
    """)
    """Base system prompt."""

    # Query fields
    source_one_pfx: ClassVar[str] = "yuewen_"
    """Prefix for source one fields in query."""

    source_one_desc_tpl: ClassVar[str] = "字幕 {idx} 嘅粤文转写"
    """Description template for subtitle fields in query."""

    source_two_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for source two fields in query."""

    source_two_desc_tpl: ClassVar[str] = "字幕 {idx} 已知嘅中文字幕"
    """Description template for subtitle fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "xiugai_yuewen_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = (
        '字幕 {idx} 修订后嘅粤文；如果冇任何修改，请回传 ""。'
    )
    """Description template for output fields in answer."""

    note_pfx: ClassVar[str] = "beizhu_"
    """Prefix of note fields in answer."""

    note_desc_tpl: ClassVar[str] = (
        '字幕 {idx} 嘅备注（英文）；如果冇任何修改，请回传 ""。'
    )
    """Description template for note fields in answer."""

    # Test case validation errors
    output_unmodified_err_tpl: ClassVar[str] = (
        "答案入面嘅输出 {idx} 同查询入面嘅来源一 {idx} 完全一样；"
        '如果冇修改，必须回传 ""。'
    )
    """Error template when output is present but unmodified relative to source one."""

    output_missing_note_present_err_tpl: ClassVar[str] = (
        "答案入面嘅输出 {idx} 同查询入面嘅来源一 {idx} 完全一样，"
        '但却提供咗备注；如果输出系 ""，就唔可以有任何备注。'
    )
    """Error template when output is missing but note is present."""

    output_present_note_missing_err_tpl: ClassVar[str] = (
        "答案入面嘅输出 {idx} 相对于查询入面嘅来源一 {idx} 有所修改，"
        "但冇提供任何备注；如果有输出，就必须同时提供备注。"
    )
    """Error template when output is present but note is missing."""


class YueHantReviewPrompt:
    """LLM correspondence text for 繁体粤文 review against 中文."""

    opencc_config = OpenCCConfig.s2hk
    """Config with which to convert characters from 简体中文 present in parent class."""
