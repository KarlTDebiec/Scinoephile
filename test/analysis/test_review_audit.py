#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of dual-script subtitle review auditing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

from pytest import raises

from scinoephile.analysis.review_audit import ReviewAuditFilter, audit_reviews
from scinoephile.core import ScinoephileError


class _AuditPaths(TypedDict):
    """Paths comprising one complete audit input set."""

    traditional_path: Path
    """Traditional review input path."""

    traditional_reviewed_path: Path
    """Traditional reviewed path."""

    traditional_simplified_path: Path
    """Traditional simplification review input path."""

    traditional_simplified_reviewed_path: Path
    """Traditional simplification reviewed path."""

    simplified_path: Path
    """Simplified review input path."""

    simplified_reviewed_path: Path
    """Simplified reviewed path."""

    traditional_json_path: Path
    """Traditional review JSON path."""

    traditional_simplified_json_path: Path
    """Traditional simplification review JSON path."""

    simplified_json_path: Path
    """Simplified review JSON path."""


def test_audit_reviews_filters_and_includes_json_notes(tmp_path: Path):
    """Test row filters, character filters, and JSON-backed notes.

    Arguments:
        tmp_path: temporary path
    """
    paths = _write_audit_inputs(tmp_path)

    report = audit_reviews(
        **paths,
        row_filter=ReviewAuditFilter.changes,
    )

    assert "- simplified review edits: 1" in report
    assert "- traditional review edits: 1" in report
    assert "- traditional simplification review edits: 1" in report
    assert "- final text discrepancies: 2" in report
    assert "- table rows: 3" in report
    assert "| 1 |" not in report
    assert "| 2 | 简错<br>简正 | 傳錯<br>傳正 | 简正<br>传正 |" in report
    assert "Simplified review: 修正简体字。" in report
    assert "Traditional review: 修正繁體字。" in report
    assert "Traditional simplification review: 修正簡化結果。" in report

    report = audit_reviews(
        **paths,
        row_filter=ReviewAuditFilter.discrepancies,
    )
    assert "- table rows: 2" in report
    assert "| 2 |" in report
    assert "| 3 |" not in report
    assert "| 4 |" in report

    report = audit_reviews(
        **paths,
        row_filter=ReviewAuditFilter.all,
        characters=("著丙",),
    )
    assert "- character filter: 著, 丙" in report
    assert "- table rows: 1" in report
    assert "| 1 |" not in report
    assert "| 3 |" in report

    report = audit_reviews(
        **paths,
        row_filter=ReviewAuditFilter.all,
        first_index=2,
        last_index=3,
    )
    assert "- final text discrepancies: 1" in report
    assert "- subtitle range: 1-indexed numbers 2 through 3" in report
    assert "- table rows: 2" in report
    assert "| 1 |" not in report
    assert "| 2 |" in report
    assert "| 3 |" in report
    assert "| 4 |" not in report


def test_audit_reviews_reuses_deduplicated_json_note(tmp_path: Path):
    """Test one cached JSON block can annotate repeated matching subtitle rows.

    Arguments:
        tmp_path: temporary path
    """
    original_path = tmp_path / "original.srt"
    reviewed_path = tmp_path / "reviewed.srt"
    original_texts = ("錯", "錯")
    reviewed_texts = ("正", "正")
    _write_srt(original_path, original_texts)
    _write_srt(reviewed_path, reviewed_texts)
    json_path = tmp_path / "review.json"
    _write_review_json(json_path, ("錯",), {1: ("正", "修正。")})

    report = audit_reviews(
        traditional_path=original_path,
        traditional_reviewed_path=reviewed_path,
        traditional_simplified_path=reviewed_path,
        traditional_simplified_reviewed_path=reviewed_path,
        simplified_path=reviewed_path,
        simplified_reviewed_path=reviewed_path,
        traditional_json_path=json_path,
    )

    assert report.count("Traditional review: 修正。") == 2


def test_audit_reviews_rejects_misaligned_series(tmp_path: Path):
    """Test mismatched subtitle numbers are rejected.

    Arguments:
        tmp_path: temporary path
    """
    paths = _write_audit_inputs(tmp_path)
    _write_srt(paths["simplified_reviewed_path"], ("甲", "简正", "着正"))

    with raises(ScinoephileError, match="missing subtitles"):
        audit_reviews(**paths, first_index=1, last_index=2)


def test_audit_reviews_validates_index_range(tmp_path: Path):
    """Test invalid subtitle index ranges are rejected.

    Arguments:
        tmp_path: temporary path
    """
    paths = _write_audit_inputs(tmp_path)

    with raises(ScinoephileError, match="--first-index"):
        audit_reviews(**paths, first_index=3, last_index=2)


def test_audit_reviews_ignores_timing_differences(tmp_path: Path):
    """Test timing differences do not prevent count-aligned audits.

    Arguments:
        tmp_path: temporary path
    """
    paths = _write_audit_inputs(tmp_path)
    reviewed_path = paths["traditional_reviewed_path"]
    reviewed_text = reviewed_path.read_text(encoding="utf-8")
    reviewed_path.write_text(
        reviewed_text.replace(
            "00:00:02,000 --> 00:00:02,500",
            "00:01:02,000 --> 00:01:02,500",
        ),
        encoding="utf-8",
    )

    report = audit_reviews(**paths, row_filter=ReviewAuditFilter.all)

    assert "- table rows: 4" in report


def _write_audit_inputs(tmp_path: Path) -> _AuditPaths:
    """Write a complete audit input set.

    Arguments:
        tmp_path: temporary path
    Returns:
        audit argument paths
    """
    texts_by_name = {
        "traditional": ("甲", "傳錯", "著", "異"),
        "traditional_reviewed": ("甲", "傳正", "著", "異"),
        "traditional_simplified": ("甲", "传正", "着错", "异乙"),
        "traditional_simplified_reviewed": ("甲", "传正", "着正", "异乙"),
        "simplified": ("甲", "简错", "着正", "异甲"),
        "simplified_reviewed": ("甲", "简正", "着正", "异甲"),
    }
    series_paths: dict[str, Path] = {}
    for name, texts in texts_by_name.items():
        path = tmp_path / f"{name}.srt"
        _write_srt(path, texts)
        series_paths[name] = path

    traditional_json_path = tmp_path / "traditional.json"
    _write_review_json(
        traditional_json_path,
        texts_by_name["traditional"],
        {2: ("傳正", "修正繁體字。")},
    )
    traditional_simplified_json_path = tmp_path / "traditional_simplified.json"
    _write_review_json(
        traditional_simplified_json_path,
        texts_by_name["traditional_simplified"],
        {3: ("着正", "修正簡化結果。")},
    )
    simplified_json_path = tmp_path / "simplified.json"
    _write_review_json(
        simplified_json_path,
        texts_by_name["simplified"],
        {2: ("简正", "修正简体字。")},
    )
    return _AuditPaths(
        traditional_path=series_paths["traditional"],
        traditional_reviewed_path=series_paths["traditional_reviewed"],
        traditional_simplified_path=series_paths["traditional_simplified"],
        traditional_simplified_reviewed_path=(
            series_paths["traditional_simplified_reviewed"]
        ),
        simplified_path=series_paths["simplified"],
        simplified_reviewed_path=series_paths["simplified_reviewed"],
        traditional_json_path=traditional_json_path,
        traditional_simplified_json_path=traditional_simplified_json_path,
        simplified_json_path=simplified_json_path,
    )


def _write_review_json(
    json_path: Path,
    texts: tuple[str, ...],
    revisions: dict[int, tuple[str, str]],
):
    """Write one block-based review JSON fixture.

    Arguments:
        json_path: output JSON path
        texts: query texts
        revisions: revised text and note keyed by one-based local index
    """
    query = {f"subtitle_{index}": text for index, text in enumerate(texts, 1)}
    answer: dict[str, str] = {}
    for index, (revised, note) in revisions.items():
        answer[f"revised_{index}"] = revised
        answer[f"note_{index}"] = note
    json_path.write_text(
        json.dumps([{"query": query, "answer": answer}], ensure_ascii=False),
        encoding="utf-8",
    )


def _write_srt(srt_path: Path, texts: tuple[str, ...]):
    """Write an SRT fixture.

    Arguments:
        srt_path: output SRT path
        texts: subtitle texts
    """
    blocks = [
        f"{number}\n00:00:{number:02},000 --> 00:00:{number:02},500\n{text}"
        for number, text in enumerate(texts, 1)
    ]
    srt_path.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
