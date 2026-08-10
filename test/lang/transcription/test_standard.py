#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for language-specific transcription configuration."""

from __future__ import annotations

from scinoephile.core import Language
from scinoephile.lang.transcription.standard import DEFAULT_PROMPTS


def test_cantonese_prompts_reject_single_source_lexical_insertions():
    """Audio-analysis traces should not corroborate isolated ASR wording."""
    traditional_prompt = DEFAULT_PROMPTS[Language.yue_hant].base_system_prompt
    simplified_prompt = DEFAULT_PROMPTS[Language.yue_hans].base_system_prompt

    assert "只出現喺單一來源" in traditional_prompt
    assert "唔係獨立嘅詞彙證據" in traditional_prompt
    assert "同語言分類一致就收錄" in traditional_prompt
    assert "只出现喺单一来源" in simplified_prompt
    assert "唔系独立嘅词汇证据" in simplified_prompt
    assert "同语言分类一致就收录" in simplified_prompt
