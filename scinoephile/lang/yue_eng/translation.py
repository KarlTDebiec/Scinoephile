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

        每個輸出項目嘅文本欄只可以係生成嘅粵文字幕正文。絕對唔好附加英文、備註、
        解釋、標籤、替代譯文、方括號內容、括號內容，或者任何字幕以外嘅説明。
        """),
    subtitles="eng",
    subtitles_desc="按順序排列、要翻譯成粵文嘅英文字幕",
    outputs="yuewen",
    outputs_desc="按輸入字幕順序排列嘅粵文譯文",
    index="xuhao",
    index_desc="由 1 開始嘅字幕序號",
    text="wenben",
    subtitle_text_desc="要翻譯成粵文嘅英文字幕文本",
    output_text_desc="完整粵文譯文",
    subtitle_indices_err="查詢字幕序號必須由 1 開始、連續並按順序排列。",
    output_indices_err="答案輸出序號必須由 1 開始、連續並按順序排列。",
    output_correspondence_err="答案輸出序號必須同查詢字幕序號完全對應。",
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
        淨係為現有粵文字幕列表入面缺失嘅序號提供譯文。每個缺失序號一定要
        啱啱好返回一項輸出；已經有粵文內容嘅序號唔好返回輸出，亦都唔好修改。
        譯文要用自然、通順嘅書面粵語，語氣同用詞要儘量貼近附近已有嘅粵文字幕。
        英文字幕係意思來源；譯文唔需要逐字對應，但要準確表達該行意思。
        輸出內容只可以係字幕正文本身，絕對唔好附加英文、備註、解釋、標籤、
        方括號內容、括號內容，或者任何譯文以外嘅説明。
        如果某個缺失序號唔需要粵文字幕，仍然要保留嗰個輸出項目，文本用空字串。
        """),
    targets="yuewen",
    targets_desc="已有嘅粵文字幕，序號同英文參考字幕一致",
    guides="eng",
    guides_desc="按序號完整排列嘅英文參考字幕",
    outputs="yuewen",
    outputs_desc="現有粵文字幕缺失序號所需嘅粵文譯文",
    index="xuhao",
    index_desc="由 1 開始嘅字幕序號",
    text="wenben",
    target_text_desc="已有嘅粵文字幕文本",
    guide_text_desc="英文參考字幕文本",
    output_text_desc="缺失序號對應嘅粵文譯文正文；如果唔需要字幕就用空字串",
    guide_indices_err="查詢參考字幕序號一定要由 1 開始、連續並按順序排列。",
    target_indices_err="查詢現有字幕序號一定要唯一並按升序排列。",
    target_index_missing_err="每個查詢現有字幕序號都一定要對應一個參考字幕序號。",
    target_gap_missing_err="查詢現有字幕一定要缺少至少一個需要翻譯嘅參考字幕序號。",
    output_indices_err="答案輸出序號一定要唯一並按升序排列。",
    output_indices_mismatch_err="答案輸出序號一定要啱啱好對應查詢現有字幕缺失嘅參考字幕序號。",
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
