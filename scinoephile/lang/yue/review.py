#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM prompts for written Cantonese review."""

from __future__ import annotations

from functools import partial

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_text_converted
from scinoephile.llms.guided_review import GuidedReviewPrompt
from scinoephile.llms.multi_review import MultiReviewPrompt
from scinoephile.llms.review import ReviewPrompt

from .prompts import YUE_HANT_PROMPT_FIELDS

__all__ = [
    "GuidedReviewPromptYueHans",
    "GuidedReviewPromptYueHant",
    "ReviewPromptYueHans",
    "ReviewPromptYueHant",
    "TimedTranscriptionMultiReviewPromptYueHans",
    "TimedTranscriptionMultiReviewPromptYueHant",
]


GuidedReviewPromptYueHant = GuidedReviewPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責為粵文字幕做最後審核。
        你亦會見到同一段內容嘅參考字幕；參考字幕可以係另一種語言，字幕數量亦未必相同。
        請利用參考字幕判斷粵文有冇明顯嘅聽錯字、寫錯字、名稱錯誤或者前後矛盾。
        唔好翻譯參考字幕，亦唔好為咗貼近參考字幕而改寫本來正確嘅粵文。
        唔好潤色或者改動語氣、文法、助詞、量詞同措辭。
        只有確實需要修改嘅粵文字幕先加入修改列表。每項修改必須包含字幕序號、
        完整修訂後文本同粵文備註。如果要刪除多餘嘅目標字幕，修訂文本只填「�」。
        如果全部字幕都唔需要修改，請返回空嘅修改列表。"""),
    targets="yuewen",
    targets_desc="按順序排列、需要審核嘅粵文字幕",
    guides="cankao",
    guides_desc="按順序排列、涵蓋同一段內容嘅參考字幕",
    revisions="xiugai_yuewen",
    revisions_desc="需要修改嘅粵文字幕；唔需要修改嘅字幕唔好包括喺內",
    index="xuhao",
    index_desc="由 1 開始嘅字幕序號",
    text="wenben",
    target_text_desc="需要審核嘅粵文字幕文本",
    guide_text_desc="參考字幕文本",
    revision_text_desc="修改後嘅完整粵文字幕文本；如果要刪除字幕就只填「�」",
    note="beizhu",
    note_desc="關於粵文字幕修改嘅粵文備註",
    target_indices_err="查詢目標字幕序號必須由 1 開始、連續並按順序排列。",
    guide_indices_err="查詢參考字幕序號必須由 1 開始、連續並按順序排列。",
    revision_indices_err="答案修改序號必須唯一並按升序排列。",
    revision_index_missing_err_tpl="答案修改序號 {idx} 喺查詢目標字幕中不存在。",
    revision_unmodified_err_tpl=(
        "答案修改 {idx} 同查詢目標字幕 {idx} 相同；唔需要修改嘅字幕必須從修改列表省略。"
    ),
)
"""LLM correspondence text for guided review of traditional Cantonese."""

GuidedReviewPromptYueHans = GuidedReviewPromptYueHant.transformed(
    Language.yue_hans, partial(get_zho_text_converted, config=OpenCCConfig.hk2s)
)
"""LLM correspondence text for guided review of simplified Cantonese."""

ReviewPromptYueHant = ReviewPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責校對粵文字幕。
        只修正排版、錯別字、OCR 或轉寫造成嘅明顯錯誤。
        唔好潤色、改寫、改動語氣或用詞，亦唔好根據上下文改劇情。
        如果原句本身已經係合理嘅粵語講法，請保持原文不變。
        只有喺字幕需要修改時先加入一項修改。每項修改必須包含字幕序號、
        修訂後嘅完整文本，同埋說明修改內容嘅粵文備註。
        如果全部字幕都唔需要修改，請返回空嘅修改列表。"""),
    subtitles="zimu",
    subtitles_desc="按順序排列、需要校對嘅粵文字幕",
    revisions="xiugai",
    revisions_desc="需要修改嘅粵文字幕；唔需要修改嘅字幕唔好包括喺內",
    index="xuhao",
    index_desc="由 1 開始嘅字幕序號",
    text="wenben",
    subtitle_text_desc="需要校對嘅粵文字幕文本",
    revision_text_desc="修改後嘅完整粵文字幕文本",
    note="beizhu",
    note_desc="關於粵文字幕修改嘅粵文備註說明",
    subtitle_indices_err="查詢字幕序號必須由 1 開始、連續並按順序排列。",
    revision_indices_err="答案修改序號必須唯一並按升序排列。",
    revision_index_missing_err_tpl="答案修改序號 {idx} 喺查詢字幕中不存在。",
    revision_unmodified_err_tpl=(
        "答案修改 {idx} 同查詢字幕 {idx} 相同；唔需要修改嘅字幕必須從修改列表省略。"
    ),
)
"""LLM correspondence text for traditional written Cantonese review."""

ReviewPromptYueHans = ReviewPromptYueHant.transformed(
    Language.yue_hans, partial(get_zho_text_converted, config=OpenCCConfig.hk2s)
)
"""LLM correspondence text for simplified written Cantonese review."""

TimedTranscriptionMultiReviewPromptYueHant = MultiReviewPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責綜合多個地位完全相同嘅廣東話語音轉寫來源，重建一份準確而完整嘅繁體粵文
        對白。唔好預設任何一個來源比較可靠，亦唔好因為來源排列次序而優先採用某一個
        來源。請比較各個來源，按粵語讀音、語境同內容判斷最合理嘅實際對白；多數共識係
        有用證據，但唔代表一定正確。每個來源嘅時序可能有少量偏差，同一句對白亦可能落
        喺相鄰時段，所以判斷時要一併考慮前後時段。
        指引欄位只係中立嘅音訊時段標籤，用嚟決定答案序號同大致位置，並唔包含對白或
        語義。唔好將時段標籤當成對白，亦唔好由標籤補寫內容。答案必須為每一個時段提供
        同序號嘅輸出。如果某個時段至少有一個來源包含轉寫，請綜合所有來源輸出最準確嘅
        繁體粵文；如果所有來源喺該時段都冇內容，輸出必須留空。
        請保留實際對白嘅意思、語域、粗口、重複、語氣助詞同人物口吻，只修正語音辨識
        錯誤、錯別字、標點同明顯前後矛盾。唔好潤色、概括、翻譯或虛構對白。"""),
    sources="laiyuan",
    sources_desc="多個地位相同、涵蓋同一段音訊嘅粵語轉寫來源",
    guides="shiduan",
    guides_desc="按順序排列、只表示音訊位置嘅中立時段標籤",
    outputs="shuchu_yuewen",
    outputs_desc="同每個時段序號一一對應嘅完整繁體粵文輸出",
    source_name="mingcheng",
    source_name_desc="轉寫來源嘅固定名稱",
    subtitles="zhuanxie",
    subtitles_desc="呢個來源現有嘅粵語轉寫，序號對應中立時段",
    index="xuhao",
    index_desc="由 1 開始嘅時段序號",
    text="wenben",
    source_text_desc="呢個來源喺該時段嘅粵語轉寫文本",
    guide_text_desc="只表示音訊位置、冇對白語義嘅時段標籤",
    output_text_desc="完整繁體粵文輸出；如果全部來源都缺失就留空",
    guide_indices_err="查詢時段序號必須由 1 開始、連續並按順序排列。",
    source_count_err="查詢必須包含至少兩個粵語轉寫來源。",
    source_name_err="查詢來源名稱必須非空白而且唯一。",
    source_indices_err="每個查詢來源嘅轉寫序號必須唯一並按升序排列。",
    source_index_missing_err="每個查詢來源嘅轉寫序號都必須對應一個時段序號。",
    output_indices_err="答案輸出序號必須由 1 開始、連續並按順序排列。",
    output_correspondence_err="答案輸出序號必須同查詢時段序號完全對應。",
    unsupported_output_err_tpl=(
        "答案輸出 {idx} 必須留空，因為所有粵語轉寫來源喺呢個時段都冇內容。"
    ),
)
"""Prompt for merging timed traditional Cantonese ASR evidence."""

TimedTranscriptionMultiReviewPromptYueHans = (
    TimedTranscriptionMultiReviewPromptYueHant.transformed(
        Language.yue_hans, partial(get_zho_text_converted, config=OpenCCConfig.hk2s)
    )
)
"""Prompt for merging timed simplified Cantonese ASR evidence."""
