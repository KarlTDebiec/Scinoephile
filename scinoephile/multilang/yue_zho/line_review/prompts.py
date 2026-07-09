#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for written Cantonese line review against standard Chinese."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.dictionaries import DictionaryToolPrompt
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import PromptYueHans, PromptYueHant
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.dual_1_to_1 import Dual1To1Prompt

__all__ = [
    "YueLineReviewVsZhoPromptYueHans",
    "YueLineReviewVsZhoPromptYueHant",
]


class YueLineReviewVsZhoPromptYueHant(
    DictionaryToolPrompt, Dual1To1Prompt, PromptYueHant
):
    """Text for traditional written Cantonese line review against standard Chinese."""

    # Dictionary tool
    dictionary_tool_name: ClassVar[str] = "lookup_dictionary"
    """Name of the dictionary lookup tool."""

    dictionary_tool_description: ClassVar[str] = (
        "查本地詞典入面嘅粵語同普通話詞條。工具會自動判斷查詢係漢字、拼音定粵拼。"
    )
    """Description of the dictionary lookup tool."""

    dictionary_tool_query_description: ClassVar[str] = (
        "要查嘅普通話或者粵語詞語，可以係漢字、拼音或者粵拼。"
    )
    """Description of the dictionary lookup query parameter."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你負責為廣東話語音嘅粵文字幕做校對。
        作為參考，你會見到對應嘅中文字幕。
        你嘅目標係糾正明顯嘅轉寫錯誤，主要係聽錯字、寫錯字，同其他一眼可見嘅轉寫問題。
        唔好為了貼近中文字幕而改寫本來已經正確嘅粵文。
        唔好調整語氣、語法、助詞、量詞或者措辭，除非嗰啲地方本身就係轉寫錯誤。
        只有當你認為原句明顯有誤時，先作修改。
        如果發現粵文同中文字幕完全對唔上，説明呢行粵文係徹底誤寫，
        請回傳字符 "�" 作為粵文，並喺備註説明無對應。

        記住：
        - 粵文轉寫唔需要同中文字幕逐字對應。
        - 講者可能會用唔同嘅粵語講法。
        - 如果唔係轉寫錯誤，意義、語氣同文法嘅差異都可以接受。
        - 如果粵文入面有啲詞同中文字幕睇落唔對應，咁可以查中文字幕入面相關詞語，
          睇下係咪有讀音相近嘅粵語詞被誤寫咗。

        如果你有修改，請用英文一句話説明改動。
        如果冇修改，備註請回傳空字串。""")
    """Base system prompt."""

    # Query fields
    src_1: ClassVar[str] = "yuewen"
    """Name of source one field in query."""

    src_1_desc: ClassVar[str] = "要校對嘅粵文字幕轉寫"
    """Description of source one field in query."""

    src_2: ClassVar[str] = "zhongwen"
    """Name of source two field in query."""

    src_2_desc: ClassVar[str] = "對應嘅中文字幕"
    """Description of source two field in query."""

    # Query validation errors
    src_1_missing_err: ClassVar[str] = "查詢必須包含要校對嘅粵文字幕。"
    """Error when source one field is missing from query."""

    src_2_missing_err: ClassVar[str] = "查詢必須包含中文字幕。"
    """Error when source two field is missing from query."""

    src_1_src_2_equal_err: ClassVar[str] = "兩份來源字幕唔可以完全一樣。"
    """Error when source one and two fields are equal in query."""

    # Answer fields
    output: ClassVar[str] = "xiugai"
    """Name of output field in answer."""

    output_desc: ClassVar[str] = '校對後嘅粵文字幕（如需刪掉請回傳 "�"）'
    """Description of output field in answer."""

    note: ClassVar[str] = "beizhu"
    """Name of note field in answer."""

    note_desc: ClassVar[str] = "改動説明（英文）"
    """Description of note field in answer."""

    # Answer validation errors
    output_missing_note_missing_err: ClassVar[str] = (
        "答案必須包含改動説明（如無改動請回傳空字串）。"
    )
    """Error when output and note fields are both missing from answer."""


class YueLineReviewVsZhoPromptYueHans(YueLineReviewVsZhoPromptYueHant, PromptYueHans):
    """Text for simplified written Cantonese line review against standard Chinese."""

    opencc_config = OpenCCConfig.hk2s
    """Config for converting traditional Chinese characters from the parent class."""
