#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Prompts for transcribing written Cantonese using standard Chinese references."""

from __future__ import annotations

from dataclasses import replace
from functools import partial

from scinoephile.core import Language
from scinoephile.core.text import dedent_and_compact
from scinoephile.lang.yue.prompts import YUE_HANT_PROMPT_FIELDS
from scinoephile.lang.zho.script.conversion import OpenCCConfig, get_zho_text_converted
from scinoephile.llms.block_delineation import BlockDelineationPrompt
from scinoephile.llms.block_punctuation import BlockPunctuationPrompt
from scinoephile.llms.delineation import DelineationPrompt
from scinoephile.llms.punctuation import PunctuationPrompt

__all__ = [
    "YueZhoBlockDelineationPromptYueHans",
    "YueZhoBlockDelineationPromptYueHant",
    "YueZhoBlockPunctuationPromptYueHans",
    "YueZhoBlockPunctuationPromptYueHant",
    "YueZhoDelineationPromptYueHans",
    "YueZhoDelineationPromptYueHant",
    "YueZhoPunctuationPromptYueHans",
    "YueZhoPunctuationPromptYueHant",
]


def _get_prompt_with_pinyin_change_alias[
    TPrompt: BlockDelineationPrompt | BlockPunctuationPrompt
](legacy_prompt: TPrompt) -> TPrompt:
    """Replace the mixed-language sparse-change alias while retaining its cache.

    Arguments:
        legacy_prompt: predecessor prompt using the mixed-language alias
    Returns:
        current prompt using a fully pinyin alias
    """
    extra_replacements: dict[str, str] = {}
    if isinstance(legacy_prompt, BlockPunctuationPrompt):
        extra_replacements["change_index_not_owned_err"] = (
            legacy_prompt.change_index_not_owned_err.replace(
                "yuewen_changes", "yuewen_xiugai"
            )
        )
    return replace(
        legacy_prompt,
        base_system_prompt=legacy_prompt.base_system_prompt.replace(
            "yuewen_changes", "yuewen_xiugai"
        ),
        changes="yuewen_xiugai",
        change_indices_err=legacy_prompt.change_indices_err.replace(
            "yuewen_changes", "yuewen_xiugai"
        ),
        change_index_missing_err=legacy_prompt.change_index_missing_err.replace(
            "yuewen_changes", "yuewen_xiugai"
        ),
        target_chars_changed_err_tpl=legacy_prompt.target_chars_changed_err_tpl.replace(
            "yuewen_changes", "yuewen_xiugai"
        ),
        legacy_cache_prompts=(legacy_prompt,),
        **extra_replacements,
    )


_YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_LEGACY = BlockDelineationPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責將一個廣東話口語粵文轉寫視窗，同中文字幕逐條對齊。
        你會收到有序嘅中文字幕 (zhongwen)，以及根據時間初步分配、
        索引完全相同嘅粵文字幕 (yuewen_initial)。
        fuze_qishi_xuhao 同 fuze_jieshu_xuhao 表示呢個視窗負責嘅本地索引範圍，
        兩端都包括；範圍外嘅字幕只係重疊上下文。
        呢個視窗負責範圍內每個索引之後嘅分界；如果嗰個索引已經係視窗最後一條，
        就冇下一個分界需要處理。請逐個檢查所有負責嘅分界，唔好因為答案係稀疏格式
        就只檢查少數索引；如果每個索引都要改，yuewen_changes 可以包含每個索引。
        將所有 yuewen_initial 依次串連成一條不可變嘅字符帶；答案只可以用原有次序
        將呢條字符帶切成連續片段，重新分配畀各索引。
        只喺 yuewen_changes 返回文字需要改動嘅索引；唔需要改嘅索引唔好返回。
        如果一條字幕改成空白，仍然要明確返回嗰個索引同空字串。
        一次分界修正通常需要返回分界兩邊所有受影響嘅索引。
        只有為咗表達跨過負責範圍邊緣嘅分界調整，先可以返回上下文索引；
        唔好改動同負責分界無關嘅上下文。
        重組後嘅粵文必須包含 yuewen_initial 全部字符，字符次序亦必須完全相同。
        唔可以加入、刪除、替換或者重新排序任何字符，包括原有標點同空格。
        唔好從中文字幕拷貝漢字。
        如果所有分界都正確，yuewen_changes 返回空列表。"""),
    guides="zhongwen",
    guides_desc="同一查詢視窗完整而有序嘅中文字幕",
    targets="yuewen_initial",
    targets_desc="查詢視窗內按時間初步分配、索引同中文字幕一致嘅粵文字幕",
    first_owned_index="fuze_qishi_xuhao",
    first_owned_index_desc="呢個視窗負責嘅第一個本地粵文索引（包含）",
    last_owned_index="fuze_jieshu_xuhao",
    last_owned_index_desc="呢個視窗負責嘅最後一個本地粵文索引（包含）",
    changes="yuewen_changes",
    changes_desc="只包含文字需要改動嘅粵文字幕",
    index="xuhao",
    index_desc="由1開始嘅中文字幕索引",
    text="wenben",
    guide_text_desc="中文字幕文字",
    target_text_desc="初步分配嘅粵文字幕文字",
    change_text_desc="呢個索引調整分界後嘅完整粵文字幕文字",
    guide_indices_err="zhongwen 索引必須由1開始、連續而且依次排列。",
    target_indices_err="yuewen_initial 索引必須同 zhongwen 索引完全一致。",
    owned_indices_err=(
        "fuze_qishi_xuhao 同 fuze_jieshu_xuhao 必須一齊省略，或者喺查詢索引內"
        "組成由細到大、包括兩端嘅範圍。"
    ),
    change_indices_err="yuewen_changes 索引必須唯一而且由細到大排列。",
    change_index_missing_err=(
        "yuewen_changes 每個索引都必須對應 zhongwen 入面嘅索引。"
    ),
    target_chars_changed_err_tpl=(
        "套用 yuewen_changes 後嘅整段粵文冇依次保留 yuewen_initial 全部字符。"
        "第一個差異喺重組後索引 {index}、由零開始嘅字符位置 {offset}："
        "期望 {expected_character}，收到 {received_character}。\n"
        "期望附近: {expected_context}\n收到附近: {received_context}\n"
        "期望: {expected}\n收到: {received}"
    ),
)
"""Predecessor prompt using the mixed-language sparse-answer alias."""

YueZhoBlockDelineationPromptYueHant = _get_prompt_with_pinyin_change_alias(
    _YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_LEGACY
)
"""Text for Traditional Cantonese/Chinese block delineation."""

YueZhoBlockDelineationPromptYueHans = YueZhoBlockDelineationPromptYueHant.transformed(
    Language.yue_hans, partial(get_zho_text_converted, config=OpenCCConfig.hk2s)
)
"""Text for Simplified Cantonese/Chinese block delineation."""

_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_LEGACY = BlockPunctuationPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責參考一個中文字幕視窗，為已經逐條對齊嘅粵文字幕補上標點同空格。
        你會收到有序嘅中文字幕 (zhongwen)，以及索引完全相同、
        已經確定分界嘅粵文字幕 (yuewen_to_punctuate)。
        fuze_qishi_xuhao 同 fuze_jieshu_xuhao 表示呢個視窗負責嘅本地索引範圍，
        兩端都包括；範圍外嘅字幕只係重疊上下文，唔可以喺答案返回。
        請逐個檢查負責範圍內每一條字幕，唔好因為答案係稀疏格式就只檢查少數索引；
        如果每條都要改，yuewen_changes 可以包含負責範圍內每個索引。
        只喺 yuewen_changes 返回標點或者空格需要改動嘅索引；
        唔需要改嘅索引唔好返回。
        每個返回項目必須包含嗰個索引完整而加好標點嘅粵文字幕。
        只可以調整同一個索引入面嘅標點同空格；唔可以喺索引之間移動文字。
        除咗標點同空格之外，唔可以加入、刪除、替換或者重新排序任何粵文字符。
        唔好從中文字幕拷貝漢字。
        如果所有粵文標點都正確，yuewen_changes 返回空列表。"""),
    guides="zhongwen",
    guides_desc="同一查詢視窗完整而有序嘅中文字幕",
    targets="yuewen_to_punctuate",
    targets_desc="查詢視窗內分界已經確定、索引同中文字幕一致嘅粵文字幕",
    first_owned_index="fuze_qishi_xuhao",
    first_owned_index_desc="呢個視窗負責嘅第一個本地粵文索引（包含）",
    last_owned_index="fuze_jieshu_xuhao",
    last_owned_index_desc="呢個視窗負責嘅最後一個本地粵文索引（包含）",
    changes="yuewen_changes",
    changes_desc="只包含標點或者空格需要改動嘅粵文字幕",
    index="xuhao",
    index_desc="由1開始嘅中文字幕索引",
    text="wenben",
    guide_text_desc="中文字幕文字",
    target_text_desc="要檢查標點嘅粵文字幕文字",
    change_text_desc="呢個索引調整標點後嘅完整粵文字幕文字",
    guide_indices_err="zhongwen 索引必須由1開始、連續而且依次排列。",
    target_indices_err="yuewen_to_punctuate 索引必須同 zhongwen 索引完全一致。",
    owned_indices_err=(
        "fuze_qishi_xuhao 同 fuze_jieshu_xuhao 必須一齊省略，或者喺查詢索引內"
        "組成由細到大、包括兩端嘅範圍。"
    ),
    change_indices_err="yuewen_changes 索引必須唯一而且由細到大排列。",
    change_index_missing_err=(
        "yuewen_changes 每個索引都必須對應 zhongwen 入面嘅索引。"
    ),
    change_index_not_owned_err=(
        "yuewen_changes 每個索引都必須喺 fuze_qishi_xuhao 至 "
        "fuze_jieshu_xuhao 嘅負責範圍內。"
    ),
    target_chars_changed_err_tpl=(
        "索引 {index} 嘅標點修改移除標點同空格後，冇保留原有粵文字符。"
        "第一個差異喺由零開始嘅字符位置 {offset}：期望 {expected_character}，"
        "收到 {received_character}。\n期望附近: {expected_context}\n"
        "收到附近: {received_context}\n期望: {expected}\n收到: {received}"
    ),
)
"""Predecessor prompt using the mixed-language sparse-answer alias."""

YueZhoBlockPunctuationPromptYueHant = _get_prompt_with_pinyin_change_alias(
    _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_LEGACY
)
"""Text for Traditional Cantonese/Chinese block punctuation."""

YueZhoBlockPunctuationPromptYueHans = YueZhoBlockPunctuationPromptYueHant.transformed(
    Language.yue_hans, partial(get_zho_text_converted, config=OpenCCConfig.hk2s)
)
"""Text for Simplified Cantonese/Chinese block punctuation."""

YueZhoDelineationPromptYueHant = DelineationPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責將廣東話口語嘅粵文字幕同對應嘅中文字幕對齊。
        你會收到一條中文字幕 (zhongwen_1) 同一條初步粵文字幕 (yuewen_1)，
        以及第二條中文字幕 (zhongwen_2) 同第二條初步粵文字幕 (yuewen_2)。
        請閲讀 zhongwen_1、zhongwen_2 同 yuewen_1、yuewen_2，
        調整 yuewen_1 同 yuewen_2 之間嘅分界，使內容同 zhongwen_1 同 zhongwen_2 對齊。
        即係將 yuewen_1 末尾嘅字符移到 yuewen_2 開頭，
        或者將 yuewen_2 開頭嘅字符移到 yuewen_1 末尾。
        請喺 yuewen_1_yidong 同 yuewen_2_yidong 返回調整後嘅粵文字幕。
        如果唔需要調整，請 yuewen_1_yidong 同 yuewen_2_yidong 都返回空字串。"""),
    ref_sub_1="zhongwen_1",
    ref_sub_1_desc="已知字幕1嘅中文",
    ref_sub_2="zhongwen_2",
    ref_sub_2_desc="已知字幕2嘅中文",
    target_sub_1="yuewen_1",
    target_sub_1_desc="初步字幕1嘅粵文",
    target_sub_2="yuewen_2",
    target_sub_2_desc="初步字幕2嘅粵文",
    target_subs_missing_err="查詢要有 yuewen_1、yuewen_2，或者兩個都有。",
    target_sub_1_shifted="yuewen_1_yidong",
    target_sub_1_shifted_desc="調整後字幕1嘅粵文",
    target_sub_2_shifted="yuewen_2_yidong",
    target_sub_2_shifted_desc="調整後字幕2嘅粵文",
    target_subs_unchanged_err=(
        "回答嘅 yuewen_1_yidong 同 yuewen_2_yidong 同查詢嘅 yuewen_1、yuewen_2 "
        "一樣；如果唔需要調整，yuewen_1_yidong 同 yuewen_2_yidong 要返空字串。"
    ),
    target_chars_changed_err_tpl=(
        "回答裏拼埋嘅 yuewen_1_yidong 同 yuewen_2_yidong 同查詢拼埋嘅 "
        "yuewen_1 同 yuewen_2 唔一致：\n"
        "期望: {expected}\n"
        "收到: {received}"
    ),
)
"""Text for LLM correspondence for traditional written Cantonese delineation."""

YueZhoDelineationPromptYueHans = YueZhoDelineationPromptYueHant.transformed(
    Language.yue_hans, partial(get_zho_text_converted, config=OpenCCConfig.hk2s)
)
"""Text for LLM correspondence for simplified written Cantonese delineation."""

YueZhoPunctuationPromptYueHant = PunctuationPrompt(
    language=Language.yue_hant,
    **YUE_HANT_PROMPT_FIELDS,
    base_system_prompt=dedent_and_compact("""
        你負責將廣東話口語嘅粵文字幕同對應嘅中文字幕對齊。
        你會收到一條中文字幕，以及同一條字幕對應嘅多行粵文轉寫。
        多行粵文代表口語停頓拆開嘅行。
        你嘅主要任務係為粵文補上標點同空格。
        請先將所有粵文行整理成一行，再參考中文字幕補上標點同空格。
        必須包含所有粵文字，整理成一行。
        唔好從中文字幕拷貝漢字。
        只可以調整粵文嘅標點同空格以配合中文字幕。
        除咗標點同空格之外唔好改任何粵文內容。"""),
    ref_sub="zhongwen",
    ref_sub_desc="對應嘅中文字幕",
    target_subs="yuewen_to_punctuate",
    target_subs_desc="要整理同加標點嘅粵文字幕行",
    ref_sub_missing_err="查詢必須包含對應嘅中文字幕。",
    target_subs_missing_err="查詢必須包含要整理同加標點嘅粵文字幕行。",
    target_sub_punctuated="yuewen_punctuated",
    target_sub_punctuated_desc="整理同加標點後嘅粵文字幕",
    target_sub_punctuated_missing_err="答案必須包含整理同加標點後嘅粵文字幕。",
    target_chars_changed_err_tpl=(
        "回答嘅 yuewen_punctuated 移除標點同空格後，同查詢入面拼埋嘅 "
        "yuewen_to_punctuate 唔一致：\n"
        "期望: {expected}\n"
        "收到: {received}"
    ),
)
"""Text for traditional written Cantonese/standard Chinese punctuation."""

YueZhoPunctuationPromptYueHans = YueZhoPunctuationPromptYueHant.transformed(
    Language.yue_hans, partial(get_zho_text_converted, config=OpenCCConfig.hk2s)
)
"""Text for simplified written Cantonese/standard Chinese punctuation."""
