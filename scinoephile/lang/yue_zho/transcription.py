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
        所有 xuhao 都係呢個視窗入面由 1 開始嘅本地索引；只可以使用 zhongwen
        實際顯示嘅索引，唔好推算或者使用全片索引。
        呢個視窗負責範圍內每個索引之後嘅分界；如果嗰個索引已經係視窗最後一條，
        就冇下一個分界需要處理。請逐個檢查所有負責嘅分界，唔好因為答案係稀疏格式
        就只檢查少數索引；如果每個索引都要改，yuewen_changes 可以包含每個索引。
        將所有 yuewen_initial 依次串連成一條不可變嘅字符帶；答案只可以用原有次序
        將呢條字符帶切成連續片段，重新分配畀各索引。每個原有字符只可以出現一次；
        唔好複製、重複或者補寫任何片段。
        將每個新分界當成不可變字符帶上面一個切割位置：先決定全部切割位置，
        然後先根據這些位置取出不重疊、無缺口、首尾相接的連續切片，
        最後才寫答案。唔好先根據字幕意思重新作句。
        決定新分界之後，必須直接由不可變字符帶複製每段連續原文去 wenben，
        包括原有標點同空格；唔好憑記憶重新輸入、改寫或者整理句子。
        只喺 yuewen_changes 返回文字需要改動嘅索引；唔需要改嘅索引唔好返回。
        如果一條字幕改成空白，仍然要明確返回嗰個索引同空字串。
        一次分界修正通常需要返回分界兩邊所有受影響嘅索引。
        負責範圍左邊嘅上下文只供閱讀，絕對唔可以喺答案返回。
        負責範圍右邊嘅上下文亦只供閱讀；只有調整 fuze_jieshu_xuhao 之後嗰個
        最後負責分界時，先可以連同緊接嘅下一個索引返回。再後嘅上下文唔可以返回。
        重組後嘅粵文必須包含 yuewen_initial 全部字符，字符次序亦必須完全相同。
        唔可以加入、刪除、替換或者重新排序任何字符，包括原有標點同空格。
        唔好從中文字幕拷貝漢字。
        回答之前必須做最後核對：先將 yuewen_changes 覆蓋相應索引，冇返回嘅索引
        已經保留 yuewen_initial 原文，唔好將佢哋再次抄入其他索引；再依次串連視窗內
        全部索引，包括上下文。串連結果必須同原本 yuewen_initial 字符帶逐字完全
        相同，否則先修正答案，唔好提交。
        如果你唔能確保上述逐字核對通過，寧願返回空列表，唔好猜測或重打原文。
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
    shift=None,
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
        "期望: {expected}\n收到: {received}\n"
        "下一次唔好沿用呢個錯誤答案；由原本 yuewen_initial 字符帶"
        "重新切分。每個新片段必須係字符帶一段連續切片，相鄰切片"
        "首尾相接、唔重疊、無缺口。如果唔能確保，yuewen_changes 返回空列表。"
    ),
)
"""Predecessor prompt using the mixed-language sparse-answer alias."""

_YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_TEXT = _get_prompt_with_pinyin_change_alias(
    _YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_LEGACY
)
"""Predecessor prompt returning complete replacement subtitle text."""

_YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V1 = replace(
    _YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_TEXT,
    base_system_prompt=dedent_and_compact("""
        你負責將一個廣東話口語粵文轉寫視窗，同中文字幕逐條對齊。
        你會收到有序嘅中文字幕 (zhongwen)，以及根據時間初步分配、
        索引完全相同嘅粵文字幕 (yuewen_initial)。
        fuze_qishi_xuhao 同 fuze_jieshu_xuhao 表示呢個視窗負責嘅本地索引範圍，
        兩端都包括；範圍外嘅字幕只係重疊上下文。
        所有 xuhao 都係呢個視窗入面由 1 開始嘅本地索引；只可以使用 zhongwen
        實際顯示嘅索引，唔好推算或者使用全片索引。
        呢個視窗負責範圍內每個索引之後嘅分界；如果嗰個索引已經係視窗最後一條，
        就冇下一個分界需要處理。請逐個檢查所有負責嘅分界。
        將所有 yuewen_initial 依次串連成一條不可變嘅字符帶。你唔需要、亦唔可以
        重新輸入任何粵文；答案只需要報告要移動嘅分界同移動字符數。
        bianjie_xiugai 每項嘅 xuhao 係分界前面嗰條字幕嘅本地索引；
        yidong_zifu_shu 係相對 yuewen_initial 原本分界嘅有正負號字符數：
        正數將分界向右移，亦即將下一條開頭嗰幾個字符撥入呢條；
        負數將分界向左移，亦即將呢條結尾嗰幾個字符撥入下一條。
        字符數按 Unicode 字符計，包括標點同空格。所有分界移動都以原本分界為基準、
        同時套用，唔係逐項順序套用。
        只返回真正需要移動嘅分界，唔好返回 0；項目必須按 xuhao 由細到大排列。
        只可以返回視窗負責嘅分界，左、右重疊上下文嘅分界都唔可以返回。
        一個移動可以越過冇返回嘅初步分界；程式會將被跨過嘅分界摺疊到同一位置，
        所以唔需要另外返回佢哋，期間嘅字幕亦可以變成空白。
        如果返回多個分界，佢哋移動後嘅位置必須仍然依次排列；返回嘅分界唔可以
        互相越過或者超出字符帶首尾。
        只根據粵語語意同中文字幕提示決定分界；唔好修正錯字、簡繁體、標點或者內容。
        如果所有負責分界都正確，bianjie_xiugai 返回空列表。"""),
    changes="bianjie_xiugai",
    changes_desc="只包含真正需要移動嘅粵文字幕分界",
    index_desc="要移動嘅分界前面嗰條字幕，由1開始嘅本地索引",
    shift="yidong_zifu_shu",
    shift_desc=(
        "分界相對 yuewen_initial 原位移動嘅有正負號 Unicode 字符數；正數向右，"
        "負數向左；被跨過而冇返回嘅初步分界會摺疊到同一位置"
    ),
    change_indices_err="bianjie_xiugai 索引必須唯一而且由細到大排列。",
    change_index_missing_err=("bianjie_xiugai 每個索引都必須對應呢個視窗負責嘅分界。"),
    change_shift_zero_err=(
        "yidong_zifu_shu 唔可以係 0；冇移動嘅分界唔好放入 bianjie_xiugai。"
    ),
    boundary_shift_invalid_err_tpl=(
        "索引 {index} 之後嘅分界移動到字符位置 {offset}，越過相鄰嘅已返回分界"
        " {previous_offset} 或 {next_offset}。下一次要以每個 yuewen_initial 原本"
        "分界為基準，同時套用所有移動；唔好逐項順序套用。"
    ),
    legacy_cache_prompts=(
        _YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_TEXT,
        *_YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_TEXT.legacy_cache_prompts,
    ),
)
"""Predecessor prompt using sparse boundary shifts."""

_YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V2 = replace(
    _YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V1,
    base_system_prompt=dedent_and_compact(f"""
        {_YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V1.base_system_prompt}
        回答之前，先按每條 yuewen_initial 嘅 Unicode 字符數，計出由字符帶開頭
        起計嘅全部原本分界絕對位置。對每個準備返回嘅項目，只可以用「原本絕對
        位置加 yidong_zifu_shu」計新位置。然後將返回同冇返回嘅全部分界新位置
        一齊由左至右核對：每個位置必須大過或等於前一個，而且細過或等於下一個，
        第一個唔可以小過 0，最後一個唔可以大過字符帶總長度。空白字幕可以令相鄰
        分界位置相同，但後面嘅分界絕對唔可以走到前面。任何一項唔符合，就要修正
        移動數或者刪除嗰項；唔好提交會互相越過嘅分界。"""),
    boundary_shift_invalid_err_tpl=(
        "索引 {index} 之後嘅分界移動到字符位置 {offset}，越過相鄰嘅最終分界"
        " {previous_offset} 或 {next_offset}。下一次先計出全部 yuewen_initial 原本"
        "分界嘅絕對字符位置，再分別加上各自嘅 yidong_zifu_shu；將返回同冇返回"
        "嘅全部最終位置一齊核對，必須由左至右大過或等於前一個。唔好逐項順序"
        "套用，亦唔好提交會互相越過嘅分界。"
    ),
    legacy_cache_prompts=(
        _YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V1,
        *_YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V1.legacy_cache_prompts,
    ),
)
"""Predecessor prompt checking absolute positions before returning shifts."""

_YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V3 = replace(
    _YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V2,
    base_system_prompt=dedent_and_compact(f"""
        {_YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V2.base_system_prompt}
        特別注意：yidong_zifu_shu 係「同一個累積分界」新舊絕對位置之差，
        唔係某條輸出字幕同 yuewen_initial 同一條字幕嘅長度差。前面分界嘅移動
        唔會改變後面分界計 yidong_zifu_shu 嘅基準；每項永遠只用自己原本嘅
        累積分界位置計算。"""),
    shift_desc=(
        "同一個累積分界相對 yuewen_initial 原位移動嘅有正負號 Unicode 字符數；"
        "唔係單條字幕嘅長度差；正數向右，負數向左；被跨過而冇返回嘅初步分界"
        "會摺疊到同一位置"
    ),
    boundary_shift_invalid_err_tpl=(
        "索引 {index} 之後嘅分界原本喺字符位置 {original_offset}，移動到 "
        "{offset}，越過相鄰嘅最終分界 {previous_offset} 或 {next_offset}。"
        "下一次呢個索引嘅 yidong_zifu_shu 必須喺 {minimum_shift} 至 "
        "{maximum_shift} 之間（包括兩端）；如果語意需要超出呢個範圍，就要一併"
        "修正被越過嘅已返回分界，或者刪除唔必要嘅項目。每項以自己原本累積"
        "分界為基準，唔好用單條字幕長度差，亦唔好逐項順序套用。"
    ),
    legacy_cache_prompts=(
        _YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V2,
        *_YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V2.legacy_cache_prompts,
    ),
)
"""Predecessor prompt clarifying cumulative boundary shifts."""

_YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V4 = replace(
    _YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V3,
    boundary_neighbors_crossed_err_tpl=(
        "相鄰嘅已返回分界最終位置 {previous_offset} 同 {next_offset} 本身已經"
        "前後倒轉，所以索引 {index} 冇任何有效嘅 yidong_zifu_shu 範圍。下一次"
        "唔好只改目前報錯嗰一項；由呢幾個相鄰分界成組重新計算，修正或者刪除"
        "一項或多項 bianjie_xiugai，直到全部最終位置由左至右排列。"
    ),
    legacy_cache_prompts=(
        _YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V3,
        *_YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V3.legacy_cache_prompts,
    ),
)
"""Predecessor prompt distinguishing already-crossed neighboring boundaries."""

YueZhoBlockDelineationPromptYueHant = replace(
    _YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V4,
    base_system_prompt=dedent_and_compact(f"""
        {_YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V4.base_system_prompt}
        如果一組準備返回嘅分界移動互相衝突，而你唔能夠一次過計出由左至右有序嘅
        全部最終位置，必須刪除嗰組有衝突嘅 bianjie_xiugai，保留初步分界。
        返回較少項目或者空列表，永遠好過提交互相越過嘅分界。唔好喺舊嘅錯誤答案
        上面逐項修補；每次都由原本 yuewen_initial 嘅累積分界重新計算。"""),
    boundary_neighbors_crossed_err_tpl=(
        _YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V4.boundary_neighbors_crossed_err_tpl
        + " 如果未能立即算出整組有效移動，最安全嘅修正係刪除造成衝突嘅整組 "
        "bianjie_xiugai，保留原本分界；唔好沿用上一個錯誤答案逐項再試。"
    ),
    legacy_cache_prompts=(
        _YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V4,
        *_YUE_ZHO_BLOCK_DELINEATION_PROMPT_YUE_HANT_SHIFTS_V4.legacy_cache_prompts,
    ),
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
        所有 xuhao 都係呢個視窗入面由 1 開始嘅本地索引；只可以使用 zhongwen
        實際顯示嘅索引，唔好推算或者使用全片索引。
        請逐個檢查負責範圍內每一條字幕，唔好因為答案係稀疏格式就只檢查少數索引；
        如果每條都要改，yuewen_changes 可以包含負責範圍內每個索引。
        只喺 yuewen_changes 返回標點或者空格需要改動嘅索引；
        唔需要改嘅索引唔好返回。
        每個返回項目必須包含嗰個索引完整而加好標點嘅粵文字幕。
        只可以調整同一個索引入面嘅標點同空格；唔可以喺索引之間移動文字。
        即使你認為初步分界錯、簡繁體唔一致、有錯別字或者口語唔通，
        都必須將每個非標點字符原樣留喺原本索引；呢個步驟唔負責改文字、
        轉換字形或者修正分界。
        唔可以將相鄰索引或者中文字幕嘅字詞複製入返回項目。
        除咗標點同空格之外，唔可以加入、刪除、替換或者重新排序任何粵文字符。
        唔好從中文字幕拷貝漢字。
        回答之前必須逐個核對每個返回項目：將佢同 yuewen_to_punctuate 同一索引
        各自移除全部標點同空格之後，粵文字符同次序必須逐字完全相同；否則先修正
        答案，唔好提交。
        再核對所有返回索引都喺 fuze_qishi_xuhao 至 fuze_jieshu_xuhao
        兩端包括嘅範圍內；如果唔喺範圍內，必須從答案刪除。
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
        "fuze_jieshu_xuhao 嘅負責範圍內。下一次回答要刪除全部範圍外索引。"
    ),
    target_chars_changed_err_tpl=(
        "索引 {index} 嘅標點修改移除標點同空格後，冇保留原有粵文字符。"
        "第一個差異喺由零開始嘅字符位置 {offset}：期望 {expected_character}，"
        "收到 {received_character}。\n期望附近: {expected_context}\n"
        "收到附近: {received_context}\n期望: {expected}\n收到: {received}\n"
        "下一次必須完全保留呢個索引原本嘅非標點字符，包括原有簡繁字形"
        "同錯別字；只可以改標點同空格，唔可以順便修正分界。"
    ),
)
"""Predecessor prompt using the mixed-language sparse-answer alias."""

_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V1 = (
    _get_prompt_with_pinyin_change_alias(
        _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_LEGACY
    )
)
"""Predecessor prompt enforcing target-character immutability."""

_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V2 = replace(
    _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V1,
    base_system_prompt=dedent_and_compact(f"""
        {_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V1.base_system_prompt}
        呢個係機械式標點任務，唔係改寫、校對或者補全任務。每個要返回嘅 wenben，
        必須先由同一個 yuewen_to_punctuate.wenben 逐字複製，再只插入、刪除或者
        更換標點同空格；唔好憑中文字幕或者語意重新寫成一句。中文字幕只可以幫你
        判斷標點位置，絕對唔可以用嚟補回粵文冇出現嘅字詞、語氣助詞、稱呼或者
        句尾字。亦唔可以刪走重複、唔通順或者你認為多餘嘅粵文字符，或者將任何字
        改成較正確、較常用、唔同簡繁體或者同音嘅字。提交之前再次移除新舊兩邊
        全部標點同空格；如果剩低嘅 Unicode 字符唔逐字相同，嗰項唔可以返回。"""),
    target_chars_changed_err_tpl=(
        _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V1.target_chars_changed_err_tpl
        + " 下一次由原本 yuewen_to_punctuate.wenben 機械複製，唔好憑中文字幕"
        "或者語意重寫；唔可以增減語氣助詞、補全句子或者更正任何字形。"
    ),
    legacy_cache_prompts=(
        _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V1,
        *_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V1.legacy_cache_prompts,
    ),
)
"""Predecessor prompt emphasizing mechanical character copying."""

_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V3 = replace(
    _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V2,
    base_system_prompt=dedent_and_compact(f"""
        {_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V2.base_system_prompt}
        yuewen_to_punctuate 可能係簡體、繁體或者兩者混合；繁體化係之後另一個步驟，
        呢度絕對唔可以轉換字形。如果某個 yuewen_to_punctuate.wenben 完全空白，
        佢冇任何標點可以修改，絕對唔可以喺 yuewen_xiugai 返回嗰個索引，亦唔可以
        用 zhongwen 補入內容。"""),
    legacy_cache_prompts=(
        _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V2,
        *_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V2.legacy_cache_prompts,
    ),
)
"""Predecessor prompt preserving mixed-script and empty target text."""

_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V4 = replace(
    _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V3,
    base_system_prompt=dedent_and_compact(f"""
        {_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V3.base_system_prompt}
        每個準備返回嘅 wenben 移除標點同空格之後，非標點字符數量、第一個字符、
        最後一個字符同完整次序，都必須同原本同一索引完全相同。唔可以喺開頭或者
        結尾加入語氣詞、稱呼或者其他字符，亦唔可以漏咗原文開頭或者結尾。
        如果核對失敗，唔好修改目前候選答案；必須由原本 yuewen_to_punctuate.wenben
        重新逐字複製，再只加入標點。"""),
    target_chars_changed_err_tpl=(
        _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V3.target_chars_changed_err_tpl
        + " 如果收到多咗非標點字符，刪除全部額外嘅開頭或結尾字符；如果收到少咗，"
        "由原文補返完全相同嘅字符。唔好用另一個語氣詞或者字去代替。放棄目前錯誤"
        "答案，由原本 yuewen_to_punctuate.wenben 重新逐字複製。"
    ),
    legacy_cache_prompts=(
        _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V3,
        *_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V3.legacy_cache_prompts,
    ),
)
"""Predecessor prompt checking complete target-character identity."""

_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V5 = replace(
    _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V4,
    base_system_prompt=dedent_and_compact(f"""
        {_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V4.base_system_prompt}
        即使 yuewen_to_punctuate.wenben 開頭或者結尾只得標點、睇落似係欠咗字，
        都只可以保留或者更換嗰個標點，絕對唔可以由 zhongwen、相鄰字幕或者語意
        猜測並補入任何漢字、語氣詞或者稱呼。句子唔完整係分界或者轉寫問題，唔係
        呢個標點步驟可以修正嘅問題。"""),
    legacy_cache_prompts=(
        _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V4,
        *_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V4.legacy_cache_prompts,
    ),
)
"""Predecessor prompt preserving incomplete target text."""

_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V6 = replace(
    _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V5,
    base_system_prompt=dedent_and_compact(f"""
        {_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V5.base_system_prompt}
        提交之前，對原文同答案分別移除標點同空格，再逐段核對連續重複字符嘅
        字符同出現次數；每段重複字符嘅長度必須完全相同。唔可以將兩個或以上
        相同字符縮成一個，亦唔可以用省略號代替任何一個重複字符。"""),
    target_chars_changed_err_tpl=(
        _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V5.target_chars_changed_err_tpl
        + " 如果差異係漏咗重複字符，必須由原文重新複製每一次出現；唔可以將"
        "重複字符合併，亦唔可以用省略號代替。"
    ),
    legacy_cache_prompts=(
        _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V5,
        *_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V5.legacy_cache_prompts,
    ),
)
"""Predecessor prompt preserving adjacent repeated characters."""

YueZhoBlockPunctuationPromptYueHant = replace(
    _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V6,
    base_system_prompt=dedent_and_compact(f"""
        {_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V6.base_system_prompt}
        如果同一個 yuewen_to_punctuate.wenben 有一段字詞或者短句重複出現，
        必須逐次由原文完整複製每一次出現，包括每次出現入面嘅語氣助詞；唔可以
        將其中一次縮短、合併或者省略任何非標點字符。提交之前要核對重複片段嘅
        出現次數，同埋每一次出現移除標點同空格後嘅完整字符次序。"""),
    target_chars_changed_err_tpl=(
        _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V6.target_chars_changed_err_tpl
        + " 如果原文有重複字詞或者短句，必須由原文逐次完整複製每一次出現，"
        "包括每次嘅語氣助詞；唔可以縮短、合併或者省略其中一次。"
    ),
    legacy_cache_prompts=(
        _YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V6,
        *_YUE_ZHO_BLOCK_PUNCTUATION_PROMPT_YUE_HANT_IMMUTABILITY_V6.legacy_cache_prompts,
    ),
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
