#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for guided transcription configuration and construction."""

from __future__ import annotations

import json
from pathlib import Path
from typing import cast
from unittest.mock import Mock, patch

from pytest import raises

from scinoephile.audio.transcription import DemucsMode, VADMode
from scinoephile.audio.transcription.mlx_audio.backend import MIMO_MODEL_NAME
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms import LLMProvider
from scinoephile.core.llms.utils import save_test_cases_to_json
from scinoephile.lang.transcription.guided import DEFAULT_SPECS, get_guided_transcriber
from scinoephile.lang.transcription.transcriber import (
    MlxAudioTimingMode,
    TranscriptionBackend,
)
from scinoephile.lang.yue.prompts import YUE_HANT_PROMPT_FIELDS
from scinoephile.lang.yue_zho.transcription import (
    YueZhoDelineationPromptYueHant,
    YueZhoPunctuationPromptYueHant,
)
from scinoephile.llms.delineation import DelineationManager, DelineationProcessor
from scinoephile.llms.punctuation import PunctuationProcessor


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
            "scinoephile.lang.transcription.guided.get_runtime_data_root_path",
            return_value=tmp_path / "data",
        ),
        patch(
            "scinoephile.lang.transcription.guided.get_torch_device",
            return_value="test",
        ),
    ):
        transcriber = get_guided_transcriber(
            Language.yue_hant,
            Language.zho_hans,
            provider=Mock(
                spec=LLMProvider,
                cache_identity={"implementation": "test"},
                completion_metrics=[],
            ),
            delineation_test_cases=[],
            punctuation_test_cases=[],
            cache_root_path=tmp_path,
            overwrite_cache=True,
        )

    assert transcriber.language is Language.yue_hant
    assert transcriber.guide_language is Language.zho_hans
    assert transcriber.backend is TranscriptionBackend.WHISPER
    assert transcriber.demucs_mode is DemucsMode.OFF
    assert transcriber.vad_mode is VADMode.OFF
    assert not hasattr(transcriber, "overwrite_cache")
    assert not hasattr(transcriber, "cache_root_path")
    assert transcriber.whisper_language == "yue"
    assert transcriber.segment_splitter is not None
    assert isinstance(transcriber.aligner.delineation_processor, DelineationProcessor)
    assert isinstance(transcriber.aligner.punctuation_processor, PunctuationProcessor)
    assert transcriber.aligner.delineation_processor.prompt is (
        YueZhoDelineationPromptYueHant
    )
    assert transcriber.aligner.punctuation_processor.prompt is (
        YueZhoPunctuationPromptYueHant
    )
    assert transcriber.transcriber.language == "yue"
    assert transcriber.transcriber.demucs_mode is DemucsMode.OFF
    assert transcriber.transcriber.vad_mode is VADMode.OFF
    assert transcriber.recovery_transcriber is not None
    assert transcriber.tail_recovery_transcriber is not None
    assert not hasattr(transcriber.transcriber, "cache_root_path")
    assert transcriber.transcriber._cache.cache_dir_path == tmp_path / "whisper"
    assert transcriber.recovery_transcriber._cache.cache_dir_path == (
        tmp_path / "whisper"
    )
    assert transcriber.tail_recovery_transcriber._cache.cache_dir_path == (
        tmp_path / "whisper"
    )
    assert transcriber.transcriber._cache.overwrite
    assert transcriber.recovery_transcriber._cache.overwrite
    assert transcriber.tail_recovery_transcriber._cache.overwrite
    assert transcriber.transcriber.demucs_separator is None
    assert transcriber.recovery_transcriber.demucs_separator is None
    test_case_dir_path = tmp_path / "data/test_cases/lang/yue_zho/transcription"
    assert transcriber.aligner.delineation_processor.current_test_cases_path == (
        test_case_dir_path / "delineation" / "test.json"
    )
    assert transcriber.aligner.punctuation_processor.current_test_cases_path == (
        test_case_dir_path / "punctuation" / "test.json"
    )
    assert not transcriber.aligner.delineation_processor.prune_test_cases
    assert not transcriber.aligner.punctuation_processor.prune_test_cases
    delineation_cache = transcriber.aligner.delineation_processor.queryer._cache
    assert delineation_cache is not None
    assert delineation_cache.cache_dir_path == tmp_path / "llm" / "delineation"
    assert delineation_cache.overwrite
    punctuation_cache = transcriber.aligner.punctuation_processor.queryer._cache
    assert punctuation_cache is not None
    assert punctuation_cache.cache_dir_path == tmp_path / "llm" / "punctuation"
    assert punctuation_cache.overwrite


def test_get_guided_transcriber_configures_mlx_audio_backend(tmp_path: Path):
    """Test the factory selects the MLX-Audio default and preprocessing modes.

    Arguments:
        tmp_path: temporary directory path
    """
    mlx_audio_transcriber = Mock()
    with patch(
        "scinoephile.lang.transcription.guided.MlxAudioTranscriber",
        return_value=mlx_audio_transcriber,
    ) as mlx_audio_transcriber_class:
        transcriber = get_guided_transcriber(
            Language.yue_hant,
            Language.zho_hans,
            backend=TranscriptionBackend.MLX_AUDIO,
            cache_root_path=tmp_path,
            strip_generated_punctuation=True,
            mlx_audio_timing_mode=MlxAudioTimingMode.PHRASE,
            provider=Mock(
                spec=LLMProvider,
                cache_identity={"implementation": "test"},
                completion_metrics=[],
            ),
            delineation_json_path=tmp_path / "delineation.json",
            punctuation_json_path=tmp_path / "punctuation.json",
            delineation_test_cases=[],
            punctuation_test_cases=[],
        )

    assert transcriber.backend is TranscriptionBackend.MLX_AUDIO
    assert transcriber.model_name == MIMO_MODEL_NAME
    assert transcriber.transcriber is mlx_audio_transcriber
    assert transcriber.recovery_transcriber is None
    assert transcriber.tail_recovery_transcriber is None
    assert transcriber.strip_generated_punctuation
    assert transcriber.mlx_audio_timing_mode is MlxAudioTimingMode.PHRASE
    mlx_audio_transcriber_class.assert_called_once_with(
        model_name=MIMO_MODEL_NAME,
        language=Language.yue_hant,
        demucs_mode=DemucsMode.OFF,
        vad_mode=VADMode.OFF,
        cache_root_path=tmp_path,
        overwrite_cache=False,
    )


def test_get_guided_transcriber_prunes_stale_cases_when_requested(tmp_path: Path):
    """Test requested pruning retains only cases encountered by the current run."""
    delineation_json_path = tmp_path / "custom" / "delineation.json"
    punctuation_json_path = tmp_path / "other" / "punctuation.json"
    transcriber = get_guided_transcriber(
        Language.yue_hant,
        Language.zho_hans,
        provider=Mock(
            spec=LLMProvider,
            cache_identity={"implementation": "test"},
            completion_metrics=[],
        ),
        prune_test_cases=True,
        delineation_json_path=delineation_json_path,
        punctuation_json_path=punctuation_json_path,
        delineation_test_cases=[],
        punctuation_test_cases=[],
    )

    assert transcriber.aligner.delineation_processor.current_test_cases_path == (
        delineation_json_path
    )
    assert transcriber.aligner.punctuation_processor.current_test_cases_path == (
        punctuation_json_path
    )

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
                    "query": {"ref_sub": "參考", "target_subs": ["目標"]},
                    "answer": {"target_sub_punctuated": "目標。"},
                }
            ]
        ),
        encoding="utf-8",
    )

    transcriber.aligner.update_all_test_cases()

    assert json.loads(delineation_json_path.read_text(encoding="utf-8")) == []
    assert json.loads(punctuation_json_path.read_text(encoding="utf-8")) == []


def test_get_guided_transcriber_preserves_cases_in_default_json_paths(tmp_path: Path):
    """Test default JSON test cases are preserved between runs."""
    with (
        patch(
            "scinoephile.lang.transcription.guided.get_runtime_data_root_path",
            return_value=tmp_path / "data",
        ),
        patch(
            "scinoephile.lang.transcription.guided.get_torch_device",
            return_value="test",
        ),
    ):
        transcriber = get_guided_transcriber(
            Language.yue_hant,
            Language.zho_hans,
            provider=Mock(
                spec=LLMProvider,
                cache_identity={"implementation": "test"},
                completion_metrics=[],
            ),
            delineation_test_cases=[],
            punctuation_test_cases=[],
            cache_root_path=tmp_path,
        )
    test_case_dir_path = tmp_path / "data/test_cases/lang/yue_zho/transcription"
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
            "query": {"ref_sub": "參考", "target_subs": ["目標"]},
            "answer": {"target_sub_punctuated": "目標。"},
            "difficulty": 2,
        }
    ]
    delineation_json_path.write_text(
        json.dumps(delineation_test_case_data), encoding="utf-8"
    )
    punctuation_json_path.write_text(
        json.dumps(punctuation_test_case_data), encoding="utf-8"
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
        delineation_json_path, [verified_test_case], DelineationManager
    )
    provider = Mock(
        spec=LLMProvider,
        cache_identity={"implementation": "test"},
        completion_metrics=[],
    )
    transcriber = get_guided_transcriber(
        Language.yue_hant,
        Language.zho_hant,
        provider=provider,
        delineation_json_path=delineation_json_path,
        punctuation_json_path=tmp_path / "punctuation.json",
        punctuation_test_cases=[],
    )
    queryer = transcriber.aligner.delineation_processor.queryer
    assert not transcriber.aligner.delineation_processor.prune_test_cases
    assert not transcriber.aligner.punctuation_processor.prune_test_cases
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
    for prompt in (YueZhoDelineationPromptYueHant, YueZhoPunctuationPromptYueHant):
        for field_name, expected in YUE_HANT_PROMPT_FIELDS.items():
            assert getattr(prompt, field_name) == expected
