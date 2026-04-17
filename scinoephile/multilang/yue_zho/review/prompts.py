#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for 粤文 review against 中文."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import YueHansPrompt
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.llms.dual_block import DualBlockPrompt
from scinoephile.multilang.dictionaries.dictionary_tool_prompt import (
    DictionaryToolPrompt,
)

__all__ = [
    "YueHansReviewPrompt",
    "YueHantReviewPrompt",
]


class YueHansReviewPrompt(DictionaryToolPrompt, DualBlockPrompt, YueHansPrompt):
    """Text for LLM correspondence for 简体粤文 review against 中文."""

    # Dictionary tool
    dictionary_tool_name: ClassVar[str] = "lookup_dictionary"
    """Name of the dictionary lookup tool."""

    dictionary_tool_description: ClassVar[str] = (
        "查本地词典入面嘅粤语同普通话词条。工具会自动判断查询系汉字、拼音定粤拼。"
    )
    """Description of the dictionary lookup tool."""

    dictionary_tool_query_description: ClassVar[str] = (
        "要查嘅普通话或者粤语词语，可以系汉字、拼音或者粤拼。"
    )
    """Description of the dictionary lookup query parameter."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你负责为广东话语音嘅粤文字幕做最后审核。
        呢一轮唔系重写字幕，而系做最后一层把关，只处理仍然明显有问题嘅粤文转写。
        请专注检查转写是否准确，尤其系听错字、写错字、人物称呼前后唔一致，或者同整套字幕其他地方明显冲突嘅情况。
        唔好评审文风、文法、语气或者措辞；如果原句本身已经系合理嘅粤语讲法，就唔好改。
        中文字幕只系参考，唔需要同粤文逐字对应。
        对于每一条粤文字幕，只有当你认为确实需要修改时，先回传修订后嘅完整粤文字幕。
        如果某条粤文字幕唔需要修改，请为该字幕回传空字串。
        如果有修改，请同时用英文附上一段简短备注，说明你改咗乜嘢。
        如果冇需要修改，备注栏同样回传空字串。
    """)
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "yuewen_"
    """Prefix for source one fields in query."""

    src_1_desc_tpl: ClassVar[str] = "字幕 {idx} 嘅粤文转写"
    """Description template for source one fields in query."""

    src_2_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for source two fields in query."""

    src_2_desc_tpl: ClassVar[str] = "字幕 {idx} 已知嘅中文字幕"
    """Description template for source two fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "xiugai_yuewen_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = (
        '字幕 {idx} 修订后嘅粤文；如果冇任何修改，请回传 ""。'
    )
    """Description template for output fields in answer."""

    note_pfx: ClassVar[str] = "beizhu_"
    """Prefix for note fields in answer."""

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


class YueHantReviewPrompt(YueHansReviewPrompt):
    """Text for LLM correspondence for 繁体粤文 review against 中文."""

    opencc_config = OpenCCConfig.s2hk
    """Config with which to convert characters from 简体中文 present in parent class."""
