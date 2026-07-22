#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the subtitle audit CLI."""

from __future__ import annotations

import json
from pathlib import Path

from pytest import CaptureFixture, mark, raises

from scinoephile.cli.audit import AuditCli
from scinoephile.cli.audit.audit_cli_base import AuditCliBase
from scinoephile.cli.audit.audit_review_cli import AuditReviewCli
from scinoephile.cli.audit.audit_review_cli_base import AuditReviewCliBase
from scinoephile.cli.audit.audit_review_dual_cli import AuditReviewDualCli
from scinoephile.cli.audit.audit_review_trad_cli import AuditReviewTradCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common.testing import run_cli_with_args


def test_audit_review_dual_cli_stdout_outfile_and_validation(
    tmp_path: Path,
    capsys: CaptureFixture,
):
    """Test audit output and input validation.

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

    run_cli_with_args(
        AuditReviewDualCli,
        f"{arguments} --first-index 1 --last-index 1",
    )
    stdout = capsys.readouterr().out
    assert stdout.startswith("# Review Audit\n")
    assert "- subtitle range: 1-indexed numbers 1 through 1" in stdout
    assert "- table rows: 1" in stdout

    run_cli_with_args(
        AuditReviewDualCli,
        f"{arguments} --first-block 1 --last-block 1",
    )
    assert "- block range: 1 through 1" in capsys.readouterr().out

    run_cli_with_args(AuditReviewDualCli, f"{arguments} --characters 错这")
    stdout = capsys.readouterr().out
    assert "- character filter: 这, 這, 錯, 错" in stdout
    assert "- table rows: 1" in stdout

    review_json_path = tmp_path / "review.json"
    review_json_path.write_text(
        json.dumps(
            [
                {
                    "query": {"subtitles": [{"index": 1, "text": "錯"}]},
                    "answer": {
                        "revisions": [{"index": 1, "text": "正", "note": "修正。"}]
                    },
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    run_cli_with_args(
        AuditReviewDualCli,
        f"{arguments} --traditional-json {review_json_path}",
    )
    assert "Traditional review: 修正。" in capsys.readouterr().out

    outfile_path = tmp_path / "audit.md"
    run_cli_with_args(AuditReviewDualCli, f"{arguments} --outfile {outfile_path}")
    assert capsys.readouterr().out == ""
    assert outfile_path.read_text(encoding="utf-8").startswith("# Review Audit\n")

    with raises(SystemExit):
        run_cli_with_args(AuditReviewDualCli, f"{arguments} --outfile {outfile_path}")
    assert "use --overwrite to replace it" in capsys.readouterr().err

    run_cli_with_args(
        AuditReviewDualCli,
        f"{arguments} --outfile {outfile_path} --overwrite",
    )
    assert capsys.readouterr().out == ""

    with raises(SystemExit):
        run_cli_with_args(AuditReviewDualCli, f"{arguments} --overwrite")
    assert "--overwrite may only be used with --outfile" in capsys.readouterr().err

    with raises(SystemExit):
        run_cli_with_args(
            AuditReviewDualCli,
            f"{arguments} --first-index 2 --last-index 1",
        )
    assert "First index must be less than or equal to last index" in (
        capsys.readouterr().err
    )

    with raises(SystemExit):
        run_cli_with_args(
            AuditReviewDualCli,
            f"{arguments} --first-index 1 --first-block 1",
        )
    assert "Subtitle-index and block ranges are mutually exclusive" in (
        capsys.readouterr().err
    )

    reviewed_path.write_text(
        reviewed_path.read_text(encoding="utf-8")
        + "\n2\n00:00:02,000 --> 00:00:02,500\n又\n",
        encoding="utf-8",
    )
    with raises(SystemExit):
        run_cli_with_args(AuditReviewDualCli, arguments)
    assert "Subtitle inputs must contain the same number of subtitles" in (
        capsys.readouterr().err
    )


def test_audit_cli_subcommands():
    """Test the audit CLI and its workflow subcommands are registered."""
    assert issubclass(AuditReviewCliBase, AuditCliBase)
    assert ScinoephileCli.subcommands()["audit"] is AuditCli
    assert AuditCli.subcommands() == {
        "review": AuditReviewCli,
        "review-dual": AuditReviewDualCli,
        "review-trad": AuditReviewTradCli,
    }


def test_audit_review_cli_detects_language(tmp_path: Path, capsys: CaptureFixture):
    """Test a single review audit detects its language.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    original_path = tmp_path / "original.srt"
    reviewed_path = tmp_path / "reviewed.srt"
    original_path.write_text(
        "1\n00:00:01,000 --> 00:00:01,500\nThis line needs work.\n\n"
        "2\n00:00:02,000 --> 00:00:02,500\nThis line is fine.\n\n"
        "3\n00:00:03,000 --> 00:00:03,500\nAnother English subtitle.\n",
        encoding="utf-8",
    )
    reviewed_path.write_text(
        "1\n00:00:01,000 --> 00:00:01,500\nThis line is improved.\n\n"
        "2\n00:00:02,000 --> 00:00:02,500\nThis line is fine.\n\n"
        "3\n00:00:03,000 --> 00:00:03,500\nAnother English subtitle.\n",
        encoding="utf-8",
    )

    run_cli_with_args(
        AuditReviewCli,
        f"--original {original_path} --reviewed {reviewed_path}",
    )

    stdout = capsys.readouterr().out
    assert "- english review edits: 1" in stdout
    assert "| Subtitle | English | Notes |" in stdout
    assert "| 1 | This line needs work.<br>This line is improved. |" in stdout


def test_audit_review_trad_cli(tmp_path: Path, capsys: CaptureFixture):
    """Test a traditional-to-simplified two-review audit.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    traditional_path = tmp_path / "traditional.srt"
    traditional_reviewed_path = tmp_path / "traditional_reviewed.srt"
    simplified_path = tmp_path / "simplified.srt"
    simplified_reviewed_path = tmp_path / "simplified_reviewed.srt"
    traditional_path.write_text(
        "1\n00:00:01,000 --> 00:00:01,500\n傳錯\n",
        encoding="utf-8",
    )
    traditional_reviewed_path.write_text(
        "1\n00:00:01,000 --> 00:00:01,500\n傳正\n",
        encoding="utf-8",
    )
    simplified_path.write_text(
        "1\n00:00:01,000 --> 00:00:01,500\n传错\n",
        encoding="utf-8",
    )
    simplified_reviewed_path.write_text(
        "1\n00:00:01,000 --> 00:00:01,500\n传正\n",
        encoding="utf-8",
    )

    run_cli_with_args(
        AuditReviewTradCli,
        f"--traditional {traditional_path} "
        f"--traditional-reviewed {traditional_reviewed_path} "
        f"--traditional-simplified {simplified_path} "
        f"--traditional-simplified-reviewed {simplified_reviewed_path}",
    )

    stdout = capsys.readouterr().out
    assert "- traditional review edits: 1" in stdout
    assert "- traditional simplification review edits: 1" in stdout
    assert "| Subtitle | Traditional | Traditional simplification | Notes |" in stdout


@mark.parametrize(
    ("texts", "label"),
    (
        (
            ("他们正在这里", "我们没有这个东西", "她说这是真的吗"),
            "Simplified Chinese",
        ),
        (
            ("他們正在這裡", "我們沒有這個東西", "她說這是真的嗎"),
            "Traditional Chinese",
        ),
        (
            ("我唔知点解你冇这个", "佢哋系咪想睇这个", "咁样冇嘢喺这边"),
            "Simplified Cantonese",
        ),
        (
            ("我唔知點解你冇這個", "佢哋係咪想睇這個", "咁樣冇嘢喺這邊"),
            "Traditional Cantonese",
        ),
    ),
)
def test_audit_review_cli_detects_chinese_language_and_script(
    tmp_path: Path,
    capsys: CaptureFixture,
    texts: tuple[str, ...],
    label: str,
):
    """Test single reviews detect Chinese language and script combinations.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
        texts: original subtitle text
        label: expected report label
    """
    original_path = tmp_path / "original.srt"
    reviewed_path = tmp_path / "reviewed.srt"
    _write_srt(original_path, texts)
    _write_srt(reviewed_path, (f"{texts[0]}！", *texts[1:]))

    run_cli_with_args(
        AuditReviewCli,
        f"--original {original_path} --reviewed {reviewed_path}",
    )

    stdout = capsys.readouterr().out
    assert f"- {label.lower()} review edits: 1" in stdout
    assert f"| Subtitle | {label} | Notes |" in stdout


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
