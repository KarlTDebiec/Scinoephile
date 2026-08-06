#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Language-specific aligned transcription merger configuration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
from types import MappingProxyType
from typing import Unpack

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider, ProcessorKwargs, TestCase
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import YUE_HANT_PROMPT_FIELDS
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_text_converted
from scinoephile.llms.aligned_transcription_merge import (
    AlignedTranscriptionMergeProcessor,
    AlignedTranscriptionMergePrompt,
)
from scinoephile.llms.providers.registry import get_provider

__all__ = ["DEFAULT_PROMPTS", "get_aligned_transcription_merger"]


_YUE_HANT_PROMPT = replace(
    AlignedTranscriptionMergePrompt(
        language=Language.yue_hant,
        **YUE_HANT_PROMPT_FIELDS,
        base_system_prompt=dedent_and_compact("""
        你負責綜合多個地位完全相同嘅廣東話語音轉寫來源，重建準確、完整而忠於錄音嘅
        繁體粵文字幕。查詢只包含語音轉寫同語音分析，冇參考字幕。唔好預設任何來源
        比較可靠，亦唔好因為來源名稱或者排列次序而優先採用某一個來源。請按各來源
        共識、粵語讀音、語境同前後內容判斷實際對白；多數共識係有用證據，但唔保證
        一定正確。

        每個查詢入面嘅來源文字同講者列係逐個 Unicode 字符直向對齊。單一來源嘅「　」
        （全形空格）只表示嗰個來源喺該欄冇字；講者列嘅全形空格表示冇語音。如果所有
        來源同講者列同一欄都係「・」，就表示至少 0.25 秒嘅偵測停頓。連續一個全共享
        「・」表示 0.25 至不足 0.5 秒，兩個表示 0.5 至不足 0.75 秒，三個表示 0.75 至
        不足 1.0 秒，如此類推。每次查詢已經喺四個或以上連續「・」（即至少 1.0 秒嘅
        停頓）分開。講者列嘅「Ａ」、「Ｂ」等表示唔同講者，「＊」表示偵測到語音但未能
        分配講者。呢啲符號只係證據，唔可以出現喺答案。

        答案要提供完整字幕列表；按列表順序串連所有文本就必須係完整共識轉寫，唔可以
        遺漏、重複、概括、翻譯或者虛構內容。保留實際對白嘅意思、語域、粗口、重複、
        猶豫、語氣助詞同人物口吻。採用香港繁體粵文，並加入合適嘅全形中文標點。

        同一個字幕只可以包含一段連續對白。所有來源同講者列共有嘅停頓原則上必須分開
        字幕；穩定講者轉換亦應該分開字幕。冇明顯停頓或者講者轉換時，就按句法、語意
        同標點選擇自然位置。目標大約 9 個非空白字符，通常保持喺 0.75 至 3.5 秒之內；
        每項字幕絕對唔可以超過 20 個非空白字符。亦要避免超過大約 6 秒。唔好輸出空白
        字幕，亦唔好為咗湊長度而切開短語、專名或者不可分割嘅語氣單位；如果一個語句
        太長，就喺最自然嘅次要句法邊界分開。
        """),
        sources="laiyuan",
        sources_desc="地位相同、逐字符直向對齊嘅語音轉寫來源",
        source_name="mingcheng",
        source_name_desc="語音轉寫來源嘅固定名稱",
        source_text="wenben",
        source_text_desc="每個對齊欄一個字符、全形空格或者全形停頓標記嘅來源文本",
        speaker="shuoshuuren",
        speaker_desc="逐欄對齊嘅全形講者、未分配語音、冇語音同停頓標記",
        subtitles="zimu",
        subtitles_desc="完整共識轉寫按顯示邊界分成嘅字幕",
        subtitle_index="xuhao",
        subtitle_index_desc="由 1 開始嘅共識字幕序號",
        subtitle_text="wenben",
        subtitle_text_desc="冇任何對齊標記、加上合適標點嘅完整共識字幕文本",
        source_name_err="每個查詢嘅來源名稱必須非空白而且唯一。",
        reference_source_err="對齊轉寫合併查詢只可以包含語音轉寫，唔可以包含參考或者指引。",
        row_length_err="同一查詢區段嘅所有來源列同講者列必須有相同嘅非零長度。",
        reference_marker_err="對齊轉寫合併查詢唔可以包含參考字幕邊界標記。",
        speaker_character_err="講者列只可以包含全形講者、星號、全形空格同停頓標記。",
        transcript_empty_err="對齊轉寫合併查詢必須包含轉寫文本。",
        subtitle_indices_err="答案字幕序號必須由 1 開始、連續並按順序排列。",
        subtitle_text_err="答案每一項字幕都必須包含非空白文本。",
        subtitle_annotation_err="答案字幕唔可以包含對齊或者講者標記。",
        consensus_coverage_err_tpl=(
            "答案只保留咗高可信多數語音轉寫字符序列嘅 {coverage:.1%}，必須至少保留 "
            "{minimum:.1%}。答案好可能漏咗各來源一致嘅對白；請重新逐欄檢查並返回完整轉寫。"
        ),
        subtitle_length_err_tpl=(
            "答案字幕序號 {indexes} 超過每項 {max_characters} 個非空白字符嘅上限。"
        ),
    ),
    test_case_invalid_post=(
        "請返回完整 JSON 答案，而唔係淨係返回修改部分。修正列出嘅問題時，必須重新檢查"
        "由第一欄到最後一欄，保留全部對白內容同順序；如果錯誤只涉及字幕長度，淨係拆分"
        "過長字幕，唔可以刪除、改寫或者重新排列其他文本。"
    ),
)
"""Prompt for merging aligned traditional Cantonese ASR evidence."""

_YUE_HANS_PROMPT = _YUE_HANT_PROMPT.transformed(
    Language.yue_hans, lambda text: get_zho_text_converted(text, OpenCCConfig.hk2s)
)
"""Prompt for merging aligned simplified Cantonese ASR evidence."""

DEFAULT_PROMPTS: Mapping[Language, AlignedTranscriptionMergePrompt] = MappingProxyType(
    {Language.yue_hans: _YUE_HANS_PROMPT, Language.yue_hant: _YUE_HANT_PROMPT}
)
"""Aligned transcription merge prompts keyed by output language."""


def get_aligned_transcription_merger(
    language: Language,
    prompt: AlignedTranscriptionMergePrompt | None = None,
    shared_test_cases: list[TestCase] | None = None,
    provider: LLMProvider | None = None,
    **kwargs: Unpack[ProcessorKwargs],
) -> AlignedTranscriptionMergeProcessor:
    """Get an aligned transcription merger for a supported language.

    Arguments:
        language: language of ASR sources and consensus output
        prompt: text for LLM correspondence
        shared_test_cases: shared verified test cases
        provider: provider to use for queries
        **kwargs: additional processor keyword arguments
    Returns:
        configured aligned transcription merge processor
    Raises:
        ScinoephileError: if aligned merging does not support the language
    """
    if language not in DEFAULT_PROMPTS:
        raise ScinoephileError(
            f"Aligned transcription merging does not support {language.code}."
        )
    if prompt is None:
        prompt = DEFAULT_PROMPTS[language]
    if provider is None:
        provider = get_provider()
    return AlignedTranscriptionMergeProcessor(
        prompt, shared_test_cases or [], provider=provider, **kwargs
    )
