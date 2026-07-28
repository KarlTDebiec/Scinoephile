#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Prompts for reviewing written Cantonese using standard Chinese."""

from __future__ import annotations

from functools import partial

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import YUE_HANT_PROMPT_FIELDS
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_text_converted
from scinoephile.llms.guided_review import GuidedReviewPrompt
from scinoephile.llms.multi_review import MultiReviewPrompt

__all__ = [
    "YueZhoGuidedReviewPromptYueHans",
    "YueZhoGuidedReviewPromptYueHant",
    "YueZhoMultiReviewPromptYueHant",
]


YueZhoGuidedReviewPromptYueHant = GuidedReviewPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責按段審核廣東話語音嘅粵文字幕。
        作為指引，你會見到同一段內容嘅中文字幕；兩邊字幕數量未必相同。
        呢一輪唔係重寫字幕，只處理明顯有問題嘅粵文轉寫。
        請專注檢查轉寫是否準確，尤其係聽錯字、寫錯字、人物稱呼前後唔一致，
        或者同整套字幕其他地方明顯衝突嘅情況。
        唔好評審文風、文法、語氣或者措辭；如果原句本身已經係合理嘅粵語講法，就唔好改。
        中文字幕只係參考，唔需要同粵文逐字對應。
        只有當一條粵文字幕確實需要修改時，先將佢加入修改列表。
        每項修改必須包含字幕序號、修訂後嘅完整粵文字幕，同埋一段粵文備註説明改動。
        如果要刪除同音訊及中文字幕都冇對應嘅多餘字幕，修訂文本只填「�」。
        如果全部粵文字幕都唔需要修改，請回傳空嘅修改列表。"""),
    targets="yuewen",
    targets_desc="按順序排列、需要審核嘅粵文字幕轉寫",
    guides="zhongwen",
    guides_desc="按順序排列、涵蓋同一段內容嘅中文字幕指引",
    revisions="xiugai_yuewen",
    revisions_desc="需要修改嘅粵文字幕；唔需要修改嘅字幕唔好包括喺內",
    index="xuhao",
    index_desc="由 1 開始嘅字幕序號",
    text="wenben",
    target_text_desc="需要審核嘅粵文字幕轉寫",
    guide_text_desc="中文字幕指引文本",
    revision_text_desc="修改後嘅完整粵文字幕文本；如果要刪除字幕就只填「�」",
    note="beizhu",
    note_desc="關於粵文字幕修改嘅粵文備註",
    target_indices_err="查詢粵文字幕序號必須由 1 開始、連續並按順序排列。",
    guide_indices_err="查詢中文字幕序號必須由 1 開始、連續並按順序排列。",
    revision_indices_err="答案修改序號必須唯一並按升序排列。",
    revision_index_missing_err_tpl="答案修改序號 {idx} 喺查詢粵文字幕中不存在。",
    revision_unmodified_err_tpl=(
        "答案修改 {idx} 同查詢粵文字幕 {idx} 相同；唔需要修改嘅字幕必須從修改列表省略。"
    ),
)
"""Prompt for guided review of traditional written Cantonese using Chinese."""

YueZhoGuidedReviewPromptYueHans = YueZhoGuidedReviewPromptYueHant.transformed(
    Language.yue_hans, partial(get_zho_text_converted, config=OpenCCConfig.hk2s)
)
"""Prompt for guided review of simplified written Cantonese using Chinese."""

YueZhoMultiReviewPromptYueHant = MultiReviewPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責綜合多個廣東話語音轉寫來源，製作一套準確嘅繁體粵文字幕。
        每個轉寫來源地位完全相同；唔好預設任何一個來源比較可靠，亦唔好因為來源排列次序
        而優先採用某一個來源。請逐句比較各個來源，按粵語讀音、語境同內容判斷最合理嘅
        實際對白。來源之間嘅多數共識係有用證據，但唔代表一定正確。
        你亦會見到一套完整嘅繁體中文字幕指引。中文字幕決定答案嘅字幕序號同時序，亦可以
        協助理解語義、人物稱呼同專有名詞，但唔係實際粵語對白。唔好將中文字幕逐字翻譯成
        粵文，亦唔好為咗貼近中文字幕而改寫來源中合理嘅粵語講法、語氣、助詞、量詞或措辭。
        答案必須為每一條中文字幕指引提供同序號嘅完整粵文輸出。如果某個序號至少有一個
        轉寫來源，請綜合現有來源輸出最準確嘅繁體粵文。如果某個序號喺所有轉寫來源都缺失，
        輸出文本必須留空；唔好根據中文字幕補寫或翻譯缺失嘅粵文。
        請保留實際對白嘅意思、語域、粗口、重複、停頓同人物口吻，只修正語音辨識錯誤、
        錯別字、標點同明顯前後矛盾。"""),
    sources="laiyuan",
    sources_desc="多個地位相同、涵蓋同一段內容嘅粵語轉寫來源",
    guides="zhongwen",
    guides_desc="按順序排列、決定輸出序號同時序嘅完整繁體中文字幕指引",
    outputs="shuchu_yuewen",
    outputs_desc="同每條中文字幕序號一一對應嘅完整繁體粵文輸出",
    source_name="mingcheng",
    source_name_desc="轉寫來源嘅固定名稱",
    subtitles="zhuanxie",
    subtitles_desc="呢個來源現有嘅粵語轉寫，序號對應中文字幕指引",
    index="xuhao",
    index_desc="由 1 開始嘅中文字幕指引序號",
    text="wenben",
    source_text_desc="呢個來源嘅粵語轉寫文本",
    guide_text_desc="繁體中文字幕指引文本",
    output_text_desc="完整繁體粵文輸出；如果全部來源都缺失就留空",
    guide_indices_err="查詢中文字幕序號必須由 1 開始、連續並按順序排列。",
    source_count_err="查詢必須包含至少兩個粵語轉寫來源。",
    source_name_err="查詢來源名稱必須非空白而且唯一。",
    source_indices_err="每個查詢來源嘅轉寫序號必須唯一並按升序排列。",
    source_index_missing_err="每個查詢來源嘅轉寫序號都必須對應中文字幕序號。",
    output_indices_err="答案輸出序號必須由 1 開始、連續並按順序排列。",
    output_correspondence_err="答案輸出序號必須同查詢中文字幕序號完全對應。",
    unsupported_output_err_tpl=(
        "答案輸出 {idx} 必須留空，因為所有粵語轉寫來源喺呢個序號都缺失。"
    ),
)
"""Prompt for multi-source review of Cantonese using traditional Chinese."""
