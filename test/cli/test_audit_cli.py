#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of the subtitle audit CLI."""

from __future__ import annotations

import json
from pathlib import Path

from pytest import CaptureFixture, mark, raises

from scinoephile.analysis.audit.review import ComparativeReviewAuditFilter
from scinoephile.analysis.audit.utils import AuditFilter
from scinoephile.cli.audit import AuditCli
from scinoephile.cli.audit.audit_aligned_diff_cli import AuditAlignedDiffCli
from scinoephile.cli.audit.audit_cli_base import AuditCliBase
from scinoephile.cli.audit.audit_delineation_cli import AuditDelineationCli
from scinoephile.cli.audit.audit_ocr_fusion_cli import AuditOcrFusionCli
from scinoephile.cli.audit.audit_punctuation_cli import AuditPunctuationCli
from scinoephile.cli.audit.audit_review_cli import AuditReviewCli
from scinoephile.cli.audit.audit_review_dual_cli import AuditReviewDualCli
from scinoephile.cli.audit.audit_review_trad_cli import AuditReviewTradCli
from scinoephile.cli.audit.audit_translation_cli import AuditTranslationCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common.argument_parsing import enum_metavar, enum_options_list_str
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
    assert "- subtitle range: 1 through 1" in stdout
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
    unchanged_review_json_path = tmp_path / "unchanged_review.json"
    unchanged_review_json_path.write_text(
        json.dumps(
            [
                {
                    "query": {"subtitles": [{"index": 1, "text": "正"}]},
                    "answer": {"revisions": []},
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    run_cli_with_args(
        AuditReviewDualCli,
        (
            f"{arguments} --simplified-json {unchanged_review_json_path} "
            f"--traditional-json {review_json_path} "
            f"--traditional-simplified-json {unchanged_review_json_path} "
            "--filter unverified"
        ),
    )
    stdout = capsys.readouterr().out
    assert "- row filter: unverified" in stdout
    assert "Traditional review: 修正。" in stdout

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

    with raises(SystemExit):
        run_cli_with_args(
            AuditReviewDualCli,
            (f"{arguments} --traditional-json {review_json_path} --filter unverified"),
        )
    assert (
        "--filter unverified requires --simplified-json, --traditional-json, and "
        "--traditional-simplified-json"
    ) in (capsys.readouterr().err)

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
    assert issubclass(AuditDelineationCli, AuditCliBase)
    assert issubclass(AuditPunctuationCli, AuditCliBase)
    assert issubclass(AuditReviewCli, AuditCliBase)
    assert issubclass(AuditReviewDualCli, AuditCliBase)
    assert issubclass(AuditReviewTradCli, AuditCliBase)
    assert ScinoephileCli.subcommands()["audit"] is AuditCli
    assert AuditCli.subcommands() == {
        "delineation": AuditDelineationCli,
        "ocr-fusion": AuditOcrFusionCli,
        "punctuation": AuditPunctuationCli,
        "review": AuditReviewCli,
        "review-dual": AuditReviewDualCli,
        "review-trad": AuditReviewTradCli,
        "translation": AuditTranslationCli,
    }


def test_transcription_audit_cli_help_describes_subtitle_indexes():
    """Test transcription audit range help describes subtitle indexes."""
    for cli_class in (AuditDelineationCli, AuditPunctuationCli):
        actions = {
            action.dest: action
            for action in cli_class.argparser()._actions  # noqa: SLF001
        }
        assert actions["first_index"].help == (
            "first 1-indexed subtitle number to include, inclusive"
        )
        assert actions["last_index"].help == (
            "last 1-indexed subtitle number to include, inclusive"
        )


def test_audit_review_cli_help_is_consistent():
    """Test review audit help documents JSON inputs and option defaults."""
    for cli_class in (AuditReviewCli, AuditReviewDualCli, AuditReviewTradCli):
        actions = {
            action.dest: action
            for action in cli_class.argparser()._actions  # noqa: SLF001
        }
        if cli_class is AuditReviewCli:
            assert "mode" not in actions
            assert actions["original_path"].option_strings == ["--original"]
        filter_type = AuditFilter
        if cli_class is AuditReviewDualCli:
            filter_type = ComparativeReviewAuditFilter
        filter_action = actions["row_filter"]
        assert filter_action.choices is None
        assert filter_action.metavar == enum_metavar(filter_type)
        assert isinstance(filter_action.help, str)
        assert enum_options_list_str(filter_type) in filter_action.help
        character_help = actions["characters"].help
        assert isinstance(character_help, str)
        assert "(default: no character filter)" in character_help
        for destination, action in actions.items():
            if destination.endswith("json_path"):
                assert isinstance(action.help, str)
                assert "test-case JSON file" in action.help
                assert "--filter unverified" in action.help


def test_audit_review_cli_guided_mode_stdout_and_outfile(
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
    arguments = f"--original {target_path} --guide {guide_path} --json {json_path}"

    run_cli_with_args(
        AuditReviewCli,
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
        AuditReviewCli,
        f"{arguments} --outfile {outfile_path}",
    )
    assert capsys.readouterr().out == ""
    assert outfile_path.read_text(encoding="utf-8").startswith(
        "# Guided Subtitle Review Audit\n"
    )

    with raises(SystemExit):
        run_cli_with_args(
            AuditReviewCli,
            f"{arguments} --first-index 2 --last-index 1",
        )
    assert "First index must be less than or equal to last index" in (
        capsys.readouterr().err
    )

    with raises(SystemExit):
        run_cli_with_args(
            AuditReviewCli,
            f"{arguments} --first-index 1 --first-block 1",
        )
    assert "mutually exclusive" in capsys.readouterr().err

    with raises(SystemExit):
        run_cli_with_args(
            AuditReviewCli,
            f"{arguments} --reviewed {target_path}",
        )
    assert "not allowed with argument --guide" in capsys.readouterr().err

    with raises(SystemExit):
        run_cli_with_args(
            AuditReviewCli,
            (f"--original {target_path} --guide {guide_path} --filter unverified"),
        )
    assert "--filter unverified requires --json" in capsys.readouterr().err


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

    with raises(SystemExit):
        run_cli_with_args(
            AuditReviewCli,
            (
                f"--original {original_path} --reviewed {reviewed_path} "
                "--filter unverified"
            ),
        )
    assert "--filter unverified requires --json" in capsys.readouterr().err

    json_path = tmp_path / "review.json"
    json_path.write_text(
        json.dumps(
            [
                {
                    "query": {
                        "subtitles": [
                            {"index": 1, "text": "This line needs work."},
                            {"index": 2, "text": "This line is fine."},
                            {"index": 3, "text": "Another English subtitle."},
                        ]
                    },
                    "answer": {
                        "revisions": [
                            {
                                "index": 1,
                                "text": "This line is improved.",
                                "note": "Improved.",
                            }
                        ]
                    },
                }
            ]
        ),
        encoding="utf-8",
    )
    run_cli_with_args(
        AuditReviewCli,
        (
            f"--original {original_path} --reviewed {reviewed_path} "
            f"--json {json_path} --filter unverified"
        ),
    )
    stdout = capsys.readouterr().out
    assert "- row filter: unverified" in stdout
    assert "- table rows: 3" in stdout


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

    arguments = (
        f"--traditional {traditional_path} "
        f"--traditional-reviewed {traditional_reviewed_path} "
        f"--traditional-simplified {simplified_path} "
        f"--traditional-simplified-reviewed {simplified_reviewed_path}"
    )
    run_cli_with_args(AuditReviewTradCli, arguments)

    stdout = capsys.readouterr().out
    assert "- traditional review edits: 1" in stdout
    assert "- traditional simplification review edits: 1" in stdout
    assert "| Subtitle | Traditional | Traditional simplification | Notes |" in stdout

    traditional_json_path = tmp_path / "traditional.json"
    traditional_json_path.write_text(
        json.dumps(
            [
                {
                    "query": {"subtitles": [{"index": 1, "text": "傳錯"}]},
                    "answer": {
                        "revisions": [
                            {"index": 1, "text": "傳正", "note": "繁體修正。"}
                        ]
                    },
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    traditional_simplified_json_path = tmp_path / "traditional_simplified.json"
    traditional_simplified_json_path.write_text(
        json.dumps(
            [
                {
                    "query": {"subtitles": [{"index": 1, "text": "传错"}]},
                    "answer": {
                        "revisions": [
                            {"index": 1, "text": "传正", "note": "简体修正。"}
                        ]
                    },
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    json_arguments = (
        f"--traditional-json {traditional_json_path} "
        f"--traditional-simplified-json {traditional_simplified_json_path}"
    )
    run_cli_with_args(
        AuditReviewTradCli,
        f"{arguments} {json_arguments} --filter unverified",
    )
    stdout = capsys.readouterr().out
    assert "- row filter: unverified" in stdout
    assert "- table rows: 1" in stdout

    with raises(SystemExit):
        run_cli_with_args(
            AuditReviewTradCli,
            (
                f"{arguments} --traditional-json {traditional_json_path} "
                "--filter unverified"
            ),
        )
    assert (
        "--filter unverified requires --traditional-json and "
        "--traditional-simplified-json"
    ) in capsys.readouterr().err


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
