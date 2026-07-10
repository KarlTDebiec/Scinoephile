#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the subtitle review audit CLI."""

from __future__ import annotations

from pathlib import Path

from pytest import CaptureFixture

from scinoephile.cli.audit_cli import AuditCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common.testing import run_cli_with_args


def test_audit_cli_stdout_and_outfile(tmp_path: Path, capsys: CaptureFixture):
    """Test audit reports can be printed or written to Markdown.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    original_path = tmp_path / "original.srt"
    reviewed_path = tmp_path / "reviewed.srt"
    original_path.write_text(
        "1\n00:00:01,000 --> 00:00:01,500\n錯\n",
        encoding="utf-8",
    )
    reviewed_path.write_text(
        "1\n00:00:01,000 --> 00:00:01,500\n正\n",
        encoding="utf-8",
    )
    arguments = (
        f"--traditional {original_path} "
        f"--traditional-reviewed {reviewed_path} "
        f"--traditional-simplified {reviewed_path} "
        f"--traditional-simplified-reviewed {reviewed_path} "
        f"--simplified {reviewed_path} "
        f"--simplified-reviewed {reviewed_path}"
    )

    run_cli_with_args(AuditCli, f"{arguments} --first-index 1 --last-index 1")
    stdout = capsys.readouterr().out
    assert stdout.startswith("# Review Audit\n")
    assert "- subtitle range: 1-indexed numbers 1 through 1" in stdout
    assert "- table rows: 1" in stdout

    outfile_path = tmp_path / "audit.md"
    run_cli_with_args(AuditCli, f"{arguments} --outfile {outfile_path}")
    assert capsys.readouterr().out == ""
    assert outfile_path.read_text(encoding="utf-8").startswith("# Review Audit\n")


def test_audit_cli_is_top_level_subcommand():
    """Test the audit CLI is registered as a top-level command."""
    assert ScinoephileCli.subcommands()["audit"] is AuditCli
