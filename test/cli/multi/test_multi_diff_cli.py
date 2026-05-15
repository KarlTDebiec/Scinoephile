#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the multi diff CLI."""

from __future__ import annotations

from pathlib import Path

import pytest

from scinoephile.cli.multi.multi_diff_cli import MultiDiffCli
from scinoephile.common.testing import run_cli_with_args


def test_multi_diff_cli(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
):
    """Test multi diff CLI output.

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
        MultiDiffCli,
        f"--one-infile {one_infile_path} --two-infile {two_infile_path} "
        "--one-label TRANSCRIBE --two-label REFERENCE",
    )
    output = capsys.readouterr().out

    assert output == ("edit: TRANSCRIBE[1] -> REFERENCE[1]: '靠你了' -> '靠你喇！'\n")


def test_multi_diff_cli_multiline_split_edit(
    tmp_path: Path,
    capsys: pytest.CaptureFixture,
):
    """Test multi diff CLI output for multi-line alignment.

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
        MultiDiffCli,
        f"--one-infile {one_infile_path} --two-infile {two_infile_path} "
        "--one-label TRANSCRIBE --two-label REFERENCE",
    )
    output = capsys.readouterr().out

    assert output == (
        "split_edit: TRANSCRIBE[1] -> REFERENCE[1-2]: "
        "['alpha beta'] -> ['alpha', 'betx']\n"
    )
