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


@pytest.mark.parametrize(
    ("one_path", "two_path", "one_lbl", "two_lbl", "expected_fixture_name"),
    [
        (
            "kob/output/eng_ocr/fuse_clean_validate_review_flatten.srt",
            "kob/output/eng/timewarp_clean_review_flatten.srt",
            "OCR",
            "SRT",
            "kob_eng_expected_series_diff",
        ),
        (
            "mlamd/output/zho-Hans_fuse_clean_validate_review_flatten.srt",
            "mlamd/output/zho-Hant_fuse_clean_validate_review_flatten_simplify_"
            "review.srt",
            "SIMP",
            "TRAD",
            "mlamd_zho_simplify_expected_series_diff",
        ),
        (
            "mnt/output/zho-Hans_fuse_clean_validate_review_flatten.srt",
            "mnt/output/zho-Hant_fuse_clean_validate_review_flatten_simplify_"
            "review.srt",
            "SIMP",
            "TRAD",
            "mnt_zho_simplify_expected_series_diff",
        ),
        (
            "t/output/zho-Hans_fuse_clean_validate_review_flatten.srt",
            "t/output/zho-Hant_fuse_clean_validate_review_flatten_simplify_review.srt",
            "SIMP",
            "TRAD",
            "t_zho_simplify_expected_series_diff",
        ),
    ],
)
def test_analysis_diff_cli(
    one_path: str,
    two_path: str,
    one_lbl: str,
    two_lbl: str,
    expected_fixture_name: str,
    request: pytest.FixtureRequest,
    capsys: pytest.CaptureFixture,
):
    """Test analysis diff CLI output against expected differences.

    Arguments:
        one_path: path to first subtitle fixture
        two_path: path to second subtitle fixture
        one_lbl: label for first subtitle stream in diff output
        two_lbl: label for second subtitle stream in diff output
        expected_fixture_name: fixture name containing expected diff strings
        request: pytest fixture request object
        capsys: pytest stdout/stderr capture fixture
    """
    one_infile_path = test_data_root / one_path
    two_infile_path = test_data_root / two_path
    expected_edits: list[str] = request.getfixturevalue(expected_fixture_name)

    run_cli_with_args(
        AnalysisDiffCli,
        f"--one-infile {one_infile_path} --two-infile {two_infile_path} "
        f"--one-label {one_lbl} --two-label {two_lbl}",
    )
    output = capsys.readouterr().out

    for expected_edit in expected_edits:
        assert expected_edit in output


def test_analysis_diff_cli_alignment_experiment(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
):
    """Test analysis diff CLI experimental alignment output.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    one_infile_path = tmp_path / "one.srt"
    two_infile_path = tmp_path / "two.srt"
    srt_text = "1\n00:00:00,000 --> 00:00:01,000\nalpha\n"
    one_infile_path.write_text(srt_text, encoding="utf-8")
    two_infile_path.write_text(srt_text, encoding="utf-8")

    run_cli_with_args(
        AnalysisDiffCli,
        f"--one-infile {one_infile_path} --two-infile {two_infile_path} "
        "--alignment-experiment",
    )
    output = capsys.readouterr().out

    assert output == "Current diff:\n\nAlignment experiment diff:\n"
