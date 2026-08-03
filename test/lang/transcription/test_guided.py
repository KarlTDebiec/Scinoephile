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
from scinoephile.lang.transcription.block_aligner import BlockTranscriptionAligner
from scinoephile.lang.transcription.guided import DEFAULT_SPECS, get_guided_transcriber
from scinoephile.lang.transcription.transcriber import (
    BlockDelineationMode,
    BlockPunctuationMode,
    MlxAudioTimingMode,
    TranscriptionAlignmentMode,
    TranscriptionBackend,
)
from scinoephile.lang.yue.prompts import YUE_HANT_PROMPT_FIELDS
from scinoephile.lang.yue_zho.transcription import (
    YueZhoAdvisoryBlockDelineationPromptYueHant,
    YueZhoBlockDelineationPromptYueHant,
    YueZhoBlockPunctuationPromptYueHant,
    YueZhoCandidateBlockDelineationPromptYueHant,
    YueZhoDelineationPromptYueHant,
    YueZhoPositionalBlockPunctuationPromptYueHant,
    YueZhoPunctuationPromptYueHant,
)
from scinoephile.llms.block_delineation import (
    AdvisoryBlockDelineationProcessor,
    BlockDelineationProcessor,
    CandidateBlockDelineationProcessor,
)
from scinoephile.llms.block_punctuation import (
    BlockPunctuationProcessor,
    PositionalBlockPunctuationProcessor,
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
    expected_block_json_dir_paths = (
        tuple(
            Path(dataset_name)
            / "output"
            / "yue-Hant_transcribe"
            / vad_name
            / transcription_name
            / "json"
            for dataset_name in ("acopopb", "acoptc", "kob", "tmm")
            for vad_name in ("vad-auto", "vad-off")
            for transcription_name in ("whisper", "mimo", "qwen")
        )
        + tuple(
            Path("acopopb")
            / "output"
            / "yue-Hant_transcribe"
            / "vad-off-stripped-punctuation"
            / transcription_name
            / "json"
            for transcription_name in ("mimo", "qwen")
        )
        + tuple(
            Path("acopopb")
            / "output"
            / "yue-Hant_transcribe"
            / "vad-off-phrase-timing-stripped-punctuation"
            / transcription_name
            / "json"
            for transcription_name in ("mimo", "qwen")
        )
    )
    spec = DEFAULT_SPECS[(Language.yue_hant, Language.zho_hant)]
    assert spec.block_delineation_json_paths == tuple(
        dir_path / "block_delineation-mps.json"
        for dir_path in expected_block_json_dir_paths
    )
    assert spec.block_punctuation_json_paths == tuple(
        dir_path / "block_punctuation-mps.json"
        for dir_path in expected_block_json_dir_paths
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
            provider=Mock(spec=LLMProvider, cache_identity={"implementation": "test"}),
            delineation_test_cases=[],
            punctuation_test_cases=[],
            cache_root_path=tmp_path,
            overwrite_cache=True,
        )

    assert transcriber.language is Language.yue_hant
    assert transcriber.guide_language is Language.zho_hans
    assert transcriber.backend is TranscriptionBackend.WHISPER
    assert transcriber.demucs_mode is DemucsMode.AUTO
    assert transcriber.vad_mode is VADMode.AUTO
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
    assert transcriber.transcriber.demucs_mode is DemucsMode.AUTO
    assert transcriber.transcriber.vad_mode is VADMode.AUTO
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
    assert transcriber.transcriber.demucs_separator is not None
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
            provider=Mock(spec=LLMProvider, cache_identity={"implementation": "test"}),
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
        demucs_mode=DemucsMode.AUTO,
        vad_mode=VADMode.AUTO,
        cache_root_path=tmp_path,
        overwrite_cache=False,
    )


def test_get_guided_transcriber_configures_block_alignment(tmp_path: Path):
    """Test block mode uses independent prompts, paths, and fallback configuration.

    Arguments:
        tmp_path: temporary directory path
    """
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
            Language.zho_hant,
            alignment_mode=TranscriptionAlignmentMode.BLOCK,
            fallback_to_no_op=True,
            provider=Mock(spec=LLMProvider, cache_identity={"implementation": "test"}),
            block_delineation_test_cases=[],
            block_punctuation_test_cases=[],
            cache_root_path=tmp_path,
        )

    assert isinstance(transcriber.aligner, BlockTranscriptionAligner)
    assert isinstance(
        transcriber.aligner.delineation_processor, BlockDelineationProcessor
    )
    assert isinstance(
        transcriber.aligner.punctuation_processor, BlockPunctuationProcessor
    )
    assert transcriber.aligner.delineation_processor.prompt is (
        YueZhoBlockDelineationPromptYueHant
    )
    assert transcriber.aligner.punctuation_processor.prompt is (
        YueZhoBlockPunctuationPromptYueHant
    )
    assert transcriber.aligner.fallback_to_no_op
    test_case_dir_path = tmp_path / "data/test_cases/lang/yue_zho/transcription"
    assert transcriber.aligner.delineation_processor.current_test_cases_path == (
        test_case_dir_path / "block_delineation" / "test.json"
    )
    assert transcriber.aligner.punctuation_processor.current_test_cases_path == (
        test_case_dir_path / "block_punctuation" / "test.json"
    )


def test_get_guided_transcriber_configures_block_positional_alignment(tmp_path: Path):
    """Test positional mode uses distinct schemas, paths, and punctuation cleanup."""
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
            Language.zho_hant,
            alignment_mode=TranscriptionAlignmentMode.BLOCK_POSITIONAL,
            provider=Mock(spec=LLMProvider, cache_identity={"implementation": "test"}),
            block_delineation_test_cases=[],
            block_punctuation_test_cases=[],
            cache_root_path=tmp_path,
        )

    assert isinstance(transcriber.aligner, BlockTranscriptionAligner)
    assert isinstance(
        transcriber.aligner.delineation_processor, CandidateBlockDelineationProcessor
    )
    assert isinstance(
        transcriber.aligner.punctuation_processor, PositionalBlockPunctuationProcessor
    )
    assert transcriber.aligner.delineation_processor.prompt is (
        YueZhoCandidateBlockDelineationPromptYueHant
    )
    assert transcriber.aligner.punctuation_processor.prompt is (
        YueZhoPositionalBlockPunctuationPromptYueHant
    )
    assert transcriber.aligner.use_delineation_candidates
    assert transcriber.strip_generated_punctuation
    test_case_dir_path = tmp_path / "data/test_cases/lang/yue_zho/transcription"
    assert transcriber.aligner.delineation_processor.current_test_cases_path == (
        test_case_dir_path / "candidate_block_delineation" / "test.json"
    )
    assert transcriber.aligner.punctuation_processor.current_test_cases_path == (
        test_case_dir_path / "positional_block_punctuation" / "test.json"
    )


def test_get_guided_transcriber_configures_candidate_delineation_only(tmp_path: Path):
    """Test candidate delineation can use the existing punctuation strategy.

    Arguments:
        tmp_path: temporary directory path
    """
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
            Language.zho_hant,
            alignment_mode=TranscriptionAlignmentMode.BLOCK,
            block_delineation_mode=BlockDelineationMode.CANDIDATE,
            provider=Mock(spec=LLMProvider, cache_identity={"implementation": "test"}),
            block_delineation_test_cases=[],
            block_punctuation_test_cases=[],
            cache_root_path=tmp_path,
        )

    assert isinstance(transcriber.aligner, BlockTranscriptionAligner)
    assert isinstance(
        transcriber.aligner.delineation_processor, CandidateBlockDelineationProcessor
    )
    assert isinstance(
        transcriber.aligner.punctuation_processor, BlockPunctuationProcessor
    )
    assert transcriber.aligner.use_delineation_candidates
    assert not transcriber.strip_generated_punctuation
    test_case_dir_path = tmp_path / "data/test_cases/lang/yue_zho/transcription"
    assert transcriber.aligner.delineation_processor.current_test_cases_path == (
        test_case_dir_path / "candidate_block_delineation" / "test.json"
    )
    assert transcriber.aligner.punctuation_processor.current_test_cases_path == (
        test_case_dir_path / "block_punctuation" / "test.json"
    )


def test_get_guided_transcriber_configures_advisory_delineation_only(tmp_path: Path):
    """Test advisory delineation can use the existing punctuation strategy.

    Arguments:
        tmp_path: temporary directory path
    """
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
            Language.zho_hant,
            alignment_mode=TranscriptionAlignmentMode.BLOCK,
            block_delineation_mode=BlockDelineationMode.ADVISORY,
            provider=Mock(spec=LLMProvider, cache_identity={"implementation": "test"}),
            block_delineation_test_cases=[],
            block_punctuation_test_cases=[],
            cache_root_path=tmp_path,
        )

    assert isinstance(transcriber.aligner, BlockTranscriptionAligner)
    assert isinstance(
        transcriber.aligner.delineation_processor, AdvisoryBlockDelineationProcessor
    )
    assert isinstance(
        transcriber.aligner.punctuation_processor, BlockPunctuationProcessor
    )
    assert transcriber.aligner.delineation_processor.prompt is (
        YueZhoAdvisoryBlockDelineationPromptYueHant
    )
    assert transcriber.aligner.use_delineation_suggestions
    assert not transcriber.aligner.use_delineation_candidates
    assert not transcriber.strip_generated_punctuation
    test_case_dir_path = tmp_path / "data/test_cases/lang/yue_zho/transcription"
    assert transcriber.aligner.delineation_processor.current_test_cases_path == (
        test_case_dir_path / "advisory_block_delineation" / "test.json"
    )
    assert transcriber.aligner.punctuation_processor.current_test_cases_path == (
        test_case_dir_path / "block_punctuation" / "test.json"
    )


def test_get_guided_transcriber_configures_gated_advisory_delineation(tmp_path: Path):
    """Test gated advisory delineation omits weak timing suggestions.

    Arguments:
        tmp_path: temporary directory path
    """
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
            Language.zho_hant,
            alignment_mode=TranscriptionAlignmentMode.BLOCK,
            block_delineation_mode=BlockDelineationMode.GATED_ADVISORY,
            provider=Mock(spec=LLMProvider, cache_identity={"implementation": "test"}),
            block_delineation_test_cases=[],
            block_punctuation_test_cases=[],
            cache_root_path=tmp_path,
        )

    assert isinstance(transcriber.aligner, BlockTranscriptionAligner)
    assert isinstance(
        transcriber.aligner.delineation_processor, AdvisoryBlockDelineationProcessor
    )
    assert transcriber.aligner.use_delineation_suggestions
    assert transcriber.aligner.gate_delineation_suggestions
    assert not transcriber.aligner.use_delineation_candidates
    test_case_dir_path = tmp_path / "data/test_cases/lang/yue_zho/transcription"
    assert transcriber.aligner.delineation_processor.current_test_cases_path == (
        test_case_dir_path / "gated_advisory_block_delineation" / "test.json"
    )


def test_get_guided_transcriber_configures_positional_punctuation_only(tmp_path: Path):
    """Test positional punctuation can use unrestricted delineation.

    Arguments:
        tmp_path: temporary directory path
    """
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
            Language.zho_hant,
            alignment_mode=TranscriptionAlignmentMode.BLOCK,
            block_punctuation_mode=BlockPunctuationMode.POSITIONAL,
            provider=Mock(spec=LLMProvider, cache_identity={"implementation": "test"}),
            block_delineation_test_cases=[],
            block_punctuation_test_cases=[],
            cache_root_path=tmp_path,
        )

    assert isinstance(transcriber.aligner, BlockTranscriptionAligner)
    assert isinstance(
        transcriber.aligner.delineation_processor, BlockDelineationProcessor
    )
    assert isinstance(
        transcriber.aligner.punctuation_processor, PositionalBlockPunctuationProcessor
    )
    assert not transcriber.aligner.use_delineation_candidates
    assert transcriber.strip_generated_punctuation
    test_case_dir_path = tmp_path / "data/test_cases/lang/yue_zho/transcription"
    assert transcriber.aligner.delineation_processor.current_test_cases_path == (
        test_case_dir_path / "block_delineation" / "test.json"
    )
    assert transcriber.aligner.punctuation_processor.current_test_cases_path == (
        test_case_dir_path / "positional_block_punctuation" / "test.json"
    )


def test_get_guided_transcriber_rejects_pairwise_fallback():
    """Test sparse no-op fallback cannot be enabled for legacy pairwise mode."""
    with raises(ValueError, match="only with block alignment"):
        get_guided_transcriber(
            Language.yue_hant,
            Language.zho_hant,
            fallback_to_no_op=True,
            provider=Mock(spec=LLMProvider, cache_identity={"implementation": "test"}),
        )


def test_get_guided_transcriber_rejects_block_strategy_in_pairwise_mode():
    """Test block strategy overrides cannot be used in pairwise mode."""
    with raises(ValueError, match="require a block alignment mode"):
        get_guided_transcriber(
            Language.yue_hant,
            Language.zho_hant,
            block_delineation_mode=BlockDelineationMode.CANDIDATE,
            provider=Mock(spec=LLMProvider, cache_identity={"implementation": "test"}),
        )


def test_get_guided_transcriber_prunes_stale_cases_when_requested(tmp_path: Path):
    """Test requested pruning retains only cases encountered by the current run."""
    delineation_json_path = tmp_path / "custom" / "delineation.json"
    punctuation_json_path = tmp_path / "other" / "punctuation.json"
    transcriber = get_guided_transcriber(
        Language.yue_hant,
        Language.zho_hans,
        provider=Mock(spec=LLMProvider, cache_identity={"implementation": "test"}),
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
            provider=Mock(spec=LLMProvider, cache_identity={"implementation": "test"}),
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
    provider = Mock(spec=LLMProvider, cache_identity={"implementation": "test"})
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
    for prompt in (
        YueZhoBlockDelineationPromptYueHant,
        YueZhoBlockPunctuationPromptYueHant,
        YueZhoDelineationPromptYueHant,
        YueZhoPunctuationPromptYueHant,
    ):
        for field_name, expected in YUE_HANT_PROMPT_FIELDS.items():
            assert getattr(prompt, field_name) == expected
