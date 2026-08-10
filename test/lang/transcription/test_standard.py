#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for language-specific transcription configuration."""

from __future__ import annotations

from typing import cast
from unittest.mock import Mock, patch

from scinoephile.core import Language
from scinoephile.core.llms import LLMProvider
from scinoephile.lang.transcription.standard import DEFAULT_PROMPTS, get_transcriber
from scinoephile.lang.yue.transcription_validation import (
    CantoneseTranscriptionAlignmentScorer,
)
from scinoephile.llms.transcription import TranscriptionTestCase


def test_cantonese_prompts_distinguish_single_and_multiple_sources():
    """Prompts should preserve one source but reject isolated multisource wording."""
    traditional_prompt = DEFAULT_PROMPTS[Language.yue_hant].base_system_prompt
    simplified_prompt = DEFAULT_PROMPTS[Language.yue_hans].base_system_prompt

    assert "如果查詢只有一個來源" in traditional_prompt
    assert "如果查詢有多個來源" in traditional_prompt
    assert "只出現喺單一來源" in traditional_prompt
    assert "唔係獨立嘅詞彙證據" in traditional_prompt
    assert "同語言分類一致就收錄" in traditional_prompt
    assert "如果查询只有一个来源" in simplified_prompt
    assert "如果查询有多个来源" in simplified_prompt
    assert "只出现喺单一来源" in simplified_prompt
    assert "唔系独立嘅词汇证据" in simplified_prompt
    assert "同语言分类一致就收录" in simplified_prompt


def test_get_transcriber_loads_defaults_only_when_shared_test_cases_are_omitted():
    """Default cases should load for None without replacing an explicit empty list."""
    provider = Mock(spec=LLMProvider, cache_identity={"implementation": "test"})
    loader_path = "scinoephile.lang.transcription.standard.load_shared_test_cases"

    with patch(loader_path, return_value=()) as load_shared_test_cases:
        transcriber = get_transcriber(Language.yue_hant, provider=provider, no_op=True)

    load_shared_test_cases.assert_called_once_with(
        transcriber.manager_cls, DEFAULT_PROMPTS[Language.yue_hant], ()
    )
    test_case_cls = cast(type[TranscriptionTestCase], transcriber.test_case_cls)
    assert isinstance(
        test_case_cls.alignment_scorer, CantoneseTranscriptionAlignmentScorer
    )

    with patch(loader_path) as load_shared_test_cases:
        get_transcriber(
            Language.yue_hant, shared_test_cases=[], provider=provider, no_op=True
        )

    load_shared_test_cases.assert_not_called()
