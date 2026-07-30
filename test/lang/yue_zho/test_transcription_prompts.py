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

        assert prompt.changes == "yuewen_xiugai"
        assert prompt.first_owned_index == "fuze_qishi_xuhao"
        assert prompt.last_owned_index == "fuze_jieshu_xuhao"
        assert "yuewen_changes" not in prompt.base_system_prompt
        assert "fuze_qishi_xuhao" in prompt.base_system_prompt
        assert "fuze_jieshu_xuhao" in prompt.base_system_prompt
        assert set(properties) == {"yuewen_xiugai"}
        assert len(prompt.legacy_cache_prompts) == 1
        legacy_prompt = prompt.legacy_cache_prompts[0]
        assert isinstance(
            legacy_prompt, BlockDelineationPrompt | BlockPunctuationPrompt
        )
        assert legacy_prompt.changes == "yuewen_changes"


def test_block_prompts_require_local_index_and_character_conservation_checks():
    """Block prompts should make sparse-window invariants explicit."""
    delineation_prompt = YueZhoBlockDelineationPromptYueHant.base_system_prompt
    punctuation_prompt = YueZhoBlockPunctuationPromptYueHant.base_system_prompt

    assert "本地索引" in delineation_prompt
    assert "左邊嘅上下文只供閱讀" in delineation_prompt
    assert "緊接嘅下一個索引" in delineation_prompt
    assert "每個原有字符只可以出現一次" in delineation_prompt
    assert "切割位置" in delineation_prompt
    assert "不重疊、無缺口、首尾相接" in delineation_prompt
    assert "直接由不可變字符帶複製" in delineation_prompt
    assert "唔好憑記憶重新輸入" in delineation_prompt
    assert "回答之前必須做最後核對" in delineation_prompt
    assert "寧願返回空列表" in delineation_prompt
    assert "下一次唔好沿用呢個錯誤答案" in (
        YueZhoBlockDelineationPromptYueHant.target_chars_changed_err_tpl
    )
    assert "本地索引" in punctuation_prompt
    assert "相鄰索引" in punctuation_prompt
    assert "簡繁體唔一致" in punctuation_prompt
    assert "呢個步驟唔負責改文字" in punctuation_prompt
    assert "回答之前必須逐個核對" in punctuation_prompt
    assert "必須從答案刪除" in punctuation_prompt
    assert "原有簡繁字形" in (
        YueZhoBlockPunctuationPromptYueHant.target_chars_changed_err_tpl
    )
