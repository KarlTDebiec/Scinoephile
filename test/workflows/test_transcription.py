#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for the aligned multi-source transcription workflow."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

from pydub import AudioSegment

from scinoephile.analysis.transcription_alignment import SubtitleTimingSettings
from scinoephile.audio.classification import AudioClassificationMode
from scinoephile.audio.diarization import DiarizationMode
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import DemucsMode, VADImplementation
from scinoephile.core import Language
from scinoephile.lang.transcription.pipeline import TranscriptionPipeline
from scinoephile.workflows.transcription import transcribe_series


def test_transcribe_series_constructs_aligned_pipeline(tmp_path: Path):
    """Workflow configuration should construct and invoke the production pipeline."""
    audio_series = AudioSeries(audio=AudioSegment.silent(duration=1_000), events=[])
    expected = AudioSeries(audio=audio_series.audio, events=[])
    pipeline = Mock(spec=TranscriptionPipeline)
    pipeline.process.return_value = expected
    provider = Mock()
    timing = SubtitleTimingSettings(lead_in_seconds=0.1)

    with patch(
        "scinoephile.workflows.transcription.get_transcription_pipeline",
        return_value=pipeline,
    ) as get_pipeline:
        output = transcribe_series(
            audio_series,
            language=Language.yue_hant,
            demucs_mode=DemucsMode.ON,
            diarization_mode=DiarizationMode.ON,
            vad_implementation=VADImplementation.TEN,
            block_vad_implementation=VADImplementation.SILERO,
            mlx_audio_token_limit_guard=False,
            cache_root_path=tmp_path / "cache",
            overwrite_cache=True,
            provider=provider,
            additional_context="人物名係阿明。",
            no_op=True,
            aligned_merge_json_path=tmp_path / "merge.json",
            prune_test_cases=True,
            timing_settings=timing,
            start_at_idx=1,
            stop_at_idx=3,
        )

    assert output is expected
    get_pipeline.assert_called_once_with(
        Language.yue_hant,
        audio_event_mode=AudioClassificationMode.AUTO,
        source_specs=None,
        demucs_mode=DemucsMode.ON,
        diarization_mode=DiarizationMode.ON,
        language_identification_mode=AudioClassificationMode.AUTO,
        vad_implementation=VADImplementation.TEN,
        block_vad_implementation=VADImplementation.SILERO,
        mlx_audio_token_limit_guard=False,
        cache_root_path=tmp_path / "cache",
        overwrite_cache=True,
        provider=provider,
        additional_context="人物名係阿明。",
        no_op=True,
        aligned_merge_json_path=tmp_path / "merge.json",
        prune_test_cases=True,
        aligned_merge_test_cases=None,
        timing_settings=timing,
    )
    pipeline.process.assert_called_once_with(
        audio_series, start_at_idx=1, stop_at_idx=3
    )


def test_transcribe_series_saves_injected_pipeline_artifact(tmp_path: Path):
    """An injected pipeline should save its portable artifact when requested."""
    audio_series = AudioSeries(audio=AudioSegment.silent(duration=1_000), events=[])
    expected = AudioSeries(audio=audio_series.audio, events=[])
    pipeline = Mock(spec=TranscriptionPipeline)
    pipeline.process.return_value = expected
    artifact = Mock()
    pipeline.last_alignment_artifact = artifact
    artifact_path = tmp_path / "alignment.json"

    output = transcribe_series(
        audio_series,
        language=Language.yue_hant,
        pipeline=pipeline,
        alignment_json_path=artifact_path,
    )

    assert output is expected
    pipeline.process.assert_called_once_with(
        audio_series, start_at_idx=0, stop_at_idx=None
    )
    artifact.save.assert_called_once_with(artifact_path)
