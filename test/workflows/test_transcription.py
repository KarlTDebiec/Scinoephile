#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for reference-guided transcription workflow."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

from pydub import AudioSegment

from scinoephile.audio.diarization import DiarizationMode
from scinoephile.audio.subtitles import AudioSeries, UnguidedDelineationSettings
from scinoephile.audio.transcription import DemucsMode, VADImplementation, VADMode
from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.transcriber import (
    BlockDelineationMode,
    BlockPunctuationMode,
    GuidedTranscriber,
    MlxAudioTimingMode,
    TranscriptionAlignmentMode,
    TranscriptionBackend,
)
from scinoephile.lang.transcription.unguided import UnguidedTranscriber
from scinoephile.workflows.transcription import (
    transcribe_series_guided,
    transcribe_series_unguided,
)


def test_transcribe_series_guided_constructs_transcriber_for_language_pair(
    tmp_path: Path,
):
    """Test workflow resolves construction and delegates processing."""
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
            backend=TranscriptionBackend.MLX_AUDIO,
            vad_implementation=VADImplementation.TEN,
            cache_root_path=tmp_path / "cache",
            overwrite_cache=True,
            strip_generated_punctuation=True,
            mlx_audio_timing_mode=MlxAudioTimingMode.PHRASE,
            mlx_audio_token_limit_guard=True,
            no_op=True,
            alignment_mode=TranscriptionAlignmentMode.BLOCK,
            block_delineation_mode=BlockDelineationMode.CANDIDATE,
            block_punctuation_mode=BlockPunctuationMode.FULL_TEXT,
            prune_test_cases=True,
            delineation_json_path=delineation_json_path,
            punctuation_json_path=punctuation_json_path,
            start_at_idx=1,
            stop_at_idx=2,
        )

    assert output is expected
    assert get_transcriber.call_args.args == (Language.yue_hant, Language.zho_hans)
    assert get_transcriber.call_args.kwargs["demucs_mode"] is DemucsMode.OFF
    assert get_transcriber.call_args.kwargs["vad_mode"] is VADMode.OFF
    assert get_transcriber.call_args.kwargs["diarization_mode"] is DiarizationMode.OFF
    assert get_transcriber.call_args.kwargs["vad_implementation"] is (
        VADImplementation.TEN
    )
    assert get_transcriber.call_args.kwargs["backend"] is (
        TranscriptionBackend.MLX_AUDIO
    )
    assert get_transcriber.call_args.kwargs["cache_root_path"] == tmp_path / "cache"
    assert get_transcriber.call_args.kwargs["overwrite_cache"] is True
    assert get_transcriber.call_args.kwargs["strip_generated_punctuation"] is True
    assert (
        get_transcriber.call_args.kwargs["mlx_audio_timing_mode"]
        is MlxAudioTimingMode.PHRASE
    )
    assert get_transcriber.call_args.kwargs["mlx_audio_token_limit_guard"] is True
    assert get_transcriber.call_args.kwargs["no_op"] is True
    assert (
        get_transcriber.call_args.kwargs["alignment_mode"]
        is TranscriptionAlignmentMode.BLOCK
    )
    assert (
        get_transcriber.call_args.kwargs["block_delineation_mode"]
        is BlockDelineationMode.CANDIDATE
    )
    assert (
        get_transcriber.call_args.kwargs["block_punctuation_mode"]
        is BlockPunctuationMode.FULL_TEXT
    )
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


def test_transcribe_series_unguided_constructs_transcriber_and_delegates(
    tmp_path: Path,
):
    """Test unguided workflow forwards configuration and delegates processing."""
    audio_series = Mock(spec=AudioSeries)
    expected = AudioSeries(audio=AudioSegment.silent(duration=1000))
    transcriber = Mock(spec=UnguidedTranscriber)
    transcriber.process.return_value = expected
    settings = UnguidedDelineationSettings(target_characters=7)

    with patch(
        "scinoephile.workflows.transcription.get_unguided_transcriber",
        return_value=transcriber,
    ) as get_transcriber:
        output = transcribe_series_unguided(
            audio_series,
            language=Language.yue_hant,
            model_name="custom/mlx-audio",
            backend=TranscriptionBackend.MLX_AUDIO,
            demucs_mode=DemucsMode.ON,
            vad_mode=VADMode.AUTO,
            diarization_mode=DiarizationMode.ON,
            vad_implementation=VADImplementation.TEN,
            mlx_audio_token_limit_guard=True,
            cache_root_path=tmp_path / "cache",
            overwrite_cache=True,
            delineation_settings=settings,
        )

    assert output is expected
    get_transcriber.assert_called_once_with(
        Language.yue_hant,
        multi_source=False,
        model_name="custom/mlx-audio",
        backend=TranscriptionBackend.MLX_AUDIO,
        demucs_mode=DemucsMode.ON,
        vad_mode=VADMode.AUTO,
        diarization_mode=DiarizationMode.ON,
        vad_implementation=VADImplementation.TEN,
        block_vad_implementation=VADImplementation.PYANNOTE,
        mlx_audio_token_limit_guard=True,
        cache_root_path=tmp_path / "cache",
        overwrite_cache=True,
        delineation_settings=settings,
        provider=None,
        additional_context=None,
        no_op=False,
    )
    transcriber.process.assert_called_once_with(
        audio_series, start_at_idx=0, stop_at_idx=None
    )


def test_transcribe_series_unguided_forwards_multi_source_configuration():
    """Test unguided workflow forwards reference-free consensus configuration."""
    audio_series = Mock(spec=AudioSeries)
    expected = AudioSeries(audio=AudioSegment.silent(duration=1000))
    transcriber = Mock(spec=UnguidedTranscriber)
    transcriber.process.return_value = expected
    provider = Mock()

    with patch(
        "scinoephile.workflows.transcription.get_unguided_transcriber",
        return_value=transcriber,
    ) as get_transcriber:
        output = transcribe_series_unguided(
            audio_series,
            language=Language.yue_hant,
            multi_source=True,
            provider=provider,
            additional_context="人物名係阿明。",
            no_op=True,
            start_at_idx=1,
            stop_at_idx=2,
        )

    assert output is expected
    assert get_transcriber.call_args.kwargs["multi_source"] is True
    assert get_transcriber.call_args.kwargs["provider"] is provider
    assert get_transcriber.call_args.kwargs["additional_context"] == "人物名係阿明。"
    assert get_transcriber.call_args.kwargs["no_op"] is True
    transcriber.process.assert_called_once_with(
        audio_series, start_at_idx=1, stop_at_idx=2
    )
