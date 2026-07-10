#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for standard Chinese/written Cantonese translation prompts."""

from __future__ import annotations

from functools import partial

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.zho.prompts import PromptZhoHant
from scinoephile.lang.zho.script.conversion import (
    OpenCCConfig,
    get_zho_text_converted,
)
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


ZhoYueTranslationPromptZhoHant = TranslationPrompt(
    language=Language.zho_hant,
    schema_intro=PromptZhoHant.schema_intro,
    few_shot_intro=PromptZhoHant.few_shot_intro,
    few_shot_query_intro=PromptZhoHant.few_shot_query_intro,
    few_shot_answer_intro=PromptZhoHant.few_shot_answer_intro,
    answer_invalid_pre=PromptZhoHant.answer_invalid_pre,
    answer_invalid_post=PromptZhoHant.answer_invalid_post,
    difficulty_description=PromptZhoHant.difficulty_description,
    few_shot_description=PromptZhoHant.few_shot_description,
    verified_description=PromptZhoHant.verified_description,
    test_case_invalid_pre=PromptZhoHant.test_case_invalid_pre,
    test_case_invalid_post=PromptZhoHant.test_case_invalid_post,
    base_system_prompt=dedent_and_compact("""
        你負責根據粵文字幕，創作對應的標準中文字幕。

        每條粵文字幕都要輸出一條標準中文字幕。譯文要自然、通順，準確表達粵文字幕
        的意思、語氣、戲劇意圖和說話人意圖。不要逐字硬譯；可以調整措辭，使其
        更像自然的標準中文字幕。專名、固定稱呼、重複術語和字幕標記要在適合時
        保留或按標準中文習慣處理。

        輸出內容只能是生成的中文字幕正文。不要附加英文、備註、解釋、標籤、
        替代譯文、方括號內容、括號內容，或任何字幕以外的說明。
        """),
    input_pfx="yuewen_",
    input_desc_tpl="要翻譯成標準中文的粵文字幕 {idx}",
    output_pfx="zhongwen_",
    output_desc_tpl="字幕 {idx} 對應的標準中文譯文",
)
"""Text for traditional standard Chinese translation from written Cantonese."""

ZhoYueTranslationPromptZhoHans = ZhoYueTranslationPromptZhoHant.transformed(
    Language.zho_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.t2s),
)
"""Text for simplified standard Chinese translation from written Cantonese."""

ZhoYueGapTranslationPromptZhoHant = GapTranslationPrompt(
    language=Language.zho_hant,
    schema_intro=PromptZhoHant.schema_intro,
    few_shot_intro=PromptZhoHant.few_shot_intro,
    few_shot_query_intro=PromptZhoHant.few_shot_query_intro,
    few_shot_answer_intro=PromptZhoHant.few_shot_answer_intro,
    answer_invalid_pre=PromptZhoHant.answer_invalid_pre,
    answer_invalid_post=PromptZhoHant.answer_invalid_post,
    difficulty_description=PromptZhoHant.difficulty_description,
    few_shot_description=PromptZhoHant.few_shot_description,
    verified_description=PromptZhoHant.verified_description,
    test_case_invalid_pre=PromptZhoHant.test_case_invalid_pre,
    test_case_invalid_post=PromptZhoHant.test_case_invalid_post,
    base_system_prompt=dedent_and_compact("""
        你負責根據對應的粵文字幕，補翻譯缺失的標準中文字幕。
        只有當某行現有中文字幕爲空字符串時，才需要提供譯文。
        如果某行已經有中文內容，不要修改，該行請輸出空字符串。
        譯文要自然、通順，語氣和用詞要儘量貼近附近已有的中文字幕。
        粵文字幕是意思來源；譯文不需要逐字對應，但要準確表達該行意思。
        輸出內容只能是字幕正文本身，不要附加英文、備註、解釋、標籤、
        方括號內容、括號內容，或任何譯文以外的說明。
        如果不需要翻譯，就輸出空字符串。
        """),
    src_1_pfx="zhongwen_",
    src_1_desc_tpl="字幕 {idx} 現有的中文內容；如果爲空就代表要翻譯",
    src_2_pfx="yuewen_",
    src_2_desc_tpl="字幕 {idx} 對應的粵文字幕",
    output_pfx="zhongwen_",
    output_desc_tpl='字幕 {idx} 譯好後的標準中文正文；如果不需要翻譯請輸出 ""。'
    "不要包含英文、備註、解釋、標籤或者括號說明。",
    output_unmodified_err_tpl="字幕 {idx} 已經有中文內容，該行輸出必須爲空字符串。",
    output_contains_note_err_tpl=(
        "字幕 {idx} 包含英文或者備註說明；只可以輸出中文字幕正文。"
    ),
)
"""Text for traditional standard Chinese gap translation using Cantonese."""

ZhoYueGapTranslationPromptZhoHans = ZhoYueGapTranslationPromptZhoHant.transformed(
    Language.zho_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.t2s),
)
"""Text for simplified standard Chinese gap translation using Cantonese."""

ZhoYueGuidedTranslationPromptZhoHant = GuidedTranslationPrompt(
    language=Language.zho_hant,
    schema_intro=PromptZhoHant.schema_intro,
    few_shot_intro=PromptZhoHant.few_shot_intro,
    few_shot_query_intro=PromptZhoHant.few_shot_query_intro,
    few_shot_answer_intro=PromptZhoHant.few_shot_answer_intro,
    answer_invalid_pre=PromptZhoHant.answer_invalid_pre,
    answer_invalid_post=PromptZhoHant.answer_invalid_post,
    difficulty_description=PromptZhoHant.difficulty_description,
    few_shot_description=PromptZhoHant.few_shot_description,
    verified_description=PromptZhoHant.verified_description,
    test_case_invalid_pre=PromptZhoHant.test_case_invalid_pre,
    test_case_invalid_post=PromptZhoHant.test_case_invalid_post,
    base_system_prompt=dedent_and_compact("""
        你負責根據粵文字幕，創作對應的標準中文字幕。你也會收到同一段場景的
        既有中文字幕，作爲參考材料。

        每條粵文字幕都要輸出一條標準中文字幕。譯文要準確表達粵文字幕的意思、
        語氣、戲劇意圖和說話人意圖。既有中文字幕是角色名、專名、重複術語、
        語域和固定說法的參考；當它和粵文字幕意思兼容時，儘量沿用。
        如果粵文字幕和既有中文字幕有差異，要優先按粵文意思翻譯，同時保留
        已經建立好的名詞和稱呼。

        輸出內容只能是生成的中文字幕正文。不要附加英文、備註、解釋、標籤、
        替代譯文、方括號內容、括號內容，或任何字幕以外的說明。
        """),
    src_1_pfx="yuewen_",
    src_1_desc_tpl="要翻譯成標準中文的粵文字幕 {idx}",
    src_2_pfx="zhongwen_reference_",
    src_2_desc_tpl="同一段場景的既有標準中文參考字幕 {idx}",
    output_pfx="zhongwen_",
    output_desc_tpl="字幕 {idx} 對應的標準中文譯文",
)
"""Text for traditional guided standard Chinese translation from Cantonese."""

ZhoYueGuidedTranslationPromptZhoHans = ZhoYueGuidedTranslationPromptZhoHant.transformed(
    Language.zho_hans,
    partial(get_zho_text_converted, config=OpenCCConfig.t2s),
)
"""Text for simplified guided standard Chinese translation from Cantonese."""
