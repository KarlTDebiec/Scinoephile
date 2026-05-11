#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.media.MediaProbeCli."""

from __future__ import annotations

from inspect import signature
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


def test_media_probe_cli_groups_arguments():
    """Test media probe CLI groups arguments by purpose."""
    groups = {
        group.title: {
            option
            for action in group._group_actions
            for option in action.option_strings
        }
        for group in MediaProbeCli.argparser()._action_groups
    }

    assert "--infile" in groups["input arguments"]
    assert "--details" in groups["operation arguments"]
    assert "--cache-dir" in groups["operation arguments"]


def test_media_probe_cli_main_orders_infile_before_details():
    """Test media probe CLI implementation signature follows argument order."""
    parameters = list(signature(MediaProbeCli._main).parameters)

    assert parameters.index("infile_path") < parameters.index("details")
    assert parameters.index("details") < parameters.index("cache_dir_path")


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
            "scinoephile.cli.media.media_probe_cli.with_stream_details",
            return_value=[],
        ) as with_details,
    ):
        run_cli_with_args(
            MediaProbeCli,
            f"--infile {infile_path} --details --cache-dir {cache_dir_path}",
        )

    get_streams.assert_called_once_with(infile_path.resolve())
    with_details.assert_called_once_with(
        infile_path.resolve(),
        [],
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


def test_media_probe_cli_details_uses_plain_probe(
    tmp_path: Path,
):
    """Test media probe CLI details mode avoids ffprobe packet counts.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with (
        patch(
            "scinoephile.media.probe.ffmpeg.probe",
            return_value={"streams": []},
        ) as probe,
        patch(
            "scinoephile.media.subtitle_analysis.details.cache_subtitle_stream_artifacts"
        ),
    ):
        run_cli_with_args(MediaProbeCli, f"--infile {infile_path} --details")

    probe.assert_called_once_with(str(infile_path.resolve()))


def test_media_probe_cli_details_includes_chinese_script_in_stream_id(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Test media probe CLI includes Chinese script analysis in stream ID.

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
                        "codec_name": "subrip",
                        "tags": {"language": "zho"},
                    },
                ],
            },
        ),
        patch(
            "scinoephile.media.subtitle_analysis.details.analyze_subtitle_stream_script"
        ) as analyze,
        patch(
            "scinoephile.media.subtitle_analysis.details.get_subtitle_stream_stats"
        ) as stats,
        patch(
            "scinoephile.media.subtitle_analysis.details.cache_subtitle_stream_artifacts"
        ),
    ):
        analyze.return_value.script = "zho-Hant"
        stats.return_value.event_count = 12
        stats.return_value.first_start_ms = 62_500
        stats.return_value.last_end_ms = 3_725_250
        run_cli_with_args(MediaProbeCli, f"--infile {infile_path} --details")

    assert capsys.readouterr().out.splitlines() == [
        (
            "Stream #0:2(zho-Hant): Subtitle: subrip "
            "(subtitles=12, span=00:01:02-01:02:05)"
        ),
    ]


def test_media_probe_cli_details_marks_undetermined_chinese_script(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Test media probe CLI marks unknown Chinese script in stream ID.

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
                        "codec_name": "subrip",
                        "tags": {"language": "zho"},
                    },
                ],
            },
        ),
        patch(
            "scinoephile.media.subtitle_analysis.details.analyze_subtitle_stream_script"
        ) as analyze,
        patch(
            "scinoephile.media.subtitle_analysis.details.get_subtitle_stream_stats"
        ) as stats,
        patch(
            "scinoephile.media.subtitle_analysis.details.cache_subtitle_stream_artifacts"
        ),
    ):
        analyze.return_value.script = None
        stats.return_value.event_count = 12
        stats.return_value.first_start_ms = 62_500
        stats.return_value.last_end_ms = 3_725_250
        run_cli_with_args(MediaProbeCli, f"--infile {infile_path} --details")

    assert capsys.readouterr().out.splitlines() == [
        (
            "Stream #0:2(zho-Unknown): Subtitle: subrip "
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
            "scinoephile.media.subtitle_analysis.details.get_subtitle_stream_stats",
            side_effect=ValueError("Malformed SUP data"),
        ),
        patch(
            "scinoephile.media.subtitle_analysis.details.cache_subtitle_stream_artifacts"
        ),
    ):
        run_cli_with_args(MediaProbeCli, f"--infile {infile_path} --details")

    assert capsys.readouterr().out.splitlines() == [
        "Stream #0:2(ita): Subtitle: hdmv_pgs_subtitle (title=SDH)",
    ]


def test_media_probe_cli_details_caches_subtitle_stream_artifacts_together(
    tmp_path: Path,
):
    """Test media probe CLI details mode caches subtitle streams in one batch.

    Arguments:
        tmp_path: temporary directory provided by pytest
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
                    {
                        "index": 3,
                        "codec_type": "subtitle",
                        "codec_name": "subrip",
                        "tags": {"language": "chi"},
                    },
                    {
                        "index": 4,
                        "codec_type": "subtitle",
                        "codec_name": "subrip",
                        "tags": {"language": "eng"},
                    },
                ],
            },
        ),
        patch(
            "scinoephile.media.subtitle_analysis.details.cache_subtitle_stream_artifacts"
        ) as cache,
        patch(
            "scinoephile.media.subtitle_analysis.details.analyze_subtitle_stream_script"
        ) as analyze,
        patch(
            "scinoephile.media.subtitle_analysis.details.get_subtitle_stream_stats",
        ) as stats,
    ):
        analyze.return_value.script = None
        stats.return_value.event_count = 12
        stats.return_value.first_start_ms = None
        stats.return_value.last_end_ms = None
        run_cli_with_args(MediaProbeCli, f"--infile {infile_path} --details")

    cache.assert_called_once()
    assert [stream.index for stream in cache.call_args.args[1]] == [2, 3, 4]


def test_media_probe_cli_uses_stream_models(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Test media probe CLI renders stream model descriptions.

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
                    "codec_name": "hevc",
                    "width": 3840,
                    "height": 2160,
                    "tags": {"title": "Main Video"},
                },
                {
                    "index": 1,
                    "codec_type": "audio",
                    "codec_name": "flac",
                    "channels": 2,
                    "tags": {"language": "jpn"},
                },
            ],
        },
    ):
        run_cli_with_args(MediaProbeCli, f"--infile {infile_path}")

    assert capsys.readouterr().out.splitlines() == [
        "Stream #0:0: Video: hevc (3840x2160, title=Main Video)",
        "Stream #0:1(jpn): Audio: flac (channels=2)",
    ]
