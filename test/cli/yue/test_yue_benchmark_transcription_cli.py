#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.yue.yue_benchmark_transcription_cli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from pydub import AudioSegment

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.cli.yue.yue_benchmark_transcription_cli import (
    YueBenchmarkTranscriptionCli,
)
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from scinoephile.multilang.yue_zho.transcription import (
    MimoRuntime,
    TranscriptionBackend,
)


def test_yue_benchmark_transcription_cli_reuses_existing_candidate(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Test benchmark CLI computes CER from an existing candidate output."""
    audio_dir_path = tmp_path / "audio"
    audio_dir_path.mkdir()
    zho_infile_path = _write_series(tmp_path / "zho.srt", "abc")
    reference_infile_path = _write_series(tmp_path / "reference.srt", "abc")
    candidate_outfile_path = _write_series(tmp_path / "candidate.srt", "axc")
    cer_outfile_path = tmp_path / "candidate.cer.txt"

    with patch(
        "scinoephile.cli.yue.yue_benchmark_transcription_cli.AudioSeries.load"
    ) as patched_audio_load:
        with patch(
            "scinoephile.cli.yue.yue_benchmark_transcription_cli.get_yue_vs_zho_transcriber"
        ) as patched_factory:
            run_cli_with_args(
                YueBenchmarkTranscriptionCli,
                f"--audio-series-indir {audio_dir_path} "
                f"--zho-infile {zho_infile_path} "
                f"--reference-infile {reference_infile_path} "
                f"--candidate-outfile {candidate_outfile_path} "
                f"--cer-outfile {cer_outfile_path}",
            )

    output = capsys.readouterr().out
    assert "CER: 0.3333333333333333" in output
    assert "Substitutions: 1" in output
    assert "CER: 0.3333333333333333" in cer_outfile_path.read_text(encoding="utf-8")
    patched_audio_load.assert_not_called()
    patched_factory.assert_not_called()


def test_yue_benchmark_transcription_cli_limits_reference_for_stopped_run(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Test stopped benchmark CLI limits reference CER blocks."""
    audio_dir_path = tmp_path / "audio"
    audio_dir_path.mkdir()
    zho_infile_path = _write_series(tmp_path / "zho.srt", "abc")
    reference_infile_path = _write_multiblock_series(
        tmp_path / "reference.srt",
        ("abc", "def", "ghi"),
    )
    candidate_outfile_path = _write_multiblock_series(
        tmp_path / "candidate.srt",
        ("abc", "def"),
    )

    with patch(
        "scinoephile.cli.yue.yue_benchmark_transcription_cli.AudioSeries.load"
    ) as patched_audio_load:
        with patch(
            "scinoephile.cli.yue.yue_benchmark_transcription_cli.get_yue_vs_zho_transcriber"
        ) as patched_factory:
            run_cli_with_args(
                YueBenchmarkTranscriptionCli,
                f"--audio-series-indir {audio_dir_path} "
                f"--zho-infile {zho_infile_path} "
                f"--reference-infile {reference_infile_path} "
                f"--candidate-outfile {candidate_outfile_path} "
                "--stop-at-idx 1",
            )

    output = capsys.readouterr().out
    assert "CER: 0.0" in output
    assert "Reference length: 6" in output
    patched_audio_load.assert_not_called()
    patched_factory.assert_not_called()


def test_yue_benchmark_transcription_cli_limits_cer_by_audio_time_window(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Test benchmark CLI can limit CER by processed audio time."""
    audio_dir_path = tmp_path / "audio"
    audio_dir_path.mkdir()
    zho_infile_path = _write_series(tmp_path / "zho.srt", "abc")
    reference_infile_path = _write_multiblock_series(
        tmp_path / "reference.srt",
        ("abc", "def"),
    )
    candidate_outfile_path = _write_series(tmp_path / "candidate.srt", "abc")
    audio_block = Mock()
    audio_block.buffered_start = 0
    audio_block.buffered_end = 1500
    audio_series = Mock()
    audio_series.blocks = [audio_block]

    with patch(
        "scinoephile.cli.yue.yue_benchmark_transcription_cli.AudioSeries.load",
        return_value=audio_series,
    ) as patched_audio_load:
        with patch(
            "scinoephile.cli.yue.yue_benchmark_transcription_cli.get_yue_vs_zho_transcriber"
        ) as patched_factory:
            run_cli_with_args(
                YueBenchmarkTranscriptionCli,
                f"--audio-series-indir {audio_dir_path} "
                f"--zho-infile {zho_infile_path} "
                f"--reference-infile {reference_infile_path} "
                f"--candidate-outfile {candidate_outfile_path} "
                "--stop-at-idx 0 "
                "--cer-window time",
            )

    output = capsys.readouterr().out
    assert "CER: 0.0" in output
    assert "Reference length: 3" in output
    patched_audio_load.assert_called_once_with(audio_dir_path)
    patched_factory.assert_not_called()


def test_yue_benchmark_transcription_cli_transcribes_missing_candidate(
    tmp_path: Path,
):
    """Test benchmark CLI transcribes, writes candidate output, and computes CER."""
    audio_dir_path = tmp_path / "audio"
    audio_dir_path.mkdir()
    zho_infile_path = _write_series(tmp_path / "zho.srt", "你好")
    reference_infile_path = _write_series(tmp_path / "reference.srt", "你好")
    candidate_outfile_path = tmp_path / "candidate.srt"
    expected_series = Series.from_string(
        "1\n00:00:00,000 --> 00:00:01,000\n你好\n",
        format_="srt",
    )
    expected_candidate = AudioSeries(
        audio=AudioSegment.silent(duration=1000),
        events=[
            AudioSeries.event_class(**event.as_dict()) for event in expected_series
        ],
    )
    audio_series = Mock()

    with patch(
        "scinoephile.cli.yue.yue_benchmark_transcription_cli.AudioSeries.load",
        return_value=audio_series,
    ) as patched_audio_load:
        with patch(
            "scinoephile.cli.yue.yue_benchmark_transcription_cli.get_yue_vs_zho_transcriber",
            return_value="transcriber",
        ) as patched_factory:
            with patch(
                "scinoephile.cli.yue.yue_benchmark_transcription_cli.get_yue_transcribed_vs_zho",
                return_value=expected_candidate,
            ) as patched_transcribe:
                run_cli_with_args(
                    YueBenchmarkTranscriptionCli,
                    f"--audio-series-indir {audio_dir_path} "
                    f"--zho-infile {zho_infile_path} "
                    f"--reference-infile {reference_infile_path} "
                    f"--candidate-outfile {candidate_outfile_path} "
                    "--asr-backend mimo "
                    "--mimo-runtime mlx "
                    "--mimo-language auto "
                    "--mimo-max-tokens 1024 "
                    "--mimo-chunk-duration 20 "
                    "--mimo-chunk-overlap 1.5 "
                    "--mimo-aligner ctc "
                    "--stop-at-idx 0 "
                    '--mimo-worker-command "python worker.py"',
                )

    patched_audio_load.assert_called_once_with(audio_dir_path)
    assert patched_factory.call_args.kwargs["backend"] == TranscriptionBackend.MIMO
    assert patched_factory.call_args.kwargs["mimo_runtime"] == MimoRuntime.MLX
    assert patched_factory.call_args.kwargs["mimo_language"] == "auto"
    assert patched_factory.call_args.kwargs["mimo_max_tokens"] == 1024
    assert patched_factory.call_args.kwargs["mimo_chunk_duration_seconds"] == 20.0
    assert patched_factory.call_args.kwargs["mimo_chunk_overlap_seconds"] == 1.5
    assert patched_factory.call_args.kwargs["mimo_aligner_backend"] == "ctc"
    assert patched_factory.call_args.kwargs["mimo_worker_command"] == [
        "python",
        "worker.py",
    ]
    assert patched_transcribe.call_args.kwargs["yuewen"] == audio_series
    assert patched_transcribe.call_args.kwargs["transcriber"] == "transcriber"
    assert patched_transcribe.call_args.kwargs["stop_at_idx"] == 0
    assert Series.load(candidate_outfile_path)[0].text == "你好"


def _write_series(path: Path, text: str) -> Path:
    """Write a one-line SRT file.

    Arguments:
        path: path to write
        text: subtitle text
    Returns:
        written path
    """
    path.write_text(
        f"1\n00:00:00,000 --> 00:00:01,000\n{text}\n",
        encoding="utf-8",
    )
    return path


def _write_multiblock_series(path: Path, texts: tuple[str, ...]) -> Path:
    """Write an SRT file with one subtitle per block.

    Arguments:
        path: path to write
        texts: subtitle texts, one per block
    Returns:
        written path
    """
    blocks = []
    for idx, text in enumerate(texts, 1):
        start = (idx - 1) * 5000
        end = start + 1000
        blocks.append(
            f"{idx}\n"
            f"00:00:{start // 1000:02d},000 --> "
            f"00:00:{end // 1000:02d},000\n"
            f"{text}\n"
        )
    path.write_text("\n".join(blocks), encoding="utf-8")
    return path
