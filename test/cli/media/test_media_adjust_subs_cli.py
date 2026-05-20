#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.media.MediaAdjustSubsCli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest
from pydub import AudioSegment

from scinoephile.audio.subtitles import AudioSeries, AudioSubtitle
from scinoephile.audio.subtitles.timing_adjustment import (
    SubtitleTimingAdjustmentBlockDiagnostics,
    SubtitleTimingAdjustmentCueDiagnostics,
    SubtitleTimingAdjustmentResult,
)
from scinoephile.cli.media.media_adjust_subs_cli import MediaAdjustSubsCli
from scinoephile.cli.utility.cache.argument_types import cache_dir_path_arg
from scinoephile.common.testing import run_cli_with_args


def test_media_adjust_subs_cli_loads_adjusts_and_saves(tmp_path: Path):
    """Test CLI wires media loading, adjustment, and subtitle output."""
    media_infile_path = tmp_path / "movie.mkv"
    subtitle_infile_path = tmp_path / "movie.srt"
    outfile_path = tmp_path / "adjusted.srt"
    cache_dir_path = tmp_path / "cache"
    media_infile_path.touch()
    subtitle_infile_path.touch()
    loaded_series = AudioSeries(
        audio=AudioSegment.silent(duration=5000),
        events=[AudioSubtitle(start=1000, end=1500, text="hello")],
    )
    adjusted_series = AudioSeries(
        audio=AudioSegment.silent(duration=5000),
        events=[AudioSubtitle(start=900, end=2400, text="hello")],
    )
    result = SubtitleTimingAdjustmentResult(series=adjusted_series, blocks=[])

    with (
        patch(
            "scinoephile.cli.media.media_adjust_subs_cli.AudioSeries.load_from_media",
            return_value=loaded_series,
        ) as load_from_media,
        patch(
            "scinoephile.cli.media.media_adjust_subs_cli.WhisperSpeechActivityDetector"
        ) as detector_cls,
        patch(
            "scinoephile.cli.media.media_adjust_subs_cli.get_series_timing_adjustment",
            return_value=result,
        ) as adjust,
        patch.object(adjusted_series, "save") as save,
    ):
        run_cli_with_args(
            MediaAdjustSubsCli,
            f"--media-infile {media_infile_path} "
            f"--subtitle-infile {subtitle_infile_path} "
            f"--outfile {outfile_path} "
            f"--cache-dir {cache_dir_path} "
            "--stream-index 1 "
            "--buffer 1500 "
            "--block-pause-length 2500 "
            "--vad-backend whisper "
            "--max-start-expansion 600 "
            "--max-end-expansion 900 "
            "--gap-merge-threshold 120 "
            "--minimum-speech-duration 80",
        )

    load_from_media.assert_called_once_with(
        media_path=media_infile_path.resolve(),
        subtitle_path=subtitle_infile_path.resolve(),
        stream_index=1,
        buffer=1500,
        cache_dir_path=cache_dir_path.resolve(),
    )
    detector_cls.assert_called_once_with(
        cache_dir_path=cache_dir_path.resolve() / "speech",
        merge_gap_ms=120,
        min_duration_ms=80,
    )
    config = adjust.call_args.kwargs["config"]
    assert adjust.call_args.kwargs["speech_detector"] == detector_cls.return_value
    assert config.block_pause_length_ms == 2500
    assert config.max_start_expansion_ms == 600
    assert config.max_end_expansion_ms == 900
    assert config.merge_gap_ms == 120
    assert config.min_speech_duration_ms == 80
    save.assert_called_once_with(outfile_path.resolve(), format_="srt")


def test_media_adjust_subs_cli_saves_suffixless_output_as_subtitles(tmp_path: Path):
    """Test suffixless output paths are saved with a subtitle format."""
    media_infile_path = tmp_path / "movie.mkv"
    subtitle_infile_path = tmp_path / "movie.srt"
    outfile_path = tmp_path / "adjusted"
    media_infile_path.touch()
    subtitle_infile_path.touch()
    adjusted_series = AudioSeries(
        audio=AudioSegment.silent(duration=5000),
        events=[AudioSubtitle(start=900, end=2400, text="hello")],
    )
    result = SubtitleTimingAdjustmentResult(series=adjusted_series, blocks=[])

    with (
        patch(
            "scinoephile.cli.media.media_adjust_subs_cli.AudioSeries.load_from_media"
        ) as load_from_media,
        patch(
            "scinoephile.cli.media.media_adjust_subs_cli.WhisperSpeechActivityDetector"
        ),
        patch(
            "scinoephile.cli.media.media_adjust_subs_cli.get_series_timing_adjustment",
            return_value=result,
        ),
        patch.object(adjusted_series, "save") as save,
    ):
        run_cli_with_args(
            MediaAdjustSubsCli,
            f"--media-infile {media_infile_path} "
            f"--subtitle-infile {subtitle_infile_path} "
            f"--outfile {outfile_path}",
        )

    save.assert_called_once_with(outfile_path.resolve(), format_="srt")
    load_from_media.assert_called_once_with(
        media_path=media_infile_path.resolve(),
        subtitle_path=subtitle_infile_path.resolve(),
        stream_index=None,
        buffer=2000,
        cache_dir_path=cache_dir_path_arg("media", "audio"),
    )


def test_media_adjust_subs_cli_dry_run_prints_diagnostics(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Test dry-run mode reports diagnostics without saving subtitles.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    media_infile_path = tmp_path / "movie.mkv"
    subtitle_infile_path = tmp_path / "movie.srt"
    outfile_path = tmp_path / "adjusted.srt"
    media_infile_path.touch()
    subtitle_infile_path.touch()
    adjusted_series = AudioSeries(
        audio=AudioSegment.silent(duration=5000),
        events=[AudioSubtitle(start=900, end=2400, text="hello")],
    )
    cue_diagnostics = SubtitleTimingAdjustmentCueDiagnostics(
        cue_idx=0,
        text="hello",
        original_start_ms=1000,
        original_end_ms=1500,
        adjusted_start_ms=900,
        adjusted_end_ms=2400,
        speech_duration_ms=1500,
        speech_coverage_before_ms=500,
        speech_coverage_after_ms=1500,
        silence_overhang_before_ms=0,
        silence_overhang_after_ms=0,
        start_delta_ms=-100,
        end_delta_ms=900,
        blocked_start_expansion_ms=0,
        blocked_end_expansion_ms=0,
        unchanged=False,
    )
    result = SubtitleTimingAdjustmentResult(
        series=adjusted_series,
        blocks=[
            SubtitleTimingAdjustmentBlockDiagnostics(
                start_idx=0,
                end_idx=1,
                buffered_start_ms=0,
                buffered_end_ms=3000,
                cues=[cue_diagnostics],
            )
        ],
    )

    with (
        patch(
            "scinoephile.cli.media.media_adjust_subs_cli.AudioSeries.load_from_media"
        ),
        patch(
            "scinoephile.cli.media.media_adjust_subs_cli.WhisperSpeechActivityDetector"
        ),
        patch(
            "scinoephile.cli.media.media_adjust_subs_cli.get_series_timing_adjustment",
            return_value=result,
        ),
        patch.object(adjusted_series, "save") as save,
    ):
        run_cli_with_args(
            MediaAdjustSubsCli,
            f"--media-infile {media_infile_path} "
            f"--subtitle-infile {subtitle_infile_path} "
            f"--outfile {outfile_path} "
            "--dry-run",
        )

    save.assert_not_called()
    assert capsys.readouterr().out.splitlines() == [
        "Adjusted cues: 1/1",
        "Total start delta: -0.100 s",
        "Total end delta: +0.900 s",
        "Blocked expansion: start +0.000 s, end +0.000 s",
    ]
