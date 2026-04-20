#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.YueProcessCli."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.cli.yue.yue_cli import YueCli
from scinoephile.cli.yue.yue_process_cli import YueProcessCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (YueProcessCli,),
        (YueCli, YueProcessCli),
        (ScinoephileCli, YueCli, YueProcessCli),
    ],
)
def test_yue_process_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test 粤文 processing CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (YueProcessCli,),
        (YueCli, YueProcessCli),
        (ScinoephileCli, YueCli, YueProcessCli),
    ],
)
def test_yue_process_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test 粤文 processing CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


@pytest.mark.parametrize(
    ("input_path", "args", "expected_path"),
    [
        (
            "kob/output/yue-Hans_timewarp_clean_flatten.srt",
            "--romanize",
            "kob/output/yue-Hans_timewarp_clean_flatten_romanize.srt",
        ),
    ],
)
def test_yue_process_cli(
    input_path: str,
    args: str,
    expected_path: str,
):
    """Test 粤文 processing CLI with file arguments.

    Arguments:
        input_path: path to input subtitle fixture
        args: command-line arguments for operation selection
        expected_path: path to expected output subtitle fixture
    """
    full_input_path = test_data_root / input_path
    full_expected_path = test_data_root / expected_path

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            YueProcessCli,
            f"--infile {full_input_path} {args} --outfile {output_path}",
        )
        output = Series.load(output_path)

    expected = Series.load(full_expected_path)
    assert output == expected


@pytest.mark.parametrize(
    ("input_path", "args", "expected_path"),
    [
        (
            "kob/output/yue-Hans_timewarp_clean_flatten.srt",
            "--romanize",
            "kob/output/yue-Hans_timewarp_clean_flatten_romanize.srt",
        ),
    ],
)
def test_yue_process_cli_pipe(input_path: str, args: str, expected_path: str):
    """Test 粤文 processing CLI via stdin/stdout.

    Arguments:
        input_path: path to input subtitle fixture
        args: command-line arguments for operation selection
        expected_path: path to expected output subtitle fixture
    """
    full_input_path = test_data_root / input_path
    full_expected_path = test_data_root / expected_path
    input_text = full_input_path.read_text()

    stdin_stream = StringIO(input_text)
    stdout_stream = StringIO()
    with patch("scinoephile.core.cli.stdin", stdin_stream):
        with patch("scinoephile.core.cli.stdout", stdout_stream):
            run_cli_with_args(YueProcessCli, f"--infile - {args}")

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(full_expected_path)
    assert output == expected
