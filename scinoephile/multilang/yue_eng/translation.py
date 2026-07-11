#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for written Cantonese/English translation prompts."""

from __future__ import annotations

from functools import partial

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import YUE_HANT_PROMPT_FIELDS
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_text_converted
from scinoephile.llms.gap_translation import GapTranslationPrompt
from scinoephile.llms.guided_translation import GuidedTranslationPrompt
from scinoephile.llms.translation import TranslationPrompt

__all__ = [
    "YueEngTranslationPromptYueHans",
    "YueEngTranslationPromptYueHant",
    "YueEngGapTranslationPromptYueHans",
    "YueEngGapTranslationPromptYueHant",
    "YueEngGuidedTranslationPromptYueHans",
    "YueEngGuidedTranslationPromptYueHant",
]


YueEngTranslationPromptYueHant = TranslationPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    dictionary_tool_name="lookup_dictionary",
    dictionary_tool_description="查本地詞典入面嘅粵語同普通話詞條。工具會自動判斷查詢係漢字、拼音定粵拼。",
    dictionary_tool_query_description="要查嘅普通話或者粵語詞語，可以係漢字、拼音或者粵拼。",
    base_system_prompt=dedent_and_compact("""
        你負責根據英文字幕，創作對應嘅粵文字幕。

        每條英文字幕都要輸出一條粵文字幕。譯文要用自然、通順嘅書面粵語，
        準確表達英文字幕嘅意思、語氣、戲劇意圖同説話人意圖。唔好逐字硬譯；
        可以調整措辭令佢更似自然粵文字幕。專名、固定稱呼、重複術語同字幕標記
        要喺適合時保留或者按粵語習慣處理。

        輸出內容只可以係生成嘅粵文字幕正文。絕對唔好附加英文、備註、解釋、標籤、
        替代譯文、方括號內容、括號內容，或者任何字幕以外嘅説明。
        """),
    input_pfx="eng_",
    input_desc_tpl="要翻譯成粵文嘅英文字幕 {idx}",
    output_pfx="yuewen_",
    output_desc_tpl="字幕 {idx} 對應嘅粵文譯文",
)
"""Text for traditional written Cantonese translation from English."""

YueEngTranslationPromptYueHans = YueEngTranslationPromptYueHant.transformed(
    Language.yue_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
"""Text for simplified written Cantonese translation from English."""

YueEngGapTranslationPromptYueHant = GapTranslationPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    dictionary_tool_name="lookup_dictionary",
    dictionary_tool_description="查本地詞典入面嘅粵語同普通話詞條。工具會自動判斷查詢係漢字、拼音定粵拼。",
    dictionary_tool_query_description="要查嘅普通話或者粵語詞語，可以係漢字、拼音或者粵拼。",
    base_system_prompt=dedent_and_compact("""
        你負責根據對應嘅英文字幕，補翻譯缺失咗嘅粵文字幕。
        只有當某行現有粵文字幕係空字串時，先需要提供譯文。
        如果某行已經有粵文內容，唔好改，嗰行請輸出空字串。
        譯文要用自然、通順嘅書面粵語，語氣同用詞要儘量貼近附近已有嘅粵文字幕。
        英文字幕係意思來源；譯文唔需要逐字對應，但要準確表達該行意思。
        輸出內容只可以係字幕正文本身，絕對唔好附加英文、備註、解釋、標籤、
        方括號內容、括號內容，或者任何譯文以外嘅説明。
        如果唔需要翻譯，就輸出空字串。
        """),
    src_1_pfx="yuewen_",
    src_1_desc_tpl="字幕 {idx} 現有嘅粵文內容；如果係空就代表要翻譯",
    src_2_pfx="eng_",
    src_2_desc_tpl="字幕 {idx} 對應嘅英文字幕",
    output_pfx="yuewen_",
    output_desc_tpl='字幕 {idx} 譯好後嘅粵文正文；如果唔需要翻譯請輸出 ""。'
    "唔好包含英文、備註、解釋、標籤或者括號説明。",
    output_unmodified_err_tpl="字幕 {idx} 已經有粵文內容，嗰行輸出必須係空字串。",
    output_contains_note_err_tpl=(
        "字幕 {idx} 包含英文或者備註説明；只可以輸出粵文字幕正文。"
    ),
)
"""Text for traditional written Cantonese gap translation using English."""

YueEngGapTranslationPromptYueHans = YueEngGapTranslationPromptYueHant.transformed(
    Language.yue_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
"""Text for simplified written Cantonese gap translation using English."""

YueEngGuidedTranslationPromptYueHant = GuidedTranslationPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    dictionary_tool_name="lookup_dictionary",
    dictionary_tool_description="查本地詞典入面嘅粵語同普通話詞條。工具會自動判斷查詢係漢字、拼音定粵拼。",
    dictionary_tool_query_description="要查嘅普通話或者粵語詞語，可以係漢字、拼音或者粵拼。",
    base_system_prompt=dedent_and_compact("""
        你負責根據英文字幕，創作對應嘅粵文字幕。你亦會收到同一段場景嘅
        既有粵文字幕，作為參考材料。

        每條英文字幕都要輸出一條粵文字幕。譯文要準確表達英文字幕嘅意思、
        語氣、戲劇意圖同説話人意圖。既有粵文字幕係角色名、專名、重複術語、
        語域同固定講法嘅參考；當佢同英文字幕意思兼容時，儘量沿用。
        如果英文字幕同既有粵文字幕有分別，要優先按英文意思翻譯，同時保留
        已經建立好嘅名詞同稱呼。

        每個輸出項目嘅文本欄只可以係生成嘅粵文字幕正文。絕對唔好附加英文、備註、
        解釋、標籤、替代譯文、方括號內容、括號內容，或者任何字幕以外嘅説明。
        """),
    subtitles="eng",
    subtitles_desc="按順序排列、要翻譯成粵文嘅英文字幕",
    guides="yuewen_reference",
    guides_desc="同一段場景嘅既有粵文參考字幕",
    outputs="yuewen",
    outputs_desc="同查詢英文字幕逐一對應嘅粵文譯文",
    index="xuhao",
    index_desc="由 1 開始嘅字幕序號",
    text="wenben",
    subtitle_text_desc="要翻譯成粵文嘅英文字幕文本",
    guide_text_desc="同一段場景嘅既有粵文參考字幕文本",
    output_text_desc="同查詢英文字幕對應嘅粵文譯文文本",
    guide_indices_err="查詢參考字幕序號必須由 1 開始、連續並按順序排列。",
    subtitle_indices_err="查詢字幕序號必須由 1 開始、連續並按順序排列。",
    output_indices_err="答案輸出序號必須由 1 開始、連續並按順序排列。",
    output_correspondence_err="答案輸出序號必須同查詢字幕序號完全對應。",
)
"""Text for traditional guided written Cantonese translation from English."""

YueEngGuidedTranslationPromptYueHans = YueEngGuidedTranslationPromptYueHant.transformed(
    Language.yue_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
"""Text for simplified guided written Cantonese translation from English."""
