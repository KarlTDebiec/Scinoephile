#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the multi diff CLI."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.cli.multi.multi_cli import MultiCli
from scinoephile.cli.multi.multi_diff_cli import MultiDiffCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.testing import run_cli_with_args
from test.helpers import assert_cli_help, assert_cli_usage, test_data_root


@pytest.mark.parametrize(
    "cli",
    [
        (MultiDiffCli,),
        (MultiCli, MultiDiffCli),
        (ScinoephileCli, MultiCli, MultiDiffCli),
    ],
)
def test_multi_diff_help(cli: tuple[type[CommandLineInterface], ...]):
    """Test multi diff CLI help output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_help(cli)


@pytest.mark.parametrize(
    "cli",
    [
        (MultiDiffCli,),
        (MultiCli, MultiDiffCli),
        (ScinoephileCli, MultiCli, MultiDiffCli),
    ],
)
def test_multi_diff_usage(cli: tuple[type[CommandLineInterface], ...]):
    """Test multi diff CLI usage output.

    Arguments:
        cli: CLI class tuple with optional subcommands
    """
    assert_cli_usage(cli)


def test_multi_diff_cli(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
):
    """Test multi diff CLI output.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    reference_infile_path = tmp_path / "reference.srt"
    candidate_infile_path = tmp_path / "candidate.srt"
    reference_infile_path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\n靠你了\n",
        encoding="utf-8",
    )
    candidate_infile_path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\n靠你喇！\n",
        encoding="utf-8",
    )

    run_cli_with_args(
        MultiDiffCli,
        f"--reference-infile {reference_infile_path} "
        f"--candidate-infile {candidate_infile_path} "
        "--reference-label REFERENCE --candidate-label CANDIDATE",
    )
    output = capsys.readouterr().out

    assert output == ("edit: REFERENCE[1] -> CANDIDATE[1]: '靠你了' -> '靠你喇！'\n")


def test_multi_diff_cli_multiline_split_edit(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
):
    """Test multi diff CLI output for multi-line alignment.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    reference_infile_path = tmp_path / "reference.srt"
    candidate_infile_path = tmp_path / "candidate.srt"
    reference_infile_path.write_text(
        "1\n00:00:00,000 --> 00:00:02,000\nalpha beta\n",
        encoding="utf-8",
    )
    candidate_infile_path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\nalpha\n\n"
        "2\n00:00:01,000 --> 00:00:02,000\nbetx\n",
        encoding="utf-8",
    )

    run_cli_with_args(
        MultiDiffCli,
        f"--reference-infile {reference_infile_path} "
        f"--candidate-infile {candidate_infile_path} "
        "--reference-label REFERENCE --candidate-label CANDIDATE",
    )
    output = capsys.readouterr().out

    assert output == (
        "split_edit: REFERENCE[1] -> CANDIDATE[1-2]: "
        "['alpha beta'] -> ['alpha', 'betx']\n"
    )


def test_multi_diff_cli_identical_series_prints_no_differences(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
):
    """Test multi diff reports when there are no differences.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    reference_infile_path = tmp_path / "reference.srt"
    candidate_infile_path = tmp_path / "candidate.srt"
    content = "1\n00:00:00,000 --> 00:00:01,000\n靠你了\n"
    reference_infile_path.write_text(content, encoding="utf-8")
    candidate_infile_path.write_text(content, encoding="utf-8")

    run_cli_with_args(
        MultiDiffCli,
        f"--reference-infile {reference_infile_path} "
        f"--candidate-infile {candidate_infile_path}",
    )
    output = capsys.readouterr().out

    assert output == "No differences found.\n"


def test_multi_diff_cli_rejects_old_one_two_flags(tmp_path: Path):
    """Test multi diff rejects the old one/two flags."""
    reference_infile_path = tmp_path / "reference.srt"
    candidate_infile_path = tmp_path / "candidate.srt"
    content = "1\n00:00:00,000 --> 00:00:01,000\n靠你了\n"
    reference_infile_path.write_text(content, encoding="utf-8")
    candidate_infile_path.write_text(content, encoding="utf-8")

    with pytest.raises(SystemExit, match="2"):
        run_cli_with_args(
            MultiDiffCli,
            f"--one-infile {reference_infile_path} "
            f"--two-infile {candidate_infile_path}",
        )


@pytest.mark.parametrize(
    (
        "reference_path",
        "candidate_path",
        "reference_label",
        "candidate_label",
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
            Path("mlamd/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"),
            Path(
                "mlamd/output/"
                "zho-Hant_ocr/"
                "fuse_clean_validate_review_flatten_simplify_review.srt"
            ),
            "SIMP",
            "TRAD",
            "mlamd_zho_simplify_expected_series_diff",
        ),
        (
            Path("mnt/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"),
            Path(
                "mnt/output/"
                "zho-Hant_ocr/"
                "fuse_clean_validate_review_flatten_simplify_review.srt"
            ),
            "SIMP",
            "TRAD",
            "mnt_zho_simplify_expected_series_diff",
        ),
        (
            Path("t/output/zho-Hans_ocr/fuse_clean_validate_review_flatten.srt"),
            Path(
                "t/output/"
                "zho-Hant_ocr/"
                "fuse_clean_validate_review_flatten_simplify_review.srt"
            ),
            "SIMP",
            "TRAD",
            "t_zho_simplify_expected_series_diff",
        ),
    ],
)
def test_multi_diff_cli_matches_expected_fixture(
    reference_path: Path,
    candidate_path: Path,
    reference_label: str,
    candidate_label: str,
    expected_fixture_name: str,
    capsys: pytest.CaptureFixture,
    request: pytest.FixtureRequest,
):
    """Test multi diff CLI output against real subtitle fixtures.

    Arguments:
        reference_path: reference subtitle path relative to test data root
        candidate_path: candidate subtitle path relative to test data root
        reference_label: label for the reference subtitle series
        candidate_label: label for the candidate subtitle series
        expected_fixture_name: fixture name containing expected diff strings
        capsys: pytest stdout/stderr capture fixture
        request: pytest fixture request object
    """
    expected: list[str] = request.getfixturevalue(expected_fixture_name)

    run_cli_with_args(
        MultiDiffCli,
        f"--reference-infile {test_data_root / reference_path} "
        f"--candidate-infile {test_data_root / candidate_path} "
        f"--reference-label {reference_label} --candidate-label {candidate_label}",
    )
    output = capsys.readouterr().out

    assert output.splitlines() == expected
