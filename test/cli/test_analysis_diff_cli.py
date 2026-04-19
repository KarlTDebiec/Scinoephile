#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.AnalysisDiffCli."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

import pytest

from scinoephile.cli import AnalysisCli, AnalysisDiffCli, ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


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


def test_analysis_diff_cli():
    """Test analysis diff CLI output against known expected differences."""
    simp_infile_path = (
        test_data_root / "mnt/output/zho-Hans_fuse_clean_validate_proofread_flatten.srt"
    )
    trad_infile_path = (
        test_data_root
        / "mnt/output/zho-Hant_fuse_clean_validate_proofread_flatten_simplify_"
        "proofread.srt"
    )

    output_stdout = StringIO()
    with patch("scinoephile.cli.analysis_diff_cli.stdout", output_stdout):
        run_cli_with_args(
            AnalysisDiffCli,
            (
                f"{simp_infile_path} "
                f"{trad_infile_path} "
                "--one-label SIMP --two-label TRAD"
            ),
        )
    output = output_stdout.getvalue()

    assert "edit: SIMP[1] -> TRAD[1]: '《龙猫》' -> '龙猫'" in output
    assert (
        "edit: SIMP[4] -> TRAD[4]: '你们两个累不累啊' -> '妳们两个累不累啊'" in output
    )
    assert (
        "edit: SIMP[10] -> TRAD[10]: '我姓草壁\\u3000新搬来的' -> '我姓草壁，新搬来的'"
        in output
    )
