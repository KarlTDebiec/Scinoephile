#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for written Cantonese transcription prompt correspondence fields."""

from __future__ import annotations

from scinoephile.lang.yue_zho.transcription import (
    YueZhoAdvisoryBlockDelineationPromptYueHant,
    YueZhoBlockDelineationPromptYueHans,
    YueZhoBlockDelineationPromptYueHant,
    YueZhoBlockPunctuationPromptYueHans,
    YueZhoBlockPunctuationPromptYueHant,
    YueZhoCandidateBlockDelineationPromptYueHant,
)
from scinoephile.llms.block_delineation import (
    BlockDelineationManager,
    BlockDelineationPrompt,
)
from scinoephile.llms.block_punctuation import BlockPunctuationManager


def test_block_answer_change_alias_is_pinyin():
    """Block answers should expose a fully pinyin sparse-change field name."""
    prompts_and_managers = (
        (YueZhoBlockDelineationPromptYueHans, BlockDelineationManager),
        (YueZhoBlockDelineationPromptYueHant, BlockDelineationManager),
        (YueZhoBlockPunctuationPromptYueHans, BlockPunctuationManager),
        (YueZhoBlockPunctuationPromptYueHant, BlockPunctuationManager),
    )

    for prompt, manager_cls in prompts_and_managers:
        answer_cls = manager_cls.get_answer_cls(prompt)
        properties = answer_cls.model_json_schema(by_alias=True)["properties"]

        expected_changes = (
            "bianjie_xiugai"
            if isinstance(prompt, BlockDelineationPrompt)
            else "yuewen_xiugai"
        )
        assert prompt.changes == expected_changes
        assert prompt.first_owned_index == "fuze_qishi_xuhao"
        assert prompt.last_owned_index == "fuze_jieshu_xuhao"
        assert "yuewen_changes" not in prompt.base_system_prompt
        assert "fuze_qishi_xuhao" in prompt.base_system_prompt
        assert "fuze_jieshu_xuhao" in prompt.base_system_prompt
        assert set(properties) == {expected_changes}
        if isinstance(prompt, BlockDelineationPrompt):
            assert len(prompt.legacy_cache_prompts) == 1
        else:
            assert not prompt.legacy_cache_prompts

    for prompt in (
        YueZhoBlockDelineationPromptYueHans,
        YueZhoBlockDelineationPromptYueHant,
    ):
        change_cls = BlockDelineationManager.get_change_cls(prompt)
        assert set(change_cls.model_json_schema(by_alias=True)["properties"]) == {
            "xuhao",
            "yidong_zifu_shu",
        }
        boundary_cls = BlockDelineationManager.get_boundary_cls(prompt)
        assert set(boundary_cls.model_json_schema(by_alias=True)["properties"]) == {
            "xuhao",
            "yuanben_pianyi",
            "zuixiao_yidong",
            "zuida_yidong",
        }


def test_block_delineation_prompt_requires_reconstruction_checks():
    """Block delineation prompt should make reconstruction invariants explicit."""
    delineation_prompt = YueZhoBlockDelineationPromptYueHant.base_system_prompt

    assert "本地索引" in delineation_prompt
    assert "不可變嘅字符帶" in delineation_prompt
    assert "重新輸入任何粵文" in delineation_prompt
    assert "正數將分界向右移" in delineation_prompt
    assert "負數將分界向左移" in delineation_prompt
    assert "Unicode 字符" in delineation_prompt
    assert "同時套用" in delineation_prompt
    assert "唔好返回 0" in delineation_prompt
    assert "被跨過嘅分界摺疊到同一位置" in delineation_prompt
    assert "互相越過或者超出字符帶首尾" in delineation_prompt
    assert "原本分界絕對位置" in delineation_prompt
    assert "返回同冇返回嘅全部分界新位置" in delineation_prompt
    assert "唔係某條輸出字幕" in delineation_prompt
    assert "返回較少項目或者空列表" in delineation_prompt
    assert "連續幾個完整說話單位都錯配" in delineation_prompt
    assert "bianjie_fanwei" in delineation_prompt
    assert "yuanben_pianyi" in delineation_prompt
    assert "fuze_jieshu_xuhao 唔係" in delineation_prompt
    assert "最後分界" in delineation_prompt
    assert "最終重組分界核對清單" in delineation_prompt
    assert "只剩標點或者空格" in delineation_prompt
    assert YueZhoBlockDelineationPromptYueHant.validate_output_quality is True
    assert "冇任何有效嘅 yidong_zifu_shu 範圍" in (
        YueZhoBlockDelineationPromptYueHant.boundary_neighbors_crossed_err_tpl
    )


def test_specialized_block_delineation_prompts_localize_validation():
    """Specialized delineation prompts should retry in written Cantonese."""
    for prompt in (
        YueZhoAdvisoryBlockDelineationPromptYueHant,
        YueZhoCandidateBlockDelineationPromptYueHant,
    ):
        error = prompt.boundary_shift_invalid_err(
            index=2, offset=13, original_offset=11, previous_offset=11, next_offset=11
        )

        assert error.startswith("索引 2 之後嘅分界")
        assert "yidong_zifu_shu 必須喺 0 至 0 之間" in error
        assert prompt.guide_text_desc == "中文字幕文字"
        assert prompt.guide_indices_err.startswith("zhongwen 索引必須")
        assert prompt.change_indices_err.startswith("bianjie_xiugai 索引必須")
        assert prompt.leading_closing_punctuation_err_tpl.startswith("重組後字幕索引")
        assert prompt.legacy_cache_prompts

    assert "shijian_jianyi 必須" in (
        YueZhoAdvisoryBlockDelineationPromptYueHant.boundary_suggestions_err
    )
    assert "houxuan 必須" in (
        YueZhoCandidateBlockDelineationPromptYueHant.boundary_candidates_err
    )
    assert "必須揀自所提供嘅 houxuan" in (
        YueZhoCandidateBlockDelineationPromptYueHant.change_shift_not_candidate_err_tpl
    )


def test_block_punctuation_prompt_requires_character_conservation_checks():
    """Block punctuation prompt should make character invariants explicit."""
    punctuation_prompt = YueZhoBlockPunctuationPromptYueHant.base_system_prompt

    assert "本地索引" in punctuation_prompt
    assert "相鄰索引" in punctuation_prompt
    assert "簡繁體唔一致" in punctuation_prompt
    assert "呢個步驟唔負責改文字" in punctuation_prompt
    assert "回答之前必須逐個核對" in punctuation_prompt
    assert "必須從答案刪除" in punctuation_prompt
    assert "機械式標點任務" in punctuation_prompt
    assert "絕對唔可以用嚟補回" in punctuation_prompt
    assert "繁體化係之後另一個步驟" in punctuation_prompt
    assert "wenben 完全空白" in punctuation_prompt
    assert "第一個字符" in punctuation_prompt
    assert "最後一個字符" in punctuation_prompt
    assert "開頭或者結尾只得標點" in punctuation_prompt
    assert "逐段核對連續重複字符" in punctuation_prompt
    assert "重複片段嘅" in punctuation_prompt
    assert "出現次數" in punctuation_prompt
    assert "孤零零留喺字幕開頭" in punctuation_prompt
    assert "只剩標點或者空格" in punctuation_prompt
    assert "全形中文句子標點" in punctuation_prompt
    assert "原本只含標點同空格" in punctuation_prompt
    assert "強烈疑問" in punctuation_prompt
    assert "最終重組分界核對清單" in punctuation_prompt
    assert YueZhoBlockPunctuationPromptYueHant.validate_output_quality is True
    assert "原有簡繁字形" in (
        YueZhoBlockPunctuationPromptYueHant.target_chars_changed_err_tpl
    )
    assert "漏咗重複字符" in (
        YueZhoBlockPunctuationPromptYueHant.target_chars_changed_err_tpl
    )
    assert "重複字詞或者短句" in (
        YueZhoBlockPunctuationPromptYueHant.target_chars_changed_err_tpl
    )
