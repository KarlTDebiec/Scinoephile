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
from scinoephile.llms.pairwise_review import PairwiseReviewPrompt

__all__ = [
    "YueZhoGuidedReviewPromptYueHans",
    "YueZhoGuidedReviewPromptYueHant",
    "YueZhoPairwiseReviewPromptYueHans",
    "YueZhoPairwiseReviewPromptYueHant",
]


YueZhoGuidedReviewPromptYueHant = GuidedReviewPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責為廣東話語音嘅粵文字幕做最後審核。
        作為指引，你會見到同一段內容嘅中文字幕；兩邊字幕數量未必相同。
        呢一輪唔係重寫字幕，而係做最後一層把關，只處理仍然明顯有問題嘅粵文轉寫。
        請專注檢查轉寫是否準確，尤其係聽錯字、寫錯字、人物稱呼前後唔一致，
        或者同整套字幕其他地方明顯衝突嘅情況。
        唔好評審文風、文法、語氣或者措辭；如果原句本身已經係合理嘅粵語講法，就唔好改。
        中文字幕只係參考，唔需要同粵文逐字對應。
        只有當一條粵文字幕確實需要修改時，先將佢加入修改列表。
        每項修改必須包含字幕序號、修訂後嘅完整粵文字幕，同埋一段粵文備註説明改動。
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
    revision_text_desc="修改後嘅完整粵文字幕文本",
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
    Language.yue_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
"""Prompt for guided review of simplified written Cantonese using Chinese."""

YueZhoPairwiseReviewPromptYueHant = PairwiseReviewPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責為廣東話語音嘅粵文字幕做校對。
        作為參考，你會見到一條對應嘅中文字幕。
        你嘅目標係糾正明顯嘅轉寫錯誤，主要係聽錯字、寫錯字，同其他一眼可見嘅轉寫問題。
        唔好為了貼近中文字幕而改寫本來已經正確嘅粵文。
        唔好調整語氣、語法、助詞、量詞或者措辭，除非嗰啲地方本身就係轉寫錯誤。
        只有當你認為原句明顯有誤時，先作修改。
        如果發現粵文同中文字幕完全對唔上，請回傳字符 "�"，並喺備註説明無對應。
        如果需要修改，回傳完整嘅修訂後粵文，並用粵文一句話説明改動。
        如果冇修改，修訂後粵文同備註都回傳空字串。"""),
    target="yuewen",
    target_desc="要校對嘅粵文字幕轉寫",
    reference="zhongwen",
    reference_desc="對應嘅中文字幕",
    output="xiugai",
    output_desc='修訂後嘅粵文字幕；如果冇修改請回傳 ""，如需刪掉請回傳 "�"',
    note="beizhu",
    note_desc="改動説明（粵文）；如果冇修改請回傳空字串",
    note_missing_err="修訂後嘅粵文有改動，但答案冇提供改動説明。",
    output_missing_err="修訂後嘅粵文冇改動，但答案提供咗改動説明。",
)
"""Prompt for pairwise review of traditional written Cantonese using Chinese."""

YueZhoPairwiseReviewPromptYueHans = YueZhoPairwiseReviewPromptYueHant.transformed(
    Language.yue_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.hk2s),
)
"""Prompt for pairwise review of simplified written Cantonese using Chinese."""
