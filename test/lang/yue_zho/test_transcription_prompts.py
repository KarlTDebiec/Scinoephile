#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for written Cantonese transcription prompt correspondence fields."""

from __future__ import annotations

from scinoephile.lang.yue_zho.transcription import (
    YueZhoBlockDelineationPromptYueHans,
    YueZhoBlockDelineationPromptYueHant,
    YueZhoBlockPunctuationPromptYueHans,
    YueZhoBlockPunctuationPromptYueHant,
)
from scinoephile.llms.block_delineation import (
    BlockDelineationManager,
    BlockDelineationPrompt,
)
from scinoephile.llms.block_punctuation import (
    BlockPunctuationManager,
    BlockPunctuationPrompt,
)


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
        expected_legacy_count = 6 if isinstance(prompt, BlockDelineationPrompt) else 5
        assert len(prompt.legacy_cache_prompts) == expected_legacy_count
        legacy_prompt = prompt.legacy_cache_prompts[-1]
        assert isinstance(
            legacy_prompt, BlockDelineationPrompt | BlockPunctuationPrompt
        )
        assert legacy_prompt.changes == "yuewen_changes"

    for prompt in (
        YueZhoBlockDelineationPromptYueHans,
        YueZhoBlockDelineationPromptYueHant,
    ):
        change_cls = BlockDelineationManager.get_change_cls(prompt)
        assert set(change_cls.model_json_schema(by_alias=True)["properties"]) == {
            "xuhao",
            "yidong_zifu_shu",
        }


def test_block_prompts_require_local_index_and_character_conservation_checks():
    """Block prompts should make sparse-window invariants explicit."""
    delineation_prompt = YueZhoBlockDelineationPromptYueHant.base_system_prompt
    punctuation_prompt = YueZhoBlockPunctuationPromptYueHant.base_system_prompt

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
    assert "冇任何有效嘅 yidong_zifu_shu 範圍" in (
        YueZhoBlockDelineationPromptYueHant.boundary_neighbors_crossed_err_tpl
    )
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
    assert "原有簡繁字形" in (
        YueZhoBlockPunctuationPromptYueHant.target_chars_changed_err_tpl
    )
