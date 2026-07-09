#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for standard Chinese/written Cantonese translation prompts."""

from __future__ import annotations

from typing import ClassVar

from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.zho.prompts import PromptZhoHant
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.gap_translation import GapTranslationPrompt
from scinoephile.llms.guided_translation import GuidedTranslationPrompt
from scinoephile.llms.translation import TranslationPrompt

__all__ = [
    "ZhoYueTranslationPromptZhoHans",
    "ZhoYueTranslationPromptZhoHant",
    "ZhoYueGapTranslationPromptZhoHans",
    "ZhoYueGapTranslationPromptZhoHant",
    "ZhoYueGuidedTranslationPromptZhoHans",
    "ZhoYueGuidedTranslationPromptZhoHant",
]


class ZhoYueTranslationPromptZhoHant(TranslationPrompt, PromptZhoHant):
    """Text for traditional standard Chinese translation from written Cantonese."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你負責根據粵文字幕，創作對應的標準中文字幕。

        每條粵文字幕都要輸出一條標準中文字幕。譯文要自然、通順，準確表達粵文字幕
        的意思、語氣、戲劇意圖和說話人意圖。不要逐字硬譯；可以調整措辭，使其
        更像自然的標準中文字幕。專名、固定稱呼、重複術語和字幕標記要在適合時
        保留或按標準中文習慣處理。

        輸出內容只能是生成的中文字幕正文。不要附加英文、備註、解釋、標籤、
        替代譯文、方括號內容、括號內容，或任何字幕以外的說明。
        """)
    """Base system prompt."""

    # Query fields
    input_pfx: ClassVar[str] = "yuewen_"
    """Prefix for written Cantonese source fields in query."""

    input_desc_tpl: ClassVar[str] = "要翻譯成標準中文的粵文字幕 {idx}"
    """Description template for written Cantonese source fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for generated standard Chinese output fields in answer."""

    output_desc_tpl: ClassVar[str] = "字幕 {idx} 對應的標準中文譯文"
    """Description template for generated standard Chinese output fields."""


class ZhoYueTranslationPromptZhoHans(ZhoYueTranslationPromptZhoHant):
    """Text for simplified standard Chinese translation from written Cantonese."""

    opencc_config = OpenCCConfig.t2s
    """Config for converting traditional Chinese characters from the parent class."""


class ZhoYueGapTranslationPromptZhoHant(GapTranslationPrompt, PromptZhoHant):
    """Text for traditional standard Chinese gap translation using Cantonese."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你負責根據對應的粵文字幕，補翻譯缺失的標準中文字幕。
        只有當某行現有中文字幕爲空字符串時，才需要提供譯文。
        如果某行已經有中文內容，不要修改，該行請輸出空字符串。
        譯文要自然、通順，語氣和用詞要儘量貼近附近已有的中文字幕。
        粵文字幕是意思來源；譯文不需要逐字對應，但要準確表達該行意思。
        輸出內容只能是字幕正文本身，不要附加英文、備註、解釋、標籤、
        方括號內容、括號內容，或任何譯文以外的說明。
        如果不需要翻譯，就輸出空字符串。
        """)
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for source one fields in query."""

    src_1_desc_tpl: ClassVar[str] = "字幕 {idx} 現有的中文內容；如果爲空就代表要翻譯"
    """Description template for source one fields in query."""

    src_2_pfx: ClassVar[str] = "yuewen_"
    """Prefix for source two fields in query."""

    src_2_desc_tpl: ClassVar[str] = "字幕 {idx} 對應的粵文字幕"
    """Description template for source two fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = (
        '字幕 {idx} 譯好後的標準中文正文；如果不需要翻譯請輸出 ""。'
        "不要包含英文、備註、解釋、標籤或者括號說明。"
    )
    """Description template for output fields in answer."""

    # Test case validation errors
    output_unmodified_err_tpl: ClassVar[str] = (
        "字幕 {idx} 已經有中文內容，該行輸出必須爲空字符串。"
    )
    """Error template when output is present but unmodified relative to source one."""

    output_contains_note_err_tpl: ClassVar[str] = (
        "字幕 {idx} 包含英文或者備註說明；只可以輸出中文字幕正文。"
    )
    """Error template when output includes leaked note text."""

    @classmethod
    def output_contains_note_err(cls, idx: int) -> str:
        """Error when output includes note-like text."""
        return cls.output_contains_note_err_tpl.format(idx=idx)


class ZhoYueGapTranslationPromptZhoHans(ZhoYueGapTranslationPromptZhoHant):
    """Text for simplified standard Chinese gap translation using Cantonese."""

    opencc_config = OpenCCConfig.t2s
    """Config for converting traditional Chinese characters from the parent class."""


class ZhoYueGuidedTranslationPromptZhoHant(GuidedTranslationPrompt, PromptZhoHant):
    """Text for traditional guided standard Chinese translation from Cantonese."""

    # Prompt
    base_system_prompt: ClassVar[str] = dedent_and_compact("""
        你負責根據粵文字幕，創作對應的標準中文字幕。你也會收到同一段場景的
        既有中文字幕，作爲參考材料。

        每條粵文字幕都要輸出一條標準中文字幕。譯文要準確表達粵文字幕的意思、
        語氣、戲劇意圖和說話人意圖。既有中文字幕是角色名、專名、重複術語、
        語域和固定說法的參考；當它和粵文字幕意思兼容時，儘量沿用。
        如果粵文字幕和既有中文字幕有差異，要優先按粵文意思翻譯，同時保留
        已經建立好的名詞和稱呼。

        輸出內容只能是生成的中文字幕正文。不要附加英文、備註、解釋、標籤、
        替代譯文、方括號內容、括號內容，或任何字幕以外的說明。
        """)
    """Base system prompt."""

    # Query fields
    src_1_pfx: ClassVar[str] = "yuewen_"
    """Prefix for written Cantonese source fields in query."""

    src_1_desc_tpl: ClassVar[str] = "要翻譯成標準中文的粵文字幕 {idx}"
    """Description template for written Cantonese source fields in query."""

    src_2_pfx: ClassVar[str] = "zhongwen_reference_"
    """Prefix for standard Chinese reference fields in query."""

    src_2_desc_tpl: ClassVar[str] = "同一段場景的既有標準中文參考字幕 {idx}"
    """Description template for standard Chinese reference fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "zhongwen_"
    """Prefix for generated standard Chinese output fields in answer."""

    output_desc_tpl: ClassVar[str] = "字幕 {idx} 對應的標準中文譯文"
    """Description template for generated standard Chinese output fields."""


class ZhoYueGuidedTranslationPromptZhoHans(ZhoYueGuidedTranslationPromptZhoHant):
    """Text for simplified guided standard Chinese translation from Cantonese."""

    opencc_config = OpenCCConfig.t2s
    """Config for converting traditional Chinese characters from the parent class."""
