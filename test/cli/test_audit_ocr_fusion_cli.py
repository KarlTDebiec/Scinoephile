#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for the OCR-fusion audit command-line interface."""

from __future__ import annotations

import json
from pathlib import Path

from pytest import CaptureFixture, raises

from scinoephile.analysis.audit.ocr_fusion import OcrFusionAuditFilter
from scinoephile.cli.audit.audit_ocr_fusion_cli import AuditOcrFusionCli
from scinoephile.common.argument_parsing import enum_metavar, enum_options_list_str
from scinoephile.common.testing import run_cli_with_args


def test_audit_ocr_fusion_cli_filter_help_is_consistent():
    """Test filter validation, metavar, and help derive from the filter enum."""
    action = next(
        action
        for action in AuditOcrFusionCli.argparser()._actions  # noqa: SLF001
        if action.dest == "row_filter"
    )

    assert action.choices is None
    assert action.metavar == enum_metavar(OcrFusionAuditFilter)
    assert isinstance(action.help, str)
    assert enum_options_list_str(OcrFusionAuditFilter) in action.help


def test_audit_ocr_fusion_cli_writes_validated_discrepancy_report(
    tmp_path: Path,
    capsys: CaptureFixture,
):
    """Test OCR-fusion audits write reports to stdout and explicit files.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    source_one_path = tmp_path / "one.srt"
    source_two_path = tmp_path / "two.srt"
    fused_path = tmp_path / "fused.srt"
    validated_path = tmp_path / "validated.srt"
    json_path = tmp_path / "ocr_fusion.json"
    _write_srt(source_one_path, "甲錯")
    _write_srt(source_two_path, "甲正")
    _write_srt(fused_path, "甲正")
    _write_srt(validated_path, "甲真")
    json_path.write_text(
        json.dumps(
            [
                {
                    "query": {"one": "甲錯", "two": "甲正"},
                    "answer": {"output": "甲正", "note": "Used source two."},
                    "difficulty": 2,
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    arguments = (
        f"--source-one {source_one_path} --source-two {source_two_path} "
        f"--fused {fused_path} --validated {validated_path} --json {json_path}"
    )

    run_cli_with_args(AuditOcrFusionCli, f"{arguments} --filter discrepancies")

    report = capsys.readouterr().out
    assert report.startswith("# OCR Fusion Audit\n")
    assert "- validated discrepancies: 1" in report
    assert "| 1 | 1 | 2 | 甲錯 | 甲正 | 甲正 | 甲真 |" in report

    with raises(SystemExit):
        run_cli_with_args(
            AuditOcrFusionCli,
            f"{arguments} --first-index 1 --first-block 1",
        )
    assert "mutually exclusive" in capsys.readouterr().err

    outfile_path = tmp_path / "audit.md"
    run_cli_with_args(
        AuditOcrFusionCli,
        f"{arguments} --outfile {outfile_path}",
    )
    assert capsys.readouterr().out == ""
    assert outfile_path.read_text(encoding="utf-8").startswith("# OCR Fusion Audit\n")

    with raises(SystemExit):
        run_cli_with_args(
            AuditOcrFusionCli,
            f"{arguments} --outfile {outfile_path}",
        )
    assert "File exists" in capsys.readouterr().err

    run_cli_with_args(
        AuditOcrFusionCli,
        f"{arguments} --outfile {outfile_path} --overwrite",
    )
    assert capsys.readouterr().out == ""

    no_json_arguments = (
        f"--source-one {source_one_path} --source-two {source_two_path} "
        f"--fused {fused_path}"
    )
    with raises(SystemExit):
        run_cli_with_args(
            AuditOcrFusionCli,
            f"{no_json_arguments} --filter unverified",
        )
    assert "--filter unverified requires --json" in capsys.readouterr().err

    with raises(SystemExit):
        run_cli_with_args(
            AuditOcrFusionCli,
            f"{no_json_arguments} --filter discrepancies",
        )
    assert "--filter discrepancies requires --validated" in capsys.readouterr().err

    run_cli_with_args(
        AuditOcrFusionCli,
        no_json_arguments,
    )
    report = capsys.readouterr().out
    assert "- decision log: omitted" in report
    assert (
        "| Subtitle | Case | Difficulty | Source one | Source two | Fused | Validated |"
        in report
    )


def _write_srt(file_path: Path, text: str):
    """Write one subtitle to an SRT file.

    Arguments:
        file_path: output SRT path
        text: subtitle text
    """
    file_path.write_text(
        f"1\n00:00:00,000 --> 00:00:00,500\n{text}\n",
        encoding="utf-8",
    )
