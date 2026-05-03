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


def test_analysis_diff_cli_multiline_split_edit(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
):
    """Test analysis diff CLI output for multi-line alignment.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    one_infile_path = tmp_path / "one.srt"
    two_infile_path = tmp_path / "two.srt"
    one_infile_path.write_text(
        "1\n00:00:00,000 --> 00:00:02,000\nalpha beta\n",
        encoding="utf-8",
    )
    two_infile_path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\nalpha\n\n"
        "2\n00:00:01,000 --> 00:00:02,000\nbetx\n",
        encoding="utf-8",
    )

    run_cli_with_args(
        AnalysisDiffCli,
        f"--one-infile {one_infile_path} --two-infile {two_infile_path} "
        "--one-label TRANSCRIBE --two-label REFERENCE",
    )
    output = capsys.readouterr().out

    assert output == (
        "split_edit: TRANSCRIBE[1] -> REFERENCE[1-2]: "
        "['alpha beta'] -> ['alpha', 'betx']\n"
    )


@pytest.mark.parametrize(
    (
        "one_path",
        "two_path",
        "one_label",
        "two_label",
        "expected_fixture_name",
    ),
    [
        (
            Path("kob/output/eng_ocr/fuse_clean_validate_review_flatten.srt"),
            Path("kob/output/eng/timewarp_clean_review_flatten.srt"),
            "OCR",
            "SRT",
            "kob_eng_expected_series_diff",
        ),
        (
            Path("mlamd/output/zho-Hans_fuse_clean_validate_review_flatten.srt"),
            Path(
                "mlamd/output/"
                "zho-Hant_fuse_clean_validate_review_flatten_simplify_review.srt"
            ),
            "SIMP",
            "TRAD",
            "mlamd_zho_simplify_expected_series_diff",
        ),
        (
            Path("mnt/output/zho-Hans_fuse_clean_validate_review_flatten.srt"),
            Path(
                "mnt/output/"
                "zho-Hant_fuse_clean_validate_review_flatten_simplify_review.srt"
            ),
            "SIMP",
            "TRAD",
            "mnt_zho_simplify_expected_series_diff",
        ),
        (
            Path("t/output/zho-Hans_fuse_clean_validate_review_flatten.srt"),
            Path(
                "t/output/"
                "zho-Hant_fuse_clean_validate_review_flatten_simplify_review.srt"
            ),
            "SIMP",
            "TRAD",
            "t_zho_simplify_expected_series_diff",
        ),
    ],
)
def test_analysis_diff_cli_matches_expected_fixture(
    one_path: Path,
    two_path: Path,
    one_label: str,
    two_label: str,
    expected_fixture_name: str,
    capsys: pytest.CaptureFixture,
    request: pytest.FixtureRequest,
):
    """Test analysis diff CLI output against real subtitle fixtures.

    Arguments:
        one_path: first subtitle path relative to test data root
        two_path: second subtitle path relative to test data root
        one_label: label for the first subtitle series
        two_label: label for the second subtitle series
        expected_fixture_name: fixture name containing expected diff strings
        capsys: pytest stdout/stderr capture fixture
        request: pytest fixture request object
    """
    expected: list[str] = request.getfixturevalue(expected_fixture_name)

    run_cli_with_args(
        AnalysisDiffCli,
        f"--one-infile {test_data_root / one_path} "
        f"--two-infile {test_data_root / two_path} "
        f"--one-label {one_label} --two-label {two_label}",
    )
    output = capsys.readouterr().out

    assert output.splitlines() == expected
