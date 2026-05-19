#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.media.MediaSearchSubsCli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from scinoephile.cli.media.media_cli import MediaCli
from scinoephile.cli.media.media_search_subs_cli import MediaSearchSubsCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from scinoephile.media.subtitles.opensubtitles import OpenSubtitlesFile
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (MediaSearchSubsCli,),
        (MediaCli, MediaSearchSubsCli),
        (ScinoephileCli, MediaCli, MediaSearchSubsCli),
    ],
)
def test_media_search_subs_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test media search-subs CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (MediaSearchSubsCli,),
        (MediaCli, MediaSearchSubsCli),
        (ScinoephileCli, MediaCli, MediaSearchSubsCli),
    ],
)
def test_media_search_subs_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test media search-subs CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_media_search_subs_cli_rejects_outfile_without_file_id(tmp_path: Path):
    """Test downloads require an explicit OpenSubtitles file_id.

    Arguments:
        tmp_path: temporary directory provided by pytest
    """
    with pytest.raises(SystemExit) as excinfo:
        run_cli_with_args(
            MediaSearchSubsCli,
            f"--query Matrix --language en -o {tmp_path / 'matrix.en.srt'}",
        )

    assert excinfo.value.code == 2


def test_media_search_subs_cli_rejects_file_id_without_outfile():
    """Test OpenSubtitles file_id requires an output file."""
    with pytest.raises(SystemExit) as excinfo:
        run_cli_with_args(
            MediaSearchSubsCli,
            "--query Matrix --language en --file-id 123",
        )

    assert excinfo.value.code == 2


def test_media_search_subs_cli_rejects_overwrite_without_outfile():
    """Test overwrite is only valid with an output file."""
    with pytest.raises(SystemExit) as excinfo:
        run_cli_with_args(
            MediaSearchSubsCli,
            "--query Matrix --language en --overwrite",
        )

    assert excinfo.value.code == 2


def test_media_search_subs_cli_searches_with_env_api_key(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
):
    """Test search-subs CLI searches and renders file results.

    Arguments:
        capsys: pytest output capture fixture
        monkeypatch: pytest monkeypatch fixture
    """
    monkeypatch.setenv("OPENSUBTITLES_API_KEY", "env-key")
    result = OpenSubtitlesFile(
        file_id=123,
        language="en",
        download_count=42,
        rating=9.1,
        fps=23.976,
        release_name="The.Matrix.1999.1080p.BluRay.x264",
        file_name="The.Matrix.1999.1080p.srt",
    )

    with patch(
        "scinoephile.cli.media.media_search_subs_cli.OpenSubtitlesClient"
    ) as client_type:
        client_type.return_value.search.return_value = [result]
        run_cli_with_args(
            MediaSearchSubsCli,
            "--query Matrix --language en --limit 5",
        )

    client_type.assert_called_once_with(api_key="env-key")
    client_type.return_value.search.assert_called_once_with(
        query="Matrix",
        language="en",
        limit=5,
    )
    assert capsys.readouterr().out.splitlines() == [
        "file_id\tlang\tdownloads\trating\tfps\trelease/file",
        "123\ten\t42\t9.1\t23.976\tThe.Matrix.1999.1080p.BluRay.x264",
    ]


def test_media_search_subs_cli_downloads_selected_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
):
    """Test search-subs CLI downloads an explicit file_id.

    Arguments:
        tmp_path: temporary directory provided by pytest
        monkeypatch: pytest monkeypatch fixture
    """
    outfile_path = tmp_path / "matrix.en.srt"
    monkeypatch.setenv("OPENSUBTITLES_API_KEY", "env-key")
    monkeypatch.setenv("OPENSUBTITLES_USERNAME", "env-user")
    monkeypatch.setenv("OPENSUBTITLES_PASSWORD", "env-password")

    with patch(
        "scinoephile.cli.media.media_search_subs_cli.OpenSubtitlesClient"
    ) as client_type:
        client_type.return_value.search.return_value = [
            OpenSubtitlesFile(file_id=123, language="en")
        ]
        run_cli_with_args(
            MediaSearchSubsCli,
            f"--query Matrix --language en --file-id 123 -o {outfile_path}",
        )

    client_type.assert_called_once_with(api_key="env-key")
    client_type.return_value.search.assert_called_once_with(
        query="Matrix",
        language="en",
        limit=10,
    )
    client_type.return_value.download.assert_called_once_with(
        file_id=123,
        outfile_path=outfile_path.resolve(),
        username="env-user",
        password="env-password",
        overwrite=False,
    )
