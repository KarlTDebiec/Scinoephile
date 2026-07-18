#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the subtitle audit CLI."""

from __future__ import annotations

import json
from pathlib import Path

from pytest import CaptureFixture, mark, raises

from scinoephile.cli.audit import AuditCli
from scinoephile.cli.audit.audit_aligned_diff_cli import AuditAlignedDiffCli
from scinoephile.cli.audit.audit_delineation_cli import AuditDelineationCli
from scinoephile.cli.audit.audit_guided_review_cli import AuditGuidedReviewCli
from scinoephile.cli.audit.audit_punctuation_cli import AuditPunctuationCli
from scinoephile.cli.audit.audit_review_cli import AuditReviewCli
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
        run_cli_with_args(
            AuditReviewDualCli,
            f"{arguments} --first-index 2 --last-index 1",
        )
    assert "--first-index must be less than or equal to --last-index" in (
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
    assert ScinoephileCli.subcommands()["audit"] is AuditCli
    assert AuditCli.subcommands() == {
        "aligned-diff": AuditAlignedDiffCli,
        "delineation": AuditDelineationCli,
        "guided-review": AuditGuidedReviewCli,
        "punctuation": AuditPunctuationCli,
        "review": AuditReviewCli,
        "review-dual": AuditReviewDualCli,
        "review-trad": AuditReviewTradCli,
    }


def test_audit_aligned_diff_cli_stdout_outfile_and_validation(
    tmp_path: Path,
    capsys: CaptureFixture,
):
    """Test aligned-diff audit output and range validation.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    original_path = tmp_path / "original.srt"
    transcription_path = tmp_path / "transcription.srt"
    reference_path = tmp_path / "reference.srt"
    guide_path = tmp_path / "guide.srt"
    _write_srt(original_path, ("甲原", "相同"))
    _write_srt(transcription_path, ("甲錯", "相同"))
    _write_srt(reference_path, ("甲正", "相同"))
    _write_srt(guide_path, ("指南一", "指南二"))
    arguments = (
        f"--original {original_path} --transcription {transcription_path} "
        f"--reference {reference_path} --guide {guide_path}"
    )

    run_cli_with_args(
        AuditAlignedDiffCli,
        f"{arguments} --first-index 1 --last-index 1",
    )
    stdout = capsys.readouterr().out
    assert stdout.startswith("# Aligned Subtitle Diff Audit\n")
    assert "- transcription subtitle range: 1 through 1" in stdout
    assert "- row filter: changes" in stdout
    assert "<pre>O │ 甲原<br>T │ 甲錯<br>R │ 甲正<br>G │ 指南一</pre>" in stdout

    outfile_path = tmp_path / "audit.md"
    run_cli_with_args(
        AuditAlignedDiffCli,
        f"{arguments} --filter all --outfile {outfile_path}",
    )
    assert capsys.readouterr().out == ""
    report = outfile_path.read_text(encoding="utf-8")
    assert "- row filter: all" in report
    assert "- table rows: 2" in report

    with raises(SystemExit):
        run_cli_with_args(
            AuditAlignedDiffCli,
            f"{arguments} --first-index 2 --last-index 1",
        )
    assert "--first-index must be less than or equal to --last-index" in (
        capsys.readouterr().err
    )


def test_audit_guided_review_cli_stdout_and_outfile(
    tmp_path: Path,
    capsys: CaptureFixture,
):
    """Test guided-review audit output to stdout and a file.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    target_path = tmp_path / "target.srt"
    guide_path = tmp_path / "guide.srt"
    _write_srt(target_path, ("原文",))
    _write_srt(guide_path, ("參考",))
    json_path = tmp_path / "guided_review.json"
    json_path.write_text(
        json.dumps(
            [
                {
                    "query": {
                        "targets": [{"index": 1, "text": "原文"}],
                        "guides": [{"index": 1, "text": "參考"}],
                    },
                    "answer": {
                        "revisions": [
                            {
                                "index": 1,
                                "text": "修訂",
                                "note": "correction",
                            }
                        ]
                    },
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    arguments = f"--target {target_path} --guide {guide_path} --json {json_path}"

    run_cli_with_args(
        AuditGuidedReviewCli,
        f"{arguments} --first-index 1 --last-index 1 --filter changes",
    )
    stdout = capsys.readouterr().out
    assert stdout.startswith("# Guided Subtitle Review Audit\n")
    assert "- row filter: changes" in stdout
    assert "- target subtitle range: 1 through 1" in stdout
    assert "- subtitles: 1" in stdout
    assert "| 1 | 1 | 參考 | 原文<br>修訂 |  |  |" in stdout

    outfile_path = tmp_path / "audit.md"
    run_cli_with_args(
        AuditGuidedReviewCli,
        f"{arguments} --outfile {outfile_path}",
    )
    assert capsys.readouterr().out == ""
    assert outfile_path.read_text(encoding="utf-8").startswith(
        "# Guided Subtitle Review Audit\n"
    )

    with raises(SystemExit):
        run_cli_with_args(
            AuditGuidedReviewCli,
            f"{arguments} --first-index 2 --last-index 1",
        )
    assert "--first-index must be less than or equal to --last-index" in (
        capsys.readouterr().err
    )


def test_audit_delineation_cli_stdout_and_outfile(
    tmp_path: Path,
    capsys: CaptureFixture,
):
    """Test delineation audit output to stdout and a file.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    reference_path = tmp_path / "reference.srt"
    _write_srt(reference_path, ("參考一", "參考二"))
    json_path = tmp_path / "delineation.json"
    json_path.write_text(
        json.dumps(
            [
                {
                    "query": {
                        "ref_sub_1": "參考一",
                        "ref_sub_2": "參考二",
                        "target_sub_1": "甲乙",
                        "target_sub_2": "丙",
                    },
                    "answer": {
                        "target_sub_1_shifted": "甲",
                        "target_sub_2_shifted": "乙丙",
                    },
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    arguments = f"--reference {reference_path} --json {json_path}"

    run_cli_with_args(
        AuditDelineationCli,
        f"{arguments} --first-index 1 --last-index 2 --filter changes",
    )
    stdout = capsys.readouterr().out
    assert stdout.startswith("# Transcription Delineation Audit\n")
    assert "- row filter: changes" in stdout
    assert "- subtitle range: 1-indexed numbers 1 through 2" in stdout
    assert "| 1<br>2 | 參考一<br>參考二 | 甲乙<br>丙 | 甲<br>乙丙 |" in stdout

    outfile_path = tmp_path / "audit.md"
    run_cli_with_args(
        AuditDelineationCli,
        f"{arguments} --outfile {outfile_path}",
    )
    assert capsys.readouterr().out == ""
    assert outfile_path.read_text(encoding="utf-8").startswith(
        "# Transcription Delineation Audit\n"
    )

    with raises(SystemExit):
        run_cli_with_args(
            AuditDelineationCli,
            f"{arguments} --first-index 2 --last-index 1",
        )
    assert "--first-index must be less than or equal to --last-index" in (
        capsys.readouterr().err
    )


def test_audit_punctuation_cli_stdout_and_outfile(
    tmp_path: Path,
    capsys: CaptureFixture,
):
    """Test punctuation audit output to stdout and a file.

    Arguments:
        tmp_path: temporary path
        capsys: pytest stdout/stderr capture fixture
    """
    reference_path = tmp_path / "reference.srt"
    target_path = tmp_path / "target.srt"
    _write_srt(reference_path, ("參考",))
    _write_srt(target_path, ("甲，乙",))
    json_path = tmp_path / "punctuation.json"
    json_path.write_text(
        json.dumps(
            [
                {
                    "query": {
                        "ref_sub": "參考",
                        "target_subs": ["甲", "乙"],
                    },
                    "answer": {"target_sub_punctuated": "甲，乙"},
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    arguments = (
        f"--reference {reference_path} --target {target_path} --json {json_path}"
    )

    run_cli_with_args(
        AuditPunctuationCli,
        f"{arguments} --first-index 1 --last-index 1 --filter changes",
    )
    stdout = capsys.readouterr().out
    assert stdout.startswith("# Transcription Punctuation Audit\n")
    assert "- row filter: changes" in stdout
    assert "- subtitle range: 1-indexed numbers 1 through 1" in stdout
    assert "| 1 | 參考 | 甲<br>乙 | 甲，乙 |" in stdout

    outfile_path = tmp_path / "audit.md"
    run_cli_with_args(
        AuditPunctuationCli,
        f"{arguments} --outfile {outfile_path}",
    )
    assert capsys.readouterr().out == ""
    assert outfile_path.read_text(encoding="utf-8").startswith(
        "# Transcription Punctuation Audit\n"
    )

    with raises(SystemExit):
        run_cli_with_args(
            AuditPunctuationCli,
            f"{arguments} --first-index 2 --last-index 1",
        )
    assert "--first-index must be less than or equal to --last-index" in (
        capsys.readouterr().err
    )


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
