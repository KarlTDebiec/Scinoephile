#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the multi cer CLI."""

from __future__ import annotations

from pathlib import Path

from pytest import CaptureFixture

from scinoephile.cli.multi.multi_cer_cli import MultiCerCli
from scinoephile.common.testing import run_cli_with_args


def test_multi_cer_cli(tmp_path: Path, capsys: CaptureFixture[str]):
    """Test multi cer CLI output.

    Arguments:
        tmp_path: temporary path fixture
        capsys: pytest stdout/stderr capture fixture
    """
    reference_infile_path = tmp_path / "reference.srt"
    candidate_infile_path = tmp_path / "candidate.srt"
    reference_infile_path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\nabc\n",
        encoding="utf-8",
    )
    candidate_infile_path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\naxc\n",
        encoding="utf-8",
    )

    run_cli_with_args(
        MultiCerCli,
        f"--reference-infile {reference_infile_path} "
        f"--candidate-infile {candidate_infile_path}",
    )
    output = capsys.readouterr().out

    assert "CER: 0.3333333333333333" in output
    assert "Correct: 2" in output
    assert "Substitutions: 1" in output
    assert "Insertions: 0" in output
    assert "Deletions: 0" in output
    assert "Reference length: 3" in output
