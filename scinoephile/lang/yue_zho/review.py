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
    "YueZhoMultiReviewPromptYueHantBlockGlobal",
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

YueZhoMultiReviewPromptYueHantBlockGlobal = MultiReviewPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    boundary_aware=True,
    base_system_prompt=dedent_and_compact("""
        你負責以完整區塊為單位，綜合多個廣東話語音轉寫來源，製作一套準確嘅繁體
        粵文字幕。每個來源地位完全相同；唔好預設任何一個來源比較可靠，亦唔好因為
        來源排列次序而優先採用某一個來源。來源之間嘅多數共識係有用證據，但唔代表
        一定正確。

        每個來源嘅字幕序號同分界都只係按時間作出嘅初步估計，可能將一句完整對白拆去
        相鄰序號，亦可能將幾句對白合併喺同一序號。必須先由頭到尾閱讀每個來源嘅完整
        區塊，將每個來源視為一條保持原有文字次序嘅連續對白，再決定整個輸出區塊嘅
        分界。唔可以逐個序號獨立揀答案。

        你可以按語義同時序將文字移去相鄰序號、拆開或者合併來源字幕。分界修正只可
        使用當前序號或緊貼前後序號已經出現嘅粵語對白；絕對唔可由區塊其他位置搬一句
        對白過黎，亦唔可單憑中文字幕補寫。如果一個來源將
        完整句放喺一個序號，而另一個來源將同一句拆喺兩個序號，必須揀一套首尾相接、
        唔重疊嘅分配；絕對唔可以先輸出完整句，再喺下一個序號重複輸出佢嘅後半段。
        同一段實際對白喺成個輸出區塊只可以出現一次。某個序號即使有來源文字，如果
        嗰段文字已經正確分配去相鄰輸出，該序號可以留空。相反，如果文字明顯由相鄰
        來源序號錯置過嚟，可以輸出去本來全部來源都留空嘅正確序號。

        你亦會見到一套完整嘅繁體中文字幕指引。中文字幕決定答案嘅字幕序號同時序，
        並協助理解語義、人物稱呼同專有名詞，但中文字幕同實際粵語對白嘅分句可能唔同，
        亦唔係實際對白。唔好將中文字幕逐字翻譯成粵文，亦唔好為咗貼近中文字幕而改寫
        來源中合理嘅粵語講法、語氣、助詞、量詞或措辭。如果整個區塊嘅來源都冇某段
        實際對白，輸出必須留空，唔可以用中文字幕補寫。

        請保留實際對白嘅意思、語域、粗口、重複、停頓同人物口吻，只修正語音辨識錯誤、
        錯別字、標點同明顯前後矛盾。每個實質詞語同語氣助詞都要有附近粵語轉寫支持；
        當多個來源嘅用詞一致，唔好因為另一個說法同樣通順，就自行換成同義詞或另一個語氣助詞。
        回答之前必須由頭到尾重讀完整輸出區塊，逐項核對：
        每段實際對白只出現一次；相鄰輸出冇因為來源分界唔同而重複前句嘅後綴或後句嘅
        前綴；每個分界都同相鄰中文字幕嘅語義同時序最合理；所有來源真正缺失嘅內容仍然
        留空。答案必須為每一條中文字幕提供同序號嘅完整粵文輸出。"""),
    sources="laiyuan",
    sources_desc="多個地位相同、分界只屬初步估計嘅完整粵語轉寫區塊",
    guides="zhongwen",
    guides_desc="按順序排列、決定輸出序號同時序嘅完整繁體中文字幕指引",
    outputs="shuchu_yuewen",
    outputs_desc="全區塊共同審核並重新分界後，同每條中文字幕序號一一對應嘅粵文輸出",
    source_name="mingcheng",
    source_name_desc="轉寫來源嘅固定名稱",
    subtitles="zhuanxie",
    subtitles_desc="呢個來源按初步分界排列嘅完整粵語轉寫區塊",
    index="xuhao",
    index_desc="由 1 開始嘅中文字幕指引序號",
    text="wenben",
    source_text_desc="可能需要同相鄰序號重新分界嘅粵語轉寫文本",
    guide_text_desc="繁體中文字幕指引文本",
    output_text_desc="全區塊重新分界後嘅完整繁體粵文；已移去相鄰序號或真正缺失就留空",
    guide_indices_err="查詢中文字幕序號必須由 1 開始、連續並按順序排列。",
    source_count_err="查詢必須包含至少兩個粵語轉寫來源。",
    source_name_err="查詢來源名稱必須非空白而且唯一。",
    source_indices_err="每個查詢來源嘅轉寫序號必須唯一並按升序排列。",
    source_index_missing_err="每個查詢來源嘅轉寫序號都必須對應中文字幕序號。",
    output_indices_err="答案輸出序號必須由 1 開始、連續並按順序排列。",
    output_correspondence_err="答案輸出序號必須同查詢中文字幕序號完全對應。",
    unsupported_output_err_tpl=(
        "答案輸出 {idx} 喺當前或緊貼前後序號冇任何粵語轉寫文字支持。下一次必須只用"
        "附近來源文字重新分界；如果附近來源真正缺失內容，就必須留空。"
    ),
    conflicting_boundary_duplication_err_tpl=(
        "答案輸出 {one_idx} 同 {two_idx} 因為來源分界衝突而重複使用咗片段 "
        "{fragment!r}。下一次必須以完整區塊重新決定一次分界，唔可以將同一段實際對白"
        "輸出兩次。"
    ),
)
"""Boundary-aware block-global Cantonese review using traditional Chinese."""
