#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for reusable transcription workflows."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

from pydub import AudioSegment

from scinoephile.analysis.transcription import TimingSettings
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import DemucsMode, VadMode
from scinoephile.audio.vad import VadImplementation
from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.transcriber import (
    GuidedTranscriber,
    MlxAudioTimingMode,
    TranscriptionModel,
)
from scinoephile.workflows.transcription import (
    transcribe_series,
    transcribe_series_guided,
)
from scinoephile.workflows.transcription_pipeline import (
    AudioAnalysisMode,
    TranscriptionPipeline,
)


def test_transcribe_series_constructs_aligned_pipeline(tmp_path: Path):
    """Test workflow constructs and invokes the production pipeline.

    Arguments:
        tmp_path: temporary directory path
    """
    audio_series = AudioSeries(audio=AudioSegment.silent(duration=1_000), events=[])
    expected = AudioSeries(audio=audio_series.audio, events=[])
    pipeline = Mock(spec=TranscriptionPipeline)
    pipeline.process.return_value = expected
    provider = Mock()
    timing = TimingSettings(lead_in_seconds=0.1)
    json_path = tmp_path / "transcription.json"

    with patch(
        "scinoephile.workflows.transcription.get_transcription_pipeline",
        return_value=pipeline,
    ) as get_pipeline:
        output = transcribe_series(
            audio_series,
            language=Language.yue_hant,
            demucs_mode=DemucsMode.ON,
            diarization_mode=AudioAnalysisMode.ON,
            block_vad_implementation=VadImplementation.SILERO,
            cache_root_path=tmp_path / "cache",
            overwrite_cache=True,
            provider=provider,
            additional_context="人物名係阿明。",
            no_op=True,
            current_test_cases_path=json_path,
            prune_test_cases=True,
            shared_test_cases=[],
            timing_settings=timing,
            exclude_blocks=[2],
            start_at_idx=1,
            stop_at_idx=3,
        )

    assert output is expected
    get_pipeline.assert_called_once_with(
        Language.yue_hant,
        audio_event_mode=AudioAnalysisMode.AUTO,
        source_specs=None,
        demucs_mode=DemucsMode.ON,
        diarization_mode=AudioAnalysisMode.ON,
        language_identification_mode=AudioAnalysisMode.AUTO,
        block_vad_implementation=VadImplementation.SILERO,
        cache_root_path=tmp_path / "cache",
        overwrite_cache=True,
        provider=provider,
        additional_context="人物名係阿明。",
        no_op=True,
        current_test_cases_path=json_path,
        prune_test_cases=True,
        shared_test_cases=[],
        timing_settings=timing,
    )
    pipeline.process.assert_called_once_with(
        audio_series, exclude_blocks=[2], start_at_idx=1, stop_at_idx=3
    )


def test_transcribe_series_saves_pipeline_outputs(tmp_path: Path):
    """Test an injected pipeline saves requested alignment and run outputs.

    Arguments:
        tmp_path: temporary directory path
    """
    audio_series = AudioSeries(audio=AudioSegment.silent(duration=1_000), events=[])
    expected = AudioSeries(audio=audio_series.audio, events=[])
    pipeline = Mock(spec=TranscriptionPipeline)
    pipeline.process.return_value = expected
    artifact = Mock()
    manifest = Mock()
    pipeline.last_alignment_artifact = artifact
    pipeline.last_run_manifest = manifest
    artifact_path = tmp_path / "transcribe.alignment.json"
    manifest_path = tmp_path / "transcribe.run.json"

    output = transcribe_series(
        audio_series,
        language=Language.yue_hant,
        pipeline=pipeline,
        alignment_outfile_path=artifact_path,
        run_manifest_outfile_path=manifest_path,
    )

    assert output is expected
    pipeline.process.assert_called_once_with(
        audio_series, exclude_blocks=(), start_at_idx=0, stop_at_idx=None
    )
    artifact.save.assert_called_once_with(artifact_path)
    manifest.save.assert_called_once_with(manifest_path)


def test_transcribe_series_guided_constructs_transcriber_for_language_pair(
    tmp_path: Path,
):
    """Test guided workflow resolves construction and delegates processing.

    Arguments:
        tmp_path: temporary directory path
    """
    audio_series = Mock(spec=AudioSeries)
    reference_series = Series(events=[Subtitle(start=0, end=1000, text="你好")])
    expected = AudioSeries(audio=AudioSegment.silent(duration=1000))
    transcriber = Mock(spec=GuidedTranscriber)
    transcriber.process.return_value = expected
    delineation_json_path = tmp_path / "delineation.json"
    punctuation_json_path = tmp_path / "punctuation.json"

    with patch(
        "scinoephile.workflows.transcription.get_guided_transcriber",
        return_value=transcriber,
    ) as get_transcriber:
        output = transcribe_series_guided(
            audio_series,
            reference_series,
            language=Language.yue_hant,
            guide_language=Language.zho_hans,
            model=TranscriptionModel.MIMO,
            cache_root_path=tmp_path / "cache",
            overwrite_cache=True,
            strip_generated_punctuation=True,
            mlx_audio_timing_mode=MlxAudioTimingMode.PHRASE,
            mlx_audio_token_limit_guard=True,
            no_op=True,
            prune_test_cases=True,
            delineation_json_path=delineation_json_path,
            punctuation_json_path=punctuation_json_path,
            start_at_idx=1,
            stop_at_idx=2,
        )

    assert output is expected
    assert get_transcriber.call_args.args == (Language.yue_hant, Language.zho_hans)
    assert get_transcriber.call_args.kwargs["demucs_mode"] is DemucsMode.OFF
    assert get_transcriber.call_args.kwargs["vad_mode"] is VadMode.OFF
    assert get_transcriber.call_args.kwargs["model"] is TranscriptionModel.MIMO
    assert get_transcriber.call_args.kwargs["cache_root_path"] == tmp_path / "cache"
    assert get_transcriber.call_args.kwargs["overwrite_cache"] is True
    assert get_transcriber.call_args.kwargs["strip_generated_punctuation"] is True
    assert (
        get_transcriber.call_args.kwargs["mlx_audio_timing_mode"]
        is MlxAudioTimingMode.PHRASE
    )
    assert get_transcriber.call_args.kwargs["mlx_audio_token_limit_guard"] is True
    assert get_transcriber.call_args.kwargs["no_op"] is True
    assert get_transcriber.call_args.kwargs["prune_test_cases"] is True
    assert (
        get_transcriber.call_args.kwargs["delineation_json_path"]
        == delineation_json_path
    )
    assert (
        get_transcriber.call_args.kwargs["punctuation_json_path"]
        == punctuation_json_path
    )
    transcriber.process.assert_called_once_with(
        audio_series, reference_series, stop_at_idx=2, start_at_idx=1
    )
