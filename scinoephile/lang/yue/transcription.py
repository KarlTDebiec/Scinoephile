#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM prompts for Cantonese transcription from aligned ASR evidence."""

from __future__ import annotations

from functools import partial

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_text_converted
from scinoephile.llms.transcription import TranscriptionPrompt

from .prompts import YUE_HANT_PROMPT_FIELDS

__all__ = ["TranscriptionPromptYueHans", "TranscriptionPromptYueHant"]


TranscriptionPromptYueHant = TranscriptionPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責根據一個或者多個廣東話語音轉寫來源，重建準確、完整而忠於錄音嘅繁體
        粵文字幕。查詢只包含語音轉寫同語音分析，冇參考字幕。如果有多個來源，佢哋
        地位完全相同；唔好預設任何來源比較可靠，亦唔好因為來源名稱或者排列次序而
        優先採用某一個來源。請按來源文字、粵語讀音、語境同前後內容判斷實際對白；
        多數共識係有用證據，但唔保證一定正確。

        每個查詢入面嘅來源文字同語音分析列係逐個 Unicode 字符直向對齊。單一來源嘅
        「　」（全形空格）只表示嗰個來源喺該欄冇字；講者列嘅全形空格表示冇語音。如果
        所有來源同分析列同一欄都係「・」，就表示至少 0.25 秒嘅偵測停頓。連續一個全共享
        「・」表示 0.25 至不足 0.5 秒，兩個表示 0.5 至不足 0.75 秒，三個表示 0.75 至
        不足 1.0 秒，如此類推。每次查詢已經喺四個或以上連續「・」（即至少 1.0 秒嘅
        停頓）分開。講者列嘅「Ａ」、「Ｂ」等表示唔同講者，「＊」表示偵測到語音但未能
        分配講者。呢啲符號只係證據，唔可以出現喺答案。

        如果有語言列，「粵」、「普」、「英」、「日」、「韓」分別表示粵語、普通話、
        英語、日語、韓語；其他全形字母或者「外」表示其他語言，空格表示冇可靠分類。
        如果有歌唱列，「唱」表示偵測到歌唱；如果有音樂列，「樂」表示偵測到音樂。
        歌唱、音樂同語音可以重疊；背景音樂唔係對白證據，亦唔應該令你刪走同欄嘅語音。
        語言分類都只係輔助證據；如果同多個 ASR 一致嘅轉寫衝突，唔可以單靠語言列刪走
        內容。「唱」亦唔代表一定有可辨識歌詞；只可以按 ASR 實際提供嘅文字重建內容。

        如果查詢只有一個來源，請將佢當作唯一嘅詞彙證據，忠實保留可辨識文字；唔好因為
        缺少第二個來源而刪走內容，亦唔可以單靠分析列添加來源冇提供嘅具體詞句。

        如果查詢有多個來源，具體詞句必須有跨來源嘅語音轉寫支持。如果一個詞或者連續
        片段只出現喺單一來源，而其他來源喺同一時間位置都係空格，原則上要當作單一模型
        插入或者幻覺而刪除，尤其係突然轉語言嘅英文等孤立片段。講者列只可以證明可能有
        人聲；語言列只係語言分類；歌唱同音樂列只係聲音事件。
        呢啲分析列全部都唔係獨立嘅詞彙證據，唔可以替單一來源嘅具體文字背書。
        只有其他來源喺相鄰或者重疊欄提供
        同一發音或同一語句嘅另一寫法，清楚顯示問題係對齊偏移而唔係孤立插入，先可以保留
        單一列顯示嘅形式。唔好因為孤立文字語法通順、符合語境或者同語言分類一致就收錄。

        如果成個查詢都冇任何可辨識詞句（多來源查詢包括冇任何詞句得到足夠跨來源支持），
        `wenben` 必須回答空字串 `""`，即係完全略過呢段。空字串係唯一唔需要「｜」結尾
        嘅答案。多來源查詢唔可以因為至少要輸出一項字幕而勉強揀一個來源。短片段入面，
        兩個來源只係偶然重合一個字，但各自提出唔同詞句，唔算可辨識共識。例如來源分別
        係「桃花」、「蒲布」、空白、「婆」、空白同「婆婆」時，必須回答空字串，唔可以
        回答「婆」或者「婆婆」。

        答案唔係字幕列表，而係一個 `wenben` 字串。輸出完整轉寫，並喺每項字幕結尾
        插入「｜」；答案最後一個字符都必須係「｜」。例如兩項字幕可以回答
        `甲乙｜丙丁｜`。除咗作為字幕邊界嘅「｜」之外，唔好加入任何標點或者符號。答案亦
        唔可以包含輸入嘅全形空格、停頓、講者或者語音分析標記，唔需要逐欄對齊或者補空格。
        刪走所有「｜」後嘅完整文本唔可以遺漏、重複、概括、翻譯或者虛構內容。保留實際
        對白嘅意思、語域、粗口、重複、猶豫、語氣助詞同人物口吻。採用香港繁體粵文；英文
        同其他拉丁文字都要用全形字母同數字。

        同一個字幕只可以包含一段連續對白。所有來源同講者列共有嘅停頓原則上必須分開
        字幕；穩定講者轉換亦應該分開字幕。冇明顯停頓或者講者轉換時，就按句法同語意
        選擇自然位置。目標大約 9 個非空白字符，通常保持喺 0.75 至 3.5 秒之內；
        每項字幕絕對唔可以超過 20 個非空白字符。亦要避免超過大約 6 秒。唔好輸出空白
        字幕，亦唔好為咗湊長度而切開短語、專名或者不可分割嘅語氣單位；如果一個語句
        太長，就喺最自然嘅次要句法邊界分開。
        """),
    sources="laiyuan",
    sources_desc="一個或者多個地位相同、逐字符直向對齊嘅語音轉寫來源",
    source_name="mingcheng",
    source_name_desc="語音轉寫來源嘅固定名稱",
    source_text="wenben",
    source_text_desc="每個對齊欄一個字符、全形空格或者全形停頓標記嘅來源文本",
    speaker="shuoshuuren",
    speaker_desc="逐欄對齊嘅全形講者、未分配語音、冇語音同停頓標記",
    language_field="yuyan",
    language_desc="逐欄對齊嘅全形語言、未分類同停頓標記（如果有）",
    singing="gechang",
    singing_desc="逐欄對齊嘅歌唱、冇歌唱同停頓標記（如果有）",
    music="yinyue",
    music_desc="逐欄對齊嘅音樂、冇音樂同停頓標記（如果有）",
    answer_text="wenben",
    answer_text_desc="冇標點並喺每項字幕後插入全形直線嘅完整轉寫；冇可辨識內容時用空字串",
    source_name_err="每個查詢嘅來源名稱必須非空白而且唯一。",
    reference_source_err="轉寫查詢只可以包含語音轉寫，唔可以包含參考或者指引。",
    row_length_err="同一查詢區段嘅所有來源列、講者列同可選分析列必須有相同嘅非零長度。",
    reference_marker_err="轉寫查詢唔可以包含參考字幕邊界標記。",
    speaker_character_err="講者列只可以包含全形講者、星號、全形空格同停頓標記。",
    language_character_err="語言列只可以包含已定義嘅全形語言、全形空格同停頓標記。",
    audio_event_character_err="歌唱同音樂列只可以包含相應嘅全形事件、全形空格同停頓標記。",
    transcript_empty_err="轉寫查詢必須包含轉寫文本。",
    answer_text_err=(
        "答案文本必須係空字串，或者包含非空白字幕，以全形直線分隔並結束，而且唔可以"
        "包含對齊或者講者標記。"
    ),
    answer_punctuation_err="除咗全形字幕邊界之外，答案文本唔可以包含任何標點或者符號。",
    consensus_coverage_err_tpl=(
        "答案只保留咗高可信多數語音轉寫字符序列嘅 {coverage:.1%}，必須至少保留 "
        "{minimum:.1%}。答案好可能漏咗各來源一致嘅對白；請重新逐欄檢查並返回完整轉寫。"
    ),
    subtitle_length_err_tpl=(
        "答案字幕序號 {indexes} 超過每項 {max_characters} 個非空白字符嘅上限。"
    ),
)
"""Prompt for traditional Cantonese transcription."""

TranscriptionPromptYueHans = TranscriptionPromptYueHant.transformed(
    Language.yue_hans, partial(get_zho_text_converted, config=OpenCCConfig.hk2s)
)
"""Prompt for simplified Cantonese transcription."""
