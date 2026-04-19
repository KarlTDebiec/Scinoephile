#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.YueCli."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.yue_cli import YueCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from scinoephile.lang.yue import get_yue_romanized
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (YueCli,),
        (ScinoephileCli, YueCli),
    ],
)
def test_yue_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test 粤文 CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (YueCli,),
        (ScinoephileCli, YueCli),
    ],
)
def test_yue_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test 粤文 CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_yue_cli_romanize():
    """Test 粤文 CLI direct romanization with file arguments."""
    input_path = test_data_root / "kob" / "input" / "yue-Hant.srt"

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            YueCli,
            f"--infile {input_path} --romanize --outfile {output_path}",
        )
        output = Series.load(output_path)

    expected = get_yue_romanized(Series.load(input_path), append=True)
    assert output == expected


def test_yue_cli_romanize_pipe():
    """Test 粤文 CLI direct romanization via stdin/stdout."""
    input_path = test_data_root / "kob" / "input" / "yue-Hant.srt"
    input_text = input_path.read_text()
    expected = get_yue_romanized(
        Series.from_string(input_text, format_="srt"),
        append=True,
    )

    stdin_stream = StringIO(input_text)
    stdout_stream = StringIO()
    with patch("scinoephile.core.cli.io.stdin", stdin_stream):
        with patch("scinoephile.core.cli.io.stdout", stdout_stream):
            run_cli_with_args(YueCli, "--romanize")

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert output == expected
