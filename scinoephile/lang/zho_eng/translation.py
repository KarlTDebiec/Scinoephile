#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for standard Chinese/English translation prompts."""

from __future__ import annotations

from functools import partial

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.zho.prompts import ZHO_HANT_PROMPT_FIELDS
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_text_converted
from scinoephile.llms.gap_translation import GapTranslationPrompt
from scinoephile.llms.guided_translation import GuidedTranslationPrompt
from scinoephile.llms.translation import TranslationPrompt

__all__ = [
    "ZhoEngTranslationPromptZhoHans",
    "ZhoEngTranslationPromptZhoHant",
    "ZhoEngGapTranslationPromptZhoHans",
    "ZhoEngGapTranslationPromptZhoHant",
    "ZhoEngGuidedTranslationPromptZhoHans",
    "ZhoEngGuidedTranslationPromptZhoHant",
]


ZhoEngTranslationPromptZhoHant = TranslationPrompt(
    language=Language.zho_hant,
    **ZHO_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責根據英文字幕，創作對應的標準中文字幕。

        每條英文字幕都要輸出一條標準中文字幕。譯文要自然、通順，準確表達英文字幕
        的意思、語氣、戲劇意圖和說話人意圖。不要逐字硬譯；可以調整措辭，使其
        更像自然的中文字幕。專名、固定稱呼、重複術語和字幕標記要在適合時保留
        或按中文習慣處理。

        每個輸出項目的文本欄只能是生成的中文字幕正文。不要附加備註、解釋、標籤、
        替代譯文、方括號內容、括號內容，或任何字幕以外的說明。
        """),
    subtitles="eng",
    subtitles_desc="按順序排列、要翻譯成標準中文的英文字幕",
    outputs="zhongwen",
    outputs_desc="按輸入字幕順序排列的標準中文譯文",
    index="xuhao",
    index_desc="從 1 開始的字幕序號",
    text="wenben",
    subtitle_text_desc="要翻譯成標準中文的英文字幕文本",
    output_text_desc="完整標準中文譯文",
    subtitle_indices_err="查詢字幕序號必須從 1 開始、連續並按順序排列。",
    output_indices_err="答案輸出序號必須從 1 開始、連續並按順序排列。",
    output_correspondence_err="答案輸出序號必須與查詢字幕序號完全對應。",
)
"""Text for traditional standard Chinese translation from English."""

ZhoEngTranslationPromptZhoHans = ZhoEngTranslationPromptZhoHant.transformed(
    Language.zho_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.t2s),
)
"""Text for simplified standard Chinese translation from English."""

ZhoEngGapTranslationPromptZhoHant = GapTranslationPrompt(
    language=Language.zho_hant,
    **ZHO_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責根據對應的英文字幕，補翻譯缺失的標準中文字幕。
        只為現有中文字幕列表中缺失的序號提供譯文。每個缺失序號必須恰好返回
        一項輸出；已有中文內容的序號不要返回輸出，也不要修改。
        譯文要自然、通順，語氣和用詞要儘量貼近附近已有的中文字幕。
        英文字幕是意思來源；譯文不需要逐字對應，但要準確表達該行意思。
        輸出內容只能是字幕正文本身，不要附加英文、備註、解釋、標籤、
        方括號內容、括號內容，或任何譯文以外的說明。
        如果某個缺失序號不需要中文字幕，仍要保留該輸出項目，文本使用空字符串。
        """),
    targets="zhongwen",
    targets_desc="已有的中文字幕，序號與英文參考字幕一致",
    guides="eng",
    guides_desc="按序號完整排列的英文參考字幕",
    outputs="zhongwen",
    outputs_desc="現有中文字幕缺失序號所需的標準中文譯文",
    index="xuhao",
    index_desc="從 1 開始的字幕序號",
    text="wenben",
    target_text_desc="已有的中文字幕文本",
    guide_text_desc="英文參考字幕文本",
    output_text_desc="缺失序號對應的標準中文譯文正文；如果不需要字幕則使用空字符串",
    guide_indices_err="查詢參考字幕序號必須從 1 開始、連續並按順序排列。",
    target_indices_err="查詢現有字幕序號必須唯一並按升序排列。",
    target_index_missing_err="每個查詢現有字幕序號都必須對應一個參考字幕序號。",
    target_gap_missing_err="查詢現有字幕必須缺少至少一個需要翻譯的參考字幕序號。",
    output_indices_err="答案輸出序號必須唯一並按升序排列。",
    output_indices_mismatch_err="答案輸出序號必須恰好對應查詢現有字幕缺失的參考字幕序號。",
)
"""Text for traditional standard Chinese gap translation using English."""

ZhoEngGapTranslationPromptZhoHans = ZhoEngGapTranslationPromptZhoHant.transformed(
    Language.zho_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.t2s),
)
"""Text for simplified standard Chinese gap translation using English."""

ZhoEngGuidedTranslationPromptZhoHant = GuidedTranslationPrompt(
    language=Language.zho_hant,
    **ZHO_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責根據英文字幕，創作對應的標準中文字幕。你也會收到同一段場景的
        既有中文字幕，作爲參考材料。

        每條英文字幕都要輸出一條標準中文字幕。譯文要準確表達英文字幕的意思、
        語氣、戲劇意圖和說話人意圖。既有中文字幕是角色名、專名、重複術語、
        語域和固定說法的參考；當它和英文字幕意思兼容時，儘量沿用。
        如果英文字幕和既有中文字幕有差異，要優先按英文意思翻譯，同時保留
        已經建立好的名詞和稱呼。

        每個輸出項目的文本欄只能是生成的中文字幕正文。不要附加英文、備註、解釋、
        標籤、替代譯文、方括號內容、括號內容，或任何字幕以外的說明。
        """),
    subtitles="eng",
    subtitles_desc="按順序排列、要翻譯成標準中文的英文字幕",
    guides="zhongwen_reference",
    guides_desc="同一段場景的既有標準中文參考字幕",
    outputs="zhongwen",
    outputs_desc="和查詢英文字幕逐一對應的標準中文譯文",
    index="xuhao",
    index_desc="從 1 開始的字幕序號",
    text="wenben",
    subtitle_text_desc="要翻譯成標準中文的英文字幕文本",
    guide_text_desc="同一段場景的既有標準中文參考字幕文本",
    output_text_desc="和查詢英文字幕對應的標準中文譯文文本",
    guide_indices_err="查詢參考字幕序號必須從 1 開始、連續並按順序排列。",
    subtitle_indices_err="查詢字幕序號必須從 1 開始、連續並按順序排列。",
    output_indices_err="答案輸出序號必須從 1 開始、連續並按順序排列。",
    output_correspondence_err="答案輸出序號必須與查詢字幕序號完全對應。",
)
"""Text for traditional guided standard Chinese translation from English."""

ZhoEngGuidedTranslationPromptZhoHans = ZhoEngGuidedTranslationPromptZhoHant.transformed(
    Language.zho_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.t2s),
)
"""Text for simplified guided standard Chinese translation from English."""
