#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the aligned multi-source transcription CLI."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import ANY, Mock, patch

from pydub import AudioSegment
from pytest import CaptureFixture, mark, raises

from scinoephile.analysis.transcription import TimingSettings
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import DemucsMode
from scinoephile.audio.vad import VadImplementation
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.transcribe_cli import TranscribeCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.workflows.transcription_pipeline import AudioAnalysisMode


def test_transcribe_cli_is_top_level_command():
    """Test the top-level command registry exposes transcription."""
    assert ScinoephileCli.subcommands()["transcribe"] is TranscribeCli


def test_transcribe_help_exposes_only_aligned_pipeline_options():
    """Test help omits reference-guided transcription options."""
    actions = {
        action.dest: action
        for action in TranscribeCli.argparser()._actions  # noqa: SLF001
    }

    assert "media_infile_path" in actions
    assert "language" in actions
    assert "json_path" in actions
    assert "alignment_outfile_path" in actions
    assert "guide_infile_path" not in actions
    assert "model" not in actions
    assert "delineation_json_path" not in actions
    assert "punctuation_json_path" not in actions
    assert actions["diarization_mode"].default is AudioAnalysisMode.AUTO
    assert actions["language_identification_mode"].default is AudioAnalysisMode.AUTO
    assert actions["audio_event_mode"].default is AudioAnalysisMode.AUTO
    assert actions["block_vad_implementation"].default is VadImplementation.PYANNOTE
    timing_defaults = TimingSettings()
    assert actions["lead_in_seconds"].default == timing_defaults.lead_in_seconds
    assert actions["lead_out_seconds"].default == timing_defaults.lead_out_seconds
    assert (
        actions["minimum_duration_seconds"].default
        == timing_defaults.minimum_duration_seconds
    )


def test_transcribe_cli_dispatches_and_derives_output_paths(tmp_path: Path):
    """Test the CLI loads complete audio and derives companion output paths.

    Arguments:
        tmp_path: temporary directory path
    """
    media_path = tmp_path / "audio.wav"
    media_path.touch()
    audio = Mock(spec=AudioSeries)
    output = Series(events=[Subtitle(start=0, end=1000, text="字幕")])
    provider = Mock()
    outfile_path = tmp_path / "transcribe.srt"
    json_path = tmp_path / "transcription.json"
    with (
        patch(
            "scinoephile.cli.transcribe_cli.AudioSeries.load_from_media",
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
                f"--media-infile {media_path} --language yue-Hant "
                f"--first-block 2 --last-block 3 --lead-in 0.1 --lead-out 0.2 "
                f"--minimum-duration 1.0 --json {json_path} "
                f"--outfile {outfile_path} --overwrite"
            ),
        )

    load_audio.assert_called_once_with(
        media_path=media_path.resolve(), stream_index=None
    )
    transcribe.assert_called_once_with(
        audio,
        language=Language.yue_hant,
        audio_event_mode=AudioAnalysisMode.AUTO,
        demucs_mode=DemucsMode.OFF,
        diarization_mode=AudioAnalysisMode.AUTO,
        language_identification_mode=AudioAnalysisMode.AUTO,
        block_vad_implementation=VadImplementation.PYANNOTE,
        cache_root_path=ANY,
        overwrite_cache=False,
        provider=provider,
        additional_context=None,
        no_op=False,
        current_test_cases_path=json_path.resolve(),
        alignment_outfile_path=tmp_path / "transcribe.alignment.json",
        run_manifest_outfile_path=tmp_path / "transcribe.run.json",
        timing_settings=TimingSettings(
            lead_in_seconds=0.1, lead_out_seconds=0.2, minimum_duration_seconds=1.0
        ),
        start_at_idx=1,
        stop_at_idx=3,
    )
    write_series.assert_called_once_with(ANY, output, outfile_path.resolve(), True)


def test_transcribe_cli_writes_stdout_without_companion_outputs(tmp_path: Path):
    """Test stdout-only operation does not invent output paths.

    Arguments:
        tmp_path: temporary directory path
    """
    media_path = tmp_path / "audio.wav"
    media_path.touch()
    audio = AudioSeries(audio=AudioSegment.silent(duration=1000), events=[])
    output = Series(events=[])
    with (
        patch(
            "scinoephile.cli.transcribe_cli.AudioSeries.load_from_media",
            return_value=audio,
        ),
        patch("scinoephile.cli.transcribe_cli.get_provider"),
        patch(
            "scinoephile.cli.transcribe_cli.transcribe_series", return_value=output
        ) as transcribe,
        patch("scinoephile.cli.transcribe_cli.write_series") as write_series,
    ):
        run_cli_with_args(
            TranscribeCli, f"--media-infile {media_path} --language yue-Hant"
        )

    assert transcribe.call_args.kwargs["alignment_outfile_path"] is None
    assert transcribe.call_args.kwargs["run_manifest_outfile_path"] is None
    write_series.assert_called_once_with(ANY, output, "-", False)


def test_transcribe_cli_writes_explicit_alignment_while_subtitles_use_stdout(
    tmp_path: Path,
):
    """Test an explicit alignment output also derives a run-manifest path.

    Arguments:
        tmp_path: temporary directory path
    """
    media_path = tmp_path / "audio.wav"
    media_path.touch()
    alignment_path = tmp_path / "custom-alignment"
    audio = AudioSeries(audio=AudioSegment.silent(duration=1000), events=[])
    output = Series(events=[])
    with (
        patch(
            "scinoephile.cli.transcribe_cli.AudioSeries.load_from_media",
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
            (
                f"--media-infile {media_path} --language yue-Hant "
                f"--alignment-outfile {alignment_path} --overwrite"
            ),
        )

    assert transcribe.call_args.kwargs["alignment_outfile_path"] == (
        alignment_path.resolve()
    )
    assert transcribe.call_args.kwargs["run_manifest_outfile_path"] == (
        tmp_path / "custom-alignment.run.json"
    )
    write_series.assert_called_once_with(ANY, output, "-", True)


@mark.parametrize(
    ("outfile_name", "alignment_outfile_name"),
    (("transcribe.srt", "transcribe.srt"), ("transcribe.srt", "transcribe.run.json")),
)
def test_transcribe_cli_rejects_colliding_output_paths(
    tmp_path: Path,
    capsys: CaptureFixture,
    outfile_name: str,
    alignment_outfile_name: str,
):
    """Test subtitle, alignment, and run-manifest paths must be distinct.

    Arguments:
        tmp_path: temporary directory path
        capsys: pytest stdout/stderr capture fixture
        outfile_name: subtitle output filename
        alignment_outfile_name: alignment output filename
    """
    media_path = tmp_path / "audio.wav"
    media_path.touch()
    outfile_path = tmp_path / outfile_name
    alignment_outfile_path = tmp_path / alignment_outfile_name

    with (
        patch(
            "scinoephile.cli.transcribe_cli.AudioSeries.load_from_media"
        ) as load_audio,
        raises(SystemExit),
    ):
        run_cli_with_args(
            TranscribeCli,
            (
                f"--media-infile {media_path} --language yue-Hant "
                f"--outfile {outfile_path} "
                f"--alignment-outfile {alignment_outfile_path} --overwrite"
            ),
        )

    assert "Output file paths must be distinct" in capsys.readouterr().err
    load_audio.assert_not_called()


def test_transcribe_cli_rejects_reversed_block_range(
    tmp_path: Path, capsys: CaptureFixture
):
    """Test reversed block ranges are rejected before audio loading.

    Arguments:
        tmp_path: temporary directory path
        capsys: pytest stdout/stderr capture fixture
    """
    media_path = tmp_path / "audio.wav"
    media_path.touch()
    with (
        patch(
            "scinoephile.cli.transcribe_cli.AudioSeries.load_from_media"
        ) as load_audio,
        raises(SystemExit),
    ):
        run_cli_with_args(
            TranscribeCli,
            (
                f"--media-infile {media_path} --language yue-Hant "
                "--first-block 3 --last-block 2"
            ),
        )
    assert "--first-block must be less than or equal" in capsys.readouterr().err
    load_audio.assert_not_called()


def test_transcribe_cli_wraps_workflow_errors(tmp_path: Path, capsys: CaptureFixture):
    """Test domain failures become user-facing parser errors.

    Arguments:
        tmp_path: temporary directory path
        capsys: pytest stdout/stderr capture fixture
    """
    media_path = tmp_path / "audio.wav"
    media_path.touch()
    with (
        patch(
            "scinoephile.cli.transcribe_cli.AudioSeries.load_from_media",
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
            TranscribeCli, f"--media-infile {media_path} --language yue-Hant"
        )
    assert "merge failed" in capsys.readouterr().err
