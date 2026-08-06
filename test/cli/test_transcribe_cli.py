#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the aligned multi-source transcription CLI."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import ANY, Mock, patch

from pydub import AudioSegment
from pytest import CaptureFixture, raises

from scinoephile.analysis.transcription_alignment import SubtitleTimingSettings
from scinoephile.audio.diarization import DiarizationMode
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import DemucsMode, VADImplementation
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.transcribe_cli import TranscribeCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle


def test_transcribe_cli_is_top_level_command():
    """The top-level command registry should expose transcription."""
    assert ScinoephileCli.subcommands()["transcribe"] is TranscribeCli


def test_transcribe_help_exposes_only_aligned_pipeline_options():
    """Legacy guide, backend, delineation, and punctuation switches should be gone."""
    actions = {
        action.dest: action
        for action in TranscribeCli.argparser()._actions  # noqa: SLF001
    }

    assert "media_infile_path" in actions
    assert "language" in actions
    assert "aligned_merge_json_path" in actions
    assert "alignment_outfile_path" in actions
    assert "guide_infile_path" not in actions
    assert "backend" not in actions
    assert "delineation_json_path" not in actions
    assert "punctuation_json_path" not in actions
    assert actions["diarization_mode"].default is DiarizationMode.AUTO
    assert actions["block_vad_implementation"].default is VADImplementation.PYANNOTE


def test_transcribe_cli_dispatches_and_derives_alignment_path(tmp_path: Path):
    """The CLI should load complete audio and write SRT plus a derived artifact."""
    audio = Mock(spec=AudioSeries)
    output = Series(events=[Subtitle(start=0, end=1000, text="字幕")])
    provider = Mock()
    outfile_path = tmp_path / "transcribe.srt"
    with (
        patch(
            "scinoephile.cli.transcribe_cli.AudioSeries.load_audio_from_media",
            return_value=audio,
        ) as load_audio,
        patch("scinoephile.cli.transcribe_cli.get_provider", return_value=provider),
        patch(
            "scinoephile.cli.transcribe_cli.transcribe_series", return_value=output
        ) as transcribe,
        patch("scinoephile.cli.transcribe_cli.write_series") as write_series,
    ):
        run_cli_with_args(
            TranscribeCli,
            (
                f"--media-infile {tmp_path / 'audio.wav'} --language yue-Hant "
                f"--first-block 2 --last-block 3 --lead-in 0.1 --lead-out 0.2 "
                f"--minimum-duration 1.0 --outfile {outfile_path} --overwrite"
            ),
        )

    load_audio.assert_called_once_with(
        media_path=str(tmp_path / "audio.wav"), stream_index=None
    )
    transcribe.assert_called_once_with(
        audio,
        language=Language.yue_hant,
        demucs_mode=DemucsMode.OFF,
        diarization_mode=DiarizationMode.AUTO,
        vad_implementation=VADImplementation.SILERO,
        block_vad_implementation=VADImplementation.PYANNOTE,
        mlx_audio_token_limit_guard=True,
        cache_root_path=ANY,
        overwrite_cache=False,
        provider=provider,
        additional_context=None,
        no_op=False,
        aligned_merge_json_path=None,
        alignment_json_path=tmp_path / "transcribe.alignment.json",
        timing_settings=SubtitleTimingSettings(
            lead_in_seconds=0.1, lead_out_seconds=0.2, minimum_duration_seconds=1.0
        ),
        start_at_idx=1,
        stop_at_idx=3,
    )
    write_series.assert_called_once_with(ANY, output, outfile_path, True)


def test_transcribe_cli_writes_stdout_without_artifact(tmp_path: Path):
    """Stdout-only operation should not invent an artifact path."""
    audio = AudioSeries(audio=AudioSegment.silent(duration=1000), events=[])
    output = Series(events=[])
    with (
        patch(
            "scinoephile.cli.transcribe_cli.AudioSeries.load_audio_from_media",
            return_value=audio,
        ),
        patch("scinoephile.cli.transcribe_cli.get_provider"),
        patch(
            "scinoephile.cli.transcribe_cli.transcribe_series", return_value=output
        ) as transcribe,
        patch("scinoephile.cli.transcribe_cli.write_series") as write_series,
    ):
        run_cli_with_args(
            TranscribeCli,
            f"--media-infile {tmp_path / 'audio.wav'} --language yue-Hant",
        )

    assert transcribe.call_args.kwargs["alignment_json_path"] is None
    write_series.assert_called_once_with(ANY, output, "-", False)


def test_transcribe_cli_rejects_reversed_block_range(
    tmp_path: Path, capsys: CaptureFixture
):
    """Block selection should reject a reversed inclusive range.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    with raises(SystemExit):
        run_cli_with_args(
            TranscribeCli,
            (
                f"--media-infile {tmp_path / 'audio.wav'} --language yue-Hant "
                "--first-block 3 --last-block 2"
            ),
        )
    assert "--first-block must be less than or equal" in capsys.readouterr().err


def test_transcribe_cli_wraps_workflow_errors(tmp_path: Path, capsys: CaptureFixture):
    """Domain failures should become user-facing parser errors.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    with (
        patch(
            "scinoephile.cli.transcribe_cli.AudioSeries.load_audio_from_media",
            return_value=Mock(spec=AudioSeries),
        ),
        patch("scinoephile.cli.transcribe_cli.get_provider"),
        patch(
            "scinoephile.cli.transcribe_cli.transcribe_series",
            side_effect=ScinoephileError("merge failed"),
        ),
        raises(SystemExit),
    ):
        run_cli_with_args(
            TranscribeCli,
            f"--media-infile {tmp_path / 'audio.wav'} --language yue-Hant",
        )
    assert "merge failed" in capsys.readouterr().err
