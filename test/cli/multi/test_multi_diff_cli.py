#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the multi diff CLI."""

from __future__ import annotations

from pathlib import Path

from pytest import CaptureFixture, raises

from scinoephile.cli.multi.multi_diff_cli import MultiDiffCli
from scinoephile.common.testing import run_cli_with_args


def test_multi_diff_cli(tmp_path: Path, capsys: CaptureFixture):
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


def test_multi_diff_cli_multiline_split_edit(tmp_path: Path, capsys: CaptureFixture):
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
    capsys: CaptureFixture,
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
    """Test multi diff rejects the old one/two flags.

    Arguments:
        tmp_path: temporary path
    """
    reference_infile_path = tmp_path / "reference.srt"
    candidate_infile_path = tmp_path / "candidate.srt"
    content = "1\n00:00:00,000 --> 00:00:01,000\n靠你了\n"
    reference_infile_path.write_text(content, encoding="utf-8")
    candidate_infile_path.write_text(content, encoding="utf-8")

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            MultiDiffCli,
            f"--one-infile {reference_infile_path} "
            f"--two-infile {candidate_infile_path}",
        )
