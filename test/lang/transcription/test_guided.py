#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for guided transcription configuration and construction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast
from unittest.mock import Mock, patch

from pytest import raises

from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.core.llms.utils import save_test_cases_to_json
from scinoephile.lang.transcription.guided import (
    DEFAULT_SPECS,
    get_guided_transcriber,
)
from scinoephile.lang.transcription.transcriber import DemucsMode, VADMode
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
    assert any(
        path.parts[0] == "kob"
        for path in DEFAULT_SPECS[
            (Language.yue_hant, Language.zho_hant)
        ].delineation_json_paths
    )
    assert any(
        path.parts[0] == "kob"
        for path in DEFAULT_SPECS[
            (Language.yue_hant, Language.zho_hant)
        ].punctuation_json_paths
    )
    mutable_specs = cast(dict, DEFAULT_SPECS)
    with raises(TypeError):
        mutable_specs[(Language.eng, Language.zho_hans)] = DEFAULT_SPECS[
            (Language.yue_hans, Language.zho_hans)
        ]


def test_get_guided_transcriber_uses_registered_language_configuration(tmp_path):
    """Test factory configures language-specific prompts and Whisper language."""
    with (
        patch(
            "scinoephile.lang.transcription.guided.get_runtime_cache_dir_path",
            return_value=tmp_path,
        ),
        patch(
            "scinoephile.lang.transcription.guided.get_torch_device",
            return_value="test",
        ),
    ):
        transcriber = get_guided_transcriber(
            Language.yue_hant,
            Language.zho_hans,
            provider=Mock(spec=LLMProvider),
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
    test_case_dir_path = tmp_path / "lang/yue_zho/transcription"
    assert transcriber.aligner.delineation_json_path == (
        test_case_dir_path / "delineation" / "test.json"
    )
    assert transcriber.aligner.punctuation_json_path == (
        test_case_dir_path / "punctuation" / "test.json"
    )
    assert not transcriber.aligner.prune_delineation_test_cases
    assert not transcriber.aligner.prune_punctuation_test_cases


def test_get_guided_transcriber_prunes_stale_cases_when_requested(
    tmp_path: Path,
):
    """Test requested pruning retains only cases encountered by the current run."""
    delineation_json_path = tmp_path / "custom" / "delineation.json"
    punctuation_json_path = tmp_path / "other" / "punctuation.json"
    transcriber = get_guided_transcriber(
        Language.yue_hant,
        Language.zho_hans,
        provider=Mock(spec=LLMProvider),
        prune_test_cases=True,
        delineation_json_path=delineation_json_path,
        punctuation_json_path=punctuation_json_path,
        delineation_test_cases=[],
        punctuation_test_cases=[],
    )

    assert transcriber.aligner.delineation_json_path == delineation_json_path
    assert transcriber.aligner.punctuation_json_path == punctuation_json_path

    delineation_json_path.parent.mkdir(parents=True, exist_ok=True)
    delineation_json_path.write_text(
        json.dumps(
            [
                {
                    "query": {
                        "reference_one": "參考一",
                        "reference_two": "參考二",
                        "target_one": "目標一",
                        "target_two": "目標二",
                    },
                    "answer": {},
                }
            ]
        ),
        encoding="utf-8",
    )
    punctuation_json_path.parent.mkdir(parents=True, exist_ok=True)
    punctuation_json_path.write_text(
        json.dumps(
            [
                {
                    "query": {
                        "ref_sub": "參考",
                        "target_subs": ["目標"],
                    },
                    "answer": {"target_sub_punctuated": "目標。"},
                }
            ]
        ),
        encoding="utf-8",
    )

    transcriber.aligner.update_all_test_cases()

    assert json.loads(delineation_json_path.read_text(encoding="utf-8")) == []
    assert json.loads(punctuation_json_path.read_text(encoding="utf-8")) == []


def test_get_guided_transcriber_preserves_cases_in_default_json_paths(
    tmp_path: Path,
):
    """Test default JSON test cases are preserved between runs."""
    with (
        patch(
            "scinoephile.lang.transcription.guided.get_runtime_cache_dir_path",
            return_value=tmp_path,
        ),
        patch(
            "scinoephile.lang.transcription.guided.get_torch_device",
            return_value="test",
        ),
    ):
        transcriber = get_guided_transcriber(
            Language.yue_hant,
            Language.zho_hans,
            provider=Mock(spec=LLMProvider),
            delineation_test_cases=[],
            punctuation_test_cases=[],
        )
    test_case_dir_path = tmp_path / "lang/yue_zho/transcription"
    delineation_json_path = test_case_dir_path / "delineation" / "test.json"
    punctuation_json_path = test_case_dir_path / "punctuation" / "test.json"
    delineation_test_case_data = [
        {
            "query": {
                "ref_sub_1": "參考一",
                "ref_sub_2": "參考二",
                "target_sub_1": "目標一",
                "target_sub_2": "目標二",
            },
            "answer": {},
        }
    ]
    punctuation_test_case_data = [
        {
            "query": {
                "ref_sub": "參考",
                "target_subs": ["目標"],
            },
            "answer": {"target_sub_punctuated": "目標。"},
            "difficulty": 2,
        }
    ]
    delineation_json_path.write_text(
        json.dumps(delineation_test_case_data),
        encoding="utf-8",
    )
    punctuation_json_path.write_text(
        json.dumps(punctuation_test_case_data),
        encoding="utf-8",
    )

    transcriber.aligner.update_all_test_cases()

    assert json.loads(delineation_json_path.read_text(encoding="utf-8")) == (
        delineation_test_case_data
    )
    assert json.loads(punctuation_json_path.read_text(encoding="utf-8")) == (
        punctuation_test_case_data
    )


def test_get_guided_transcriber_loads_verified_cases_from_exact_json(tmp_path: Path):
    """Test an exact JSON's verified cases bypass the provider and few-shot prompt."""
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
    delineation_json_path = tmp_path / "delineation.json"
    save_test_cases_to_json(
        delineation_json_path,
        [verified_test_case],
        DelineationManager,
    )
    provider = Mock(spec=LLMProvider)
    transcriber = get_guided_transcriber(
        Language.yue_hant,
        Language.zho_hant,
        provider=provider,
        delineation_json_path=delineation_json_path,
        punctuation_json_path=tmp_path / "punctuation.json",
        punctuation_test_cases=[],
    )
    queryer = transcriber.aligner.delineation_queryer
    assert not transcriber.aligner.prune_delineation_test_cases
    assert not transcriber.aligner.prune_punctuation_test_cases
    pending_test_case = test_case_cls.model_validate(
        {"query": verified_test_case.query.model_dump()}
    )

    result = queryer(pending_test_case)

    assert result.answer == verified_test_case.answer
    assert result.verified is True
    assert result.few_shot is False
    assert verified_test_case.query.key not in queryer.few_shot_test_cases
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
