#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.AnalysisDiffCli."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.cli.analysis.analysis_cli import AnalysisCli
from scinoephile.cli.analysis.analysis_diff_cli import AnalysisDiffCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from test.helpers import assert_cli_help, assert_cli_usage


@pytest.mark.parametrize(
    "cli",
    [
        (AnalysisDiffCli,),
        (AnalysisCli, AnalysisDiffCli),
        (ScinoephileCli, AnalysisCli, AnalysisDiffCli),
    ],
)
def test_analysis_diff_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test analysis diff CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (AnalysisDiffCli,),
        (AnalysisCli, AnalysisDiffCli),
        (ScinoephileCli, AnalysisCli, AnalysisDiffCli),
    ],
)
def test_analysis_diff_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test analysis diff CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_analysis_diff_cli(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
):
    """Test analysis diff CLI output.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    one_infile_path = tmp_path / "one.srt"
    two_infile_path = tmp_path / "two.srt"
    one_infile_path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\n靠你了\n",
        encoding="utf-8",
    )
    two_infile_path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\n靠你喇！\n",
        encoding="utf-8",
    )

    run_cli_with_args(
        AnalysisDiffCli,
        f"--one-infile {one_infile_path} --two-infile {two_infile_path} "
        "--one-label TRANSCRIBE --two-label REFERENCE",
    )
    output = capsys.readouterr().out

    assert output == ("edit: TRANSCRIBE[1] -> REFERENCE[1]: '靠你了' -> '靠你喇！'\n")
