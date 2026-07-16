#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for guided transcription configuration and construction."""

from __future__ import annotations

from typing import cast
from unittest.mock import Mock

from pytest import raises

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.lang.transcription.guided import (
    DEFAULT_SPECS,
    get_guided_transcriber,
)
from scinoephile.lang.transcription.processor import DemucsMode, VADMode
from scinoephile.lang.yue.prompts import YUE_HANT_PROMPT_FIELDS
from scinoephile.lang.yue_zho.transcription import (
    YueZhoDelineationPromptYueHant,
    YueZhoPunctuationPromptYueHant,
)
from scinoephile.llms.delineation import DelineationManager


def test_default_specs_are_read_only_and_cover_yue_zho_scripts():
    """Test default specs cover both scripts for target and reference Chinese."""
    assert set(DEFAULT_SPECS) == {
        (Language.yue_hans, Language.zho_hans),
        (Language.yue_hans, Language.zho_hant),
        (Language.yue_hant, Language.zho_hans),
        (Language.yue_hant, Language.zho_hant),
    }
    assert (
        DEFAULT_SPECS[(Language.yue_hans, Language.zho_hans)]
        is DEFAULT_SPECS[(Language.yue_hans, Language.zho_hant)]
    )
    assert (
        DEFAULT_SPECS[(Language.yue_hant, Language.zho_hans)]
        is DEFAULT_SPECS[(Language.yue_hant, Language.zho_hant)]
    )
    assert (
        DEFAULT_SPECS[(Language.yue_hans, Language.zho_hans)].language_spec
        is DEFAULT_SPECS[(Language.yue_hant, Language.zho_hans)].language_spec
    )
    mutable_specs = cast(dict, DEFAULT_SPECS)
    with raises(TypeError):
        mutable_specs[(Language.eng, Language.zho_hans)] = DEFAULT_SPECS[
            (Language.yue_hans, Language.zho_hans)
        ]


def test_get_guided_transcriber_uses_registered_language_configuration(tmp_path):
    """Test factory configures language-specific prompts and Whisper language."""
    transcriber = get_guided_transcriber(
        Language.yue_hant,
        Language.zho_hans,
        provider=Mock(spec=LLMProvider),
        test_case_dir_path=tmp_path,
        delineation_test_cases=[],
        punctuation_test_cases=[],
    )

    assert transcriber.language is Language.yue_hant
    assert transcriber.reference_language is Language.zho_hans
    assert transcriber.demucs_mode is DemucsMode.AUTO
    assert transcriber.vad_mode is VADMode.AUTO
    assert transcriber.whisper_language == "yue"
    assert transcriber.segment_splitter is not None
    assert transcriber.aligner.delineation_queryer.prompt is (
        YueZhoDelineationPromptYueHant
    )
    assert transcriber.aligner.punctuation_queryer.prompt is (
        YueZhoPunctuationPromptYueHant
    )
    assert transcriber.vad_transcriber is not None
    assert transcriber.vad_transcriber.language == "yue"
    assert transcriber.no_vad_transcriber is not None
    assert transcriber.no_vad_transcriber.language == "yue"
    assert (tmp_path / "delineation").is_dir()
    assert (tmp_path / "punctuation").is_dir()


def test_get_guided_transcriber_uses_verified_cases_without_few_shot(tmp_path):
    """Test verified cases bypass the provider without entering the prompt."""
    test_case_cls = DelineationManager.get_test_case_cls(YueZhoDelineationPromptYueHant)
    verified_test_case = test_case_cls.model_validate(
        {
            "query": {
                "reference_one": "參考一",
                "reference_two": "參考二",
                "target_one": "目標一",
                "target_two": "目標二",
            },
            "answer": {},
            "verified": True,
        }
    )
    provider = Mock(spec=LLMProvider)
    transcriber = get_guided_transcriber(
        Language.yue_hant,
        Language.zho_hant,
        provider=provider,
        test_case_dir_path=tmp_path,
        delineation_test_cases=[verified_test_case],
        punctuation_test_cases=[],
    )
    queryer = transcriber.aligner.delineation_queryer
    pending_test_case = test_case_cls.model_validate(
        {"query": verified_test_case.query.model_dump()}
    )

    result = queryer(pending_test_case)

    assert result.answer == verified_test_case.answer
    assert result.verified is True
    assert queryer.few_shot_test_cases == {}
    provider.chat_completion.assert_not_called()


def test_get_guided_transcriber_rejects_unsupported_language_pair():
    """Test factory rejects language pairs absent from the registry."""
    with raises(ScinoephileError, match="eng <- zho-Hans"):
        get_guided_transcriber(Language.eng, Language.zho_hans)


def test_transcription_prompts_use_yue_hant_correspondence_fields():
    """Test Yue-Hant transcription prompts use Yue-Hant shared text."""
    for prompt in (
        YueZhoDelineationPromptYueHant,
        YueZhoPunctuationPromptYueHant,
    ):
        for field_name, expected in YUE_HANT_PROMPT_FIELDS.items():
            assert getattr(prompt, field_name) == expected
