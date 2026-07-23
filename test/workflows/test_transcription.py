#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for reference-guided transcription workflow."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

from pydub import AudioSegment

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import MimoRuntime
from scinoephile.core import Language
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.lang.transcription.transcriber import (
    DemucsMode,
    GuidedTranscriber,
    VADMode,
)
from scinoephile.workflows.transcription import transcribe_series_guided


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
            reference_language=Language.zho_hans,
            prune_test_cases=True,
            delineation_json_path=delineation_json_path,
            punctuation_json_path=punctuation_json_path,
            mimo_fallback=True,
            mimo_model_name="custom/mimo",
            mimo_tokenizer_name="custom/tokenizer",
            mimo_runtime=MimoRuntime.MLX,
            mimo_language="auto",
            mimo_max_tokens=512,
            mimo_chunk_duration_seconds=20.0,
            mimo_chunk_overlap_seconds=1.5,
            mimo_worker_command=("python", "mimo_worker.py"),
            mimo_aligner_backend="whisperx",
            mimo_aligner_language="zh",
            mimo_aligner_model_name="custom/aligner",
            mimo_aligner_worker_command=("python", "aligner_worker.py"),
            start_at_idx=1,
            stop_at_idx=2,
        )

    assert output is expected
    assert get_transcriber.call_args.args == (
        Language.yue_hant,
        Language.zho_hans,
    )
    assert get_transcriber.call_args.kwargs["demucs_mode"] is DemucsMode.AUTO
    assert get_transcriber.call_args.kwargs["vad_mode"] is VADMode.AUTO
    assert get_transcriber.call_args.kwargs["mimo_fallback"] is True
    assert get_transcriber.call_args.kwargs["mimo_model_name"] == "custom/mimo"
    assert get_transcriber.call_args.kwargs["mimo_tokenizer_name"] == (
        "custom/tokenizer"
    )
    assert get_transcriber.call_args.kwargs["mimo_runtime"] is MimoRuntime.MLX
    assert get_transcriber.call_args.kwargs["mimo_language"] == "auto"
    assert get_transcriber.call_args.kwargs["mimo_max_tokens"] == 512
    assert get_transcriber.call_args.kwargs["mimo_chunk_duration_seconds"] == 20.0
    assert get_transcriber.call_args.kwargs["mimo_chunk_overlap_seconds"] == 1.5
    assert get_transcriber.call_args.kwargs["mimo_worker_command"] == (
        "python",
        "mimo_worker.py",
    )
    assert get_transcriber.call_args.kwargs["mimo_aligner_backend"] == "whisperx"
    assert get_transcriber.call_args.kwargs["mimo_aligner_language"] == "zh"
    assert get_transcriber.call_args.kwargs["mimo_aligner_model_name"] == (
        "custom/aligner"
    )
    assert get_transcriber.call_args.kwargs["mimo_aligner_worker_command"] == (
        "python",
        "aligner_worker.py",
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
        audio_series,
        reference_series,
        stop_at_idx=2,
        start_at_idx=1,
    )
