#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.media.MediaProbeCli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from scinoephile.cli.media.media_cli import MediaCli
from scinoephile.cli.media.media_probe_cli import MediaProbeCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (MediaProbeCli,),
        (MediaCli, MediaProbeCli),
        (ScinoephileCli, MediaCli, MediaProbeCli),
    ],
)
def test_media_probe_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test media probe CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (MediaProbeCli,),
        (MediaCli, MediaProbeCli),
        (ScinoephileCli, MediaCli, MediaProbeCli),
    ],
)
def test_media_probe_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test media probe CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_media_probe_cli_passes_cache_dir_to_stream_details(tmp_path: Path):
    """Test media probe CLI passes cache directory to stream detail enrichment."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    cache_dir_path = tmp_path / "cache"

    with (
        patch(
            "scinoephile.cli.media.media_probe_cli.get_streams",
            return_value=[],
        ) as get_streams,
        patch(
            "scinoephile.cli.media.media_probe_cli.get_zho_subtitle_streams",
            return_value=[],
        ) as get_zho_subtitle_streams,
    ):
        run_cli_with_args(
            MediaProbeCli,
            f"--infile {infile_path} --details --cache-dir {cache_dir_path}",
        )

    get_streams.assert_not_called()
    get_zho_subtitle_streams.assert_called_once_with(
        infile_path.resolve(),
        cache_dir_path=cache_dir_path.resolve(),
    )


def test_media_probe_cli_lists_all_streams(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Test media probe CLI lists all streams without packet counts.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with patch(
        "scinoephile.media.probe.ffmpeg.probe",
        return_value={
            "streams": [
                {
                    "index": 0,
                    "codec_type": "video",
                    "codec_name": "h264",
                    "width": 1920,
                    "height": 1080,
                },
                {
                    "index": 1,
                    "codec_type": "audio",
                    "codec_name": "aac",
                    "channels": 2,
                    "tags": {"language": "eng"},
                },
                {
                    "index": 2,
                    "codec_type": "subtitle",
                    "codec_name": "subrip",
                    "tags": {"language": "eng", "title": "SDH"},
                },
            ],
        },
    ) as probe:
        run_cli_with_args(MediaProbeCli, f"--infile {infile_path}")

    probe.assert_called_once_with(str(infile_path.resolve()))
    assert capsys.readouterr().out.splitlines() == [
        "Stream #0:0: Video: h264 (1920x1080)",
        "Stream #0:1(eng): Audio: aac (channels=2)",
        "Stream #0:2(eng): Subtitle: subrip (title=SDH)",
    ]


@pytest.mark.parametrize(
    ("script", "language"),
    [
        ("zho-Hant", "zho-Hant"),
        (None, "zho-Unknown"),
    ],
)
def test_media_probe_cli_details_includes_chinese_script_in_stream_id(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    script: str | None,
    language: str,
):
    """Test media probe CLI includes Chinese script analysis in stream ID.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
        script: detected script subtag, if determined
        language: expected stream language
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with (
        patch(
            "scinoephile.media.probe.ffmpeg.probe",
            return_value={
                "streams": [
                    {
                        "index": 2,
                        "codec_type": "subtitle",
                        "codec_name": "subrip",
                        "tags": {"language": "zho"},
                    },
                ],
            },
        ),
        patch(
            "scinoephile.lang.zho.subtitle_streams.analyze_zho_subtitle_stream_script"
        ) as analyze,
        patch("scinoephile.media.subtitles.details.get_subtitle_stream_stats") as stats,
        patch("scinoephile.media.subtitles.details.cache_subtitles"),
    ):
        analyze.return_value.script = script
        stats.return_value.event_count = 12
        stats.return_value.first_start_ms = 62_500
        stats.return_value.last_end_ms = 3_725_250
        run_cli_with_args(MediaProbeCli, f"--infile {infile_path} --details")

    assert capsys.readouterr().out.splitlines() == [
        (
            f"Stream #0:2({language}): Subtitle: subrip "
            "(subtitles=12, span=00:01:02-01:02:05)"
        ),
    ]


def test_media_probe_cli_details_omits_unreadable_subtitle_stats(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Test media probe CLI survives unreadable subtitle stats.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with (
        patch(
            "scinoephile.media.probe.ffmpeg.probe",
            return_value={
                "streams": [
                    {
                        "index": 2,
                        "codec_type": "subtitle",
                        "codec_name": "hdmv_pgs_subtitle",
                        "tags": {"language": "ita", "title": "SDH"},
                    },
                ],
            },
        ),
        patch(
            "scinoephile.media.subtitles.details.get_subtitle_stream_stats",
            side_effect=ValueError("Malformed SUP data"),
        ),
        patch("scinoephile.media.subtitles.details.cache_subtitles"),
    ):
        run_cli_with_args(MediaProbeCli, f"--infile {infile_path} --details")

    assert capsys.readouterr().out.splitlines() == [
        "Stream #0:2(ita): Subtitle: hdmv_pgs_subtitle (title=SDH)",
    ]
