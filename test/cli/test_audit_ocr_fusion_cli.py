#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for the OCR-fusion audit command-line interface."""

from __future__ import annotations

import json
from pathlib import Path

from pytest import CaptureFixture, raises

from scinoephile.cli.audit.audit_ocr_fusion_cli import AuditOcrFusionCli
from scinoephile.common.testing import run_cli_with_args


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

    run_cli_with_args(
        AuditOcrFusionCli,
        f"--source-one {source_one_path} --source-two {source_two_path} "
        f"--fused {fused_path}",
    )
    report = capsys.readouterr().out
    assert "- decision log: omitted" in report
    assert (
        "| Index | Case | Difficulty | Source one | Source two | Fused | Validated |"
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
