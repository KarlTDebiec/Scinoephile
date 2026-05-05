#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ExtractCli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from scinoephile.cli.extract_cli import ExtractCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.media import SubtitleStream
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (ExtractCli,),
        (ScinoephileCli, ExtractCli),
    ],
)
def test_extract_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test extract CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (ExtractCli,),
        (ScinoephileCli, ExtractCli),
    ],
)
def test_extract_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test extract CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_extract_cli(tmp_path: Path):
    """Test extract CLI exports matching streams."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"

    with (
        patch(
            "scinoephile.cli.extract_cli.get_subtitle_streams",
            return_value=[
                SubtitleStream(index=2, language="eng", codec_name="subrip"),
                SubtitleStream(index=3, language="jpn", codec_name="subrip"),
                SubtitleStream(index=4, language="zho", codec_name="subrip"),
            ],
        ) as get_streams,
        patch("scinoephile.cli.extract_cli.extract_subtitle_stream") as extract,
    ):
        run_cli_with_args(
            ExtractCli,
            f"--infile {infile_path} --languages eng zho -o {output_dir_path} --export",
        )

    get_streams.assert_called_once_with(infile_path.resolve(), counts=False)
    assert extract.call_count == 2
    assert extract.call_args_list[0].args[0] == infile_path.resolve()
    assert extract.call_args_list[0].args[1].index == 2
    assert extract.call_args_list[0].args[2] == output_dir_path.resolve() / "eng-2.srt"
    assert extract.call_args_list[1].args[0] == infile_path.resolve()
    assert extract.call_args_list[1].args[1].index == 4
    assert extract.call_args_list[1].args[2] == output_dir_path.resolve() / "zho-4.srt"


def test_extract_cli_lists_without_output_dir(tmp_path: Path):
    """Test extract CLI lists matching streams without output directory."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with (
        patch(
            "scinoephile.cli.extract_cli.get_subtitle_streams",
            return_value=[
                SubtitleStream(
                    index=2,
                    language="eng",
                    codec_name="subrip",
                    subtitle_count=42,
                ),
            ],
        ) as get_streams,
        patch("scinoephile.cli.extract_cli.extract_subtitle_stream") as extract,
    ):
        run_cli_with_args(
            ExtractCli,
            f"--infile {infile_path} --languages ENG --details",
        )

    get_streams.assert_called_once_with(infile_path.resolve(), counts=True)
    extract.assert_not_called()


def test_extract_cli_lists_with_output_dir(tmp_path: Path):
    """Test extract CLI lists output paths without exporting."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"

    with (
        patch(
            "scinoephile.cli.extract_cli.get_subtitle_streams",
            return_value=[
                SubtitleStream(index=2, language="eng", codec_name="subrip"),
            ],
        ),
        patch("scinoephile.cli.extract_cli.extract_subtitle_stream") as extract,
    ):
        run_cli_with_args(
            ExtractCli,
            f"--infile {infile_path} --languages eng -o {output_dir_path}",
        )

    extract.assert_not_called()


def test_extract_cli_overwrites_existing_file(tmp_path: Path):
    """Test extract CLI overwrite exports existing matching streams."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"
    output_dir_path.mkdir()
    outfile_path = output_dir_path / "eng-2.srt"
    outfile_path.touch()

    with (
        patch(
            "scinoephile.cli.extract_cli.get_subtitle_streams",
            return_value=[
                SubtitleStream(index=2, language="eng", codec_name="subrip"),
            ],
        ),
        patch("scinoephile.cli.extract_cli.extract_subtitle_stream") as extract,
    ):
        run_cli_with_args(
            ExtractCli,
            f"--infile {infile_path} --languages eng -o {output_dir_path} "
            "--export --overwrite",
        )

    extract.assert_called_once()
    assert extract.call_args.args[2] == outfile_path.resolve()


def test_extract_cli_export_requires_output_dir(tmp_path: Path):
    """Test extract CLI rejects export without output directory."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()

    with pytest.raises(SystemExit) as excinfo:
        run_cli_with_args(ExtractCli, f"--infile {infile_path} --export")

    assert excinfo.value.code == 2


def test_extract_cli_overwrite_requires_export(tmp_path: Path):
    """Test extract CLI rejects overwrite without export."""
    infile_path = tmp_path / "video.mkv"
    infile_path.touch()
    output_dir_path = tmp_path / "subtitles"

    with pytest.raises(SystemExit) as excinfo:
        run_cli_with_args(
            ExtractCli,
            f"--infile {infile_path} -o {output_dir_path} --overwrite",
        )

    assert excinfo.value.code == 2
