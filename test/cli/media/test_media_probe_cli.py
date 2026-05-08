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


def test_media_probe_cli_lists_all_streams_with_counts(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
):
    """Test media probe CLI lists all streams with packet counts.

    Arguments:
        tmp_path: temporary directory provided by pytest
        capsys: pytest output capture fixture
    """
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with patch(
        "scinoephile.cli.media.media_probe_cli.ffmpeg.probe",
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
                    "nb_read_packets": "42",
                },
            ],
        },
    ) as probe:
        run_cli_with_args(MediaProbeCli, f"--infile {infile_path}")

    probe.assert_called_once_with(str(infile_path.resolve()), count_packets=None)
    assert capsys.readouterr().out.splitlines() == [
        "Stream #0:0: Video: h264 (1920x1080)",
        "Stream #0:1(eng): Audio: aac (channels=2)",
        "Stream #0:2(eng): Subtitle: subrip (title=SDH, packets=42)",
    ]
