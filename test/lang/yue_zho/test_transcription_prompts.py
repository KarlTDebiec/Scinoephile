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
