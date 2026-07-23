#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for the aligned-diff audit command-line interface."""

from __future__ import annotations

from pathlib import Path

from pytest import CaptureFixture

from scinoephile.analysis.audit.aligned_diff import AlignedDiffAuditFilter
from scinoephile.cli.audit.audit_aligned_diff_cli import AuditAlignedDiffCli
from scinoephile.common.argument_parsing import enum_metavar, enum_options_list_str
from scinoephile.common.testing import run_cli_with_args


def test_audit_aligned_diff_cli_filter_help_is_consistent():
    """Test filter validation, metavar, and help derive from the filter enum."""
    actions = {
        action.dest: action
        for action in AuditAlignedDiffCli.argparser()._actions  # noqa: SLF001
    }
    action = actions["row_filter"]

    assert action.choices is None
    assert action.default is AlignedDiffAuditFilter.changes
    assert action.metavar == enum_metavar(AlignedDiffAuditFilter)
    assert isinstance(action.help, str)
    assert enum_options_list_str(AlignedDiffAuditFilter) in action.help
    assert "all includes every aligned row" in action.help
    assert "changes includes differing rows" in action.help


def test_audit_aligned_diff_cli_track_help_describes_alignment():
    """Test ancillary-track help distinguishes timing overlap from alignment."""
    actions = {
        action.dest: action
        for action in AuditAlignedDiffCli.argparser()._actions  # noqa: SLF001
    }

    assert (
        actions["original_path"].help
        == "optional original subtitle SRT file matched by timing overlap"
    )
    assert (
        actions["guide_path"].help
        == "optional guide subtitle SRT file aligned with the transcription"
    )


def test_audit_aligned_diff_cli_writes_report(
    tmp_path: Path,
    capsys: CaptureFixture,
):
    """Test aligned diff audit output to stdout and a file.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    transcription_path = tmp_path / "transcription.srt"
    reference_path = tmp_path / "reference.srt"
    _write_srt(transcription_path, ("甲錯", "相同"))
    _write_srt(reference_path, ("甲正", "相同"))
    arguments = (
        f"--transcription {transcription_path} --reference {reference_path} "
        "--first-index 1 --last-index 1"
    )

    run_cli_with_args(AuditAlignedDiffCli, arguments)
    stdout = capsys.readouterr().out
    assert stdout.startswith("# Aligned Subtitle Diff Audit\n")
    assert "- transcription subtitle range: 1 through 1" in stdout
    assert "| T 1<br>R 1 | <pre>T │ 甲錯<br>R │ 甲正</pre> |  |" in stdout

    outfile_path = tmp_path / "audit.md"
    run_cli_with_args(
        AuditAlignedDiffCli,
        f"{arguments} --outfile {outfile_path}",
    )
    assert capsys.readouterr().out == ""
    assert outfile_path.read_text(encoding="utf-8") == stdout


def _write_srt(file_path: Path, texts: tuple[str, ...]):
    """Write subtitle text to a simple SRT fixture.

    Arguments:
        file_path: output SRT path
        texts: subtitle text by event
    """
    blocks = [
        f"{index}\n00:00:{index:02d},000 --> 00:00:{index:02d},500\n{text}"
        for index, text in enumerate(texts, 1)
    ]
    file_path.write_text(f"{'\n\n'.join(blocks)}\n", encoding="utf-8")
