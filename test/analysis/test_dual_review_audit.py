#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of parallel dual-script subtitle review auditing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

from scinoephile.analysis.audit.dual_review import audit_dual_review
from scinoephile.analysis.audit.review import DualReviewAuditFilter
from scinoephile.core.llms import TestCase
from scinoephile.core.llms.utils import load_test_cases_from_json
from scinoephile.core.subtitles import Series, Subtitle
from scinoephile.llms.review import ReviewManager


class _AuditInputs(TypedDict):
    """Inputs comprising one complete audit input set."""

    traditional: Series
    """Traditional review input."""

    traditional_reviewed: Series
    """Traditional reviewed subtitles."""

    traditional_simplified: Series
    """Traditional simplification review input."""

    traditional_simplified_reviewed: Series
    """Traditional simplification reviewed subtitles."""

    simplified: Series
    """Simplified review input."""

    simplified_reviewed: Series
    """Simplified reviewed subtitles."""

    traditional_review_cases: list[TestCase]
    """Traditional review test cases."""

    traditional_simplified_review_cases: list[TestCase]
    """Traditional simplification review test cases."""

    simplified_review_cases: list[TestCase]
    """Simplified review test cases."""


def test_audit_dual_review_filters_and_includes_json_notes(tmp_path: Path):
    """Test row filters, character filters, and JSON-backed notes.

    Arguments:
        tmp_path: temporary path
    """
    inputs = _get_audit_inputs(tmp_path)

    report = audit_dual_review(
        **inputs,
        row_filter=DualReviewAuditFilter.changes,
    )

    assert "- simplified review edits: 1" in report
    assert "- traditional review edits: 1" in report
    assert "- traditional simplification review edits: 1" in report
    assert "- final text discrepancies: 2" in report
    assert "- table rows: 3" in report
    assert "| Notes | Verified |" in report
    assert "| 1 |" not in report
    assert (
        "| 2 | 简错<br>简正 | 傳錯<br>傳正 | 传正 | 简正<br>传正 | "
        "Simplified review: 修正简体字。<br>Traditional review: 修正繁體字。 |  |"
        in report
    )
    assert "| 3 | 着正 | 著 | 着错<br>着正 | 着正 |" in report
    assert "Simplified review: 修正简体字。" in report
    assert "Traditional review: 修正繁體字。" in report
    assert "Traditional simplification review: 修正簡化結果。" in report

    report = audit_dual_review(
        **inputs,
        row_filter=DualReviewAuditFilter.discrepancies,
    )
    assert "- table rows: 2" in report
    assert "| 2 |" in report
    assert "| 3 |" not in report
    assert "| 4 |" in report

    report = audit_dual_review(
        **inputs,
        row_filter=DualReviewAuditFilter.all,
        characters=("著", "丙"),
    )
    assert "- character filter: 著, 丙" in report
    assert "- table rows: 1" in report
    assert "| 1 |" not in report
    assert "| 3 |" in report

    report = audit_dual_review(
        **inputs,
        row_filter=DualReviewAuditFilter.all,
        first_index=2,
        last_index=3,
    )
    assert "- final text discrepancies: 1" in report
    assert "- subtitle range: 2 through 3" in report
    assert "- table rows: 2" in report
    assert "| 1 |" not in report
    assert "| 2 |" in report
    assert "| 3 |" in report
    assert "| 4 |" not in report


def test_audit_dual_review_ignores_timing_differences(tmp_path: Path):
    """Test timing differences do not prevent count-aligned audits.

    Arguments:
        tmp_path: temporary path
    """
    inputs = _get_audit_inputs(tmp_path)
    inputs["traditional_reviewed"].events[1].start = 62_000
    inputs["traditional_reviewed"].events[1].end = 62_500

    report = audit_dual_review(**inputs, row_filter=DualReviewAuditFilter.all)

    assert "- table rows: 4" in report


def test_audit_dual_review_reuses_deduplicated_json_note(tmp_path: Path):
    """Test one cached JSON block can annotate repeated matching subtitle rows.

    Arguments:
        tmp_path: temporary path
    """
    original_texts = ("錯", "錯")
    reviewed_texts = ("正", "正")
    original = _get_series(original_texts)
    reviewed = _get_series(reviewed_texts)
    json_path = tmp_path / "review.json"
    _write_review_json(json_path, ("錯",), {1: ("正", "修正。")})

    report = audit_dual_review(
        traditional=original,
        traditional_reviewed=reviewed,
        traditional_simplified=reviewed,
        traditional_simplified_reviewed=reviewed,
        simplified=reviewed,
        simplified_reviewed=reviewed,
        traditional_review_cases=_load_review_cases(json_path),
    )

    assert report.count("Traditional review: 修正。") == 2


def _get_audit_inputs(tmp_path: Path) -> _AuditInputs:
    """Get a complete audit input set.

    Arguments:
        tmp_path: temporary path
    Returns:
        audit inputs
    """
    texts_by_name = {
        "traditional": ("甲", "傳錯", "著", "異"),
        "traditional_reviewed": ("甲", "傳正", "著", "異"),
        "traditional_simplified": ("甲", "传正", "着错", "异乙"),
        "traditional_simplified_reviewed": ("甲", "传正", "着正", "异乙"),
        "simplified": ("甲", "简错", "着正", "异甲"),
        "simplified_reviewed": ("甲", "简正", "着正", "异甲"),
    }
    series = {name: _get_series(texts) for name, texts in texts_by_name.items()}

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
    return _AuditInputs(
        traditional=series["traditional"],
        traditional_reviewed=series["traditional_reviewed"],
        traditional_simplified=series["traditional_simplified"],
        traditional_simplified_reviewed=series["traditional_simplified_reviewed"],
        simplified=series["simplified"],
        simplified_reviewed=series["simplified_reviewed"],
        traditional_review_cases=_load_review_cases(traditional_json_path),
        traditional_simplified_review_cases=_load_review_cases(
            traditional_simplified_json_path
        ),
        simplified_review_cases=_load_review_cases(simplified_json_path),
    )


def _get_series(texts: tuple[str, ...]) -> Series:
    """Get a subtitle series fixture.

    Arguments:
        texts: subtitle texts
    Returns:
        subtitle series
    """
    return Series(events=[Subtitle(text=text) for text in texts])


def _load_review_cases(json_path: Path) -> list[TestCase]:
    """Load review test cases from a JSON fixture.

    Arguments:
        json_path: review JSON path
    Returns:
        deserialized review test cases
    """
    return load_test_cases_from_json(
        json_path,
        ReviewManager,
        ReviewManager.base_prompt,
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
    query = {
        "subtitles": [
            {"index": index, "text": text} for index, text in enumerate(texts, 1)
        ]
    }
    answer = {
        "revisions": [
            {"index": index, "text": revised, "note": note}
            for index, (revised, note) in revisions.items()
        ]
    }
    json_path.write_text(
        json.dumps([{"query": query, "answer": answer}], ensure_ascii=False),
        encoding="utf-8",
    )
