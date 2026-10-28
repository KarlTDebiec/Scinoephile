#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Editable review sessions, native decision persistence, HTTP and CLI tests."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from typing import TextIO
from unittest.mock import patch

from pytest import MonkeyPatch, raises

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common.file import open_atomic_text_file
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.llms.utils import load_test_cases_from_json
from scinoephile.core.subtitles import Series
from scinoephile.lang.review.standard import DEFAULT_PROMPTS
from scinoephile.llms.review import ReviewManager
from scinoephile.web.audit_review.app import create_app
from scinoephile.web.audit_review.session import AuditFilters, AuditSession, AuditStatus


def test_sources_findings_and_search(tmp_path: Path):
    """Apply native proposals and independent report notes without a manifest.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    assert audit.page(AuditFilters()).total == 2
    assert audit.rows()[0].reviewed == "Hallo."
    assert audit.page(AuditFilters(finding="flagged")).matching == 1
    assert audit.page(AuditFilters(changes="unchanged")).matching == 1
    assert audit.page(AuditFilters(q="model explanation")).matching == 1
    assert not audit.outfile_path.exists()
    with raises(ValueError, match="Unknown audit filter"):
        audit.page(AuditFilters(finding="bad"))


def test_dependent_filter_counts(tmp_path: Path):
    """Count all options against other filters and search, before pagination.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    rows = audit.rows()
    rows = [rows[0], replace(rows[1], verified=True)]
    counts = AuditFilters(changes="unchanged").counts(rows)
    assert counts["changes"] == {"all": 2, "changed": 1, "unchanged": 1}
    assert counts["finding"] == {"all": 1, "unaudited": 0, "review": 0, "ok": 1}
    assert counts["verification"] == {"all": 1, "verified": 1, "unverified": 0}
    counts = AuditFilters(changes="unchanged", finding="review").counts(rows)
    assert counts["changes"] == {"all": 1, "changed": 1, "unchanged": 0}
    assert counts["finding"]["ok"] == 1
    assert counts["verification"]["all"] == 0
    counts = AuditFilters(q="model explanation").counts(rows)
    assert counts["changes"]["all"] == 1
    assert counts["finding"]["review"] == 1
    assert AuditFilters(q="no matching subtitles").counts(rows)["finding"]["all"] == 0
    audit.page_size = 1
    page = audit.page(AuditFilters(), after=1)
    assert page.filter_counts["changes"]["all"] == 2
    client = create_app(audit).test_client()
    html = client.get("/?changes=unchanged").get_data(as_text=True)
    assert "All proofreading statuses (2)" in html
    assert "All audit statuses (1)" in html
    assert "OK (1)" in html and "Review (0)" in html


def test_edit_updates_native_answers_and_survives_restart(tmp_path: Path):
    """Save edited text and native answers without changing queries or originals.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    source_bytes = audit.infile_path.read_bytes()
    assert audit.json_path is not None
    original_json = json.loads(audit.json_path.read_text())
    row = audit.rows()[0]
    audit.save(
        row.key,
        reviewed="Hello there.",
        review_note="Human correction",
        notes="",
        finding="ok",
        verified=True,
        version=0,
    )
    restored = AuditSession(
        audit.infile_path,
        audit.outfile_path,
        json_path=audit.json_path,
        language=Language.eng,
    )
    assert restored.rows()[0].reviewed == "Hello there."
    assert restored.rows()[0].review_note == "Human correction"
    assert restored.rows()[0].verified and restored.rows()[0].version == 1
    assert restored.page(AuditFilters(verification="unverified")).matching == 1
    saved_json = json.loads(audit.json_path.read_text())
    assert [c["query"] for c in saved_json] == [c["query"] for c in original_json]
    assert saved_json[0]["answer"]["revisions"][0]["text"] == "Hello there."
    assert not saved_json[0].get("verified", False)
    assert not saved_json[0].get("few_shot", False)
    assert audit.infile_path.read_bytes() == source_bytes
    assert [(s.start, s.end) for s in Series.load(audit.outfile_path)] == [
        (s.start, s.end) for s in audit.original
    ]
    assert "Hello there." in audit.outfile_path.read_text()
    with raises(ValueError, match="another tab"):
        audit.save(
            row.key,
            reviewed="Stale",
            review_note="Stale correction",
            notes="",
            finding="ok",
            verified=True,
            version=0,
        )
    cases = load_test_cases_from_json(
        audit.json_path, ReviewManager, DEFAULT_PROMPTS[Language.eng]
    )
    assert cases[0].answer is not None
    assert cases[0].answer.revisions[0].text == "Hello there."


def test_revert_removes_sparse_revision(tmp_path: Path):
    """An edit restoring the original text removes the native sparse revision.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    row = audit.rows()[0]
    audit.save(
        row.key,
        reviewed=row.original,
        review_note="",
        notes="Rejected proposal",
        finding="incorrect",
        verified=True,
        version=0,
    )
    assert audit.json_path is not None
    assert json.loads(audit.json_path.read_text())[0]["answer"] == {"revisions": []}
    assert audit.rows()[0].verified and not audit.rows()[0].changed


def test_start_without_json_and_create_optional_json_on_save(tmp_path: Path):
    """Open from an SRT alone and write output or a new native log on save.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path, with_json=False)
    row = audit.rows()[0]
    assert row.reviewed == row.original
    audit.save(
        row.key,
        reviewed="Edited manually.",
        review_note="Manual",
        notes="",
        finding="ok",
        verified=True,
        version=0,
    )
    restored = AuditSession(
        audit.infile_path, audit.outfile_path, language=Language.eng
    )
    assert restored.rows()[0].reviewed == "Edited manually."
    assert restored.rows()[0].review_note == "Manual"
    assert restored.rows()[0].verified
    new_json_path = tmp_path / "new-review.json"
    resumed = AuditSession(
        audit.infile_path,
        audit.outfile_path,
        json_path=new_json_path,
        language=Language.eng,
    )
    assert not new_json_path.exists()
    row = resumed.rows()[1]
    resumed.save(
        row.key,
        reviewed="Also edited.",
        review_note="Manual correction",
        notes="",
        finding="ok",
        verified=True,
        version=row.version,
    )
    loaded = AuditSession(
        audit.infile_path,
        audit.outfile_path,
        json_path=new_json_path,
        language=Language.eng,
    )
    assert [r.reviewed for r in loaded.rows()] == ["Edited manually.", "Also edited."]


def test_chinese_is_a_separate_editable_session(tmp_path: Path):
    """Keep Unicode edits and language selection outside the browser UI.

    Arguments:
        tmp_path: temporary project directory
    """
    source_path = tmp_path / "zho.srt"
    source_path.write_text("1\n00:00:01,000 --> 00:00:02,000\n你好\n", encoding="utf-8")
    audit = AuditSession(
        source_path,
        tmp_path / "zho-output.srt",
        json_path=tmp_path / "zho.json",
        language=Language.zho_hant,
    )
    row = audit.rows()[0]
    audit.save(
        row.key,
        reviewed="您好",
        review_note="稱呼",
        notes="",
        finding="ok",
        verified=True,
        version=0,
    )
    text = create_app(audit).test_client().get("/").get_data(as_text=True)
    assert "您好" in text and 'name="track"' not in text
    assert "您好" in audit.outfile_path.read_text(encoding="utf-8")


def test_rejects_aliases_bad_output_and_external_edits(tmp_path: Path):
    """Reject unsafe paths and externally changed files rather than overwriting.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    with raises(ScinoephileError, match="differ"):
        AuditSession(audit.infile_path, audit.infile_path)
    with raises(ScinoephileError, match="SRT"):
        AuditSession(audit.infile_path, tmp_path / "output.txt")
    assert audit.json_path is not None
    audit.json_path.write_text(audit.json_path.read_text() + " ")
    row = audit.rows()[0]
    with raises(ValueError, match="outside this session"):
        audit.save(
            row.key,
            reviewed="Changed",
            review_note="Correction",
            notes="",
            finding="ok",
            verified=True,
            version=0,
        )
    assert not audit.outfile_path.exists()
    assert audit.rows()[0].version == 0


def test_shared_json_decisions_are_explicit_and_update_linked_rows(tmp_path: Path):
    """Repeated queries share native answers with visible affected row indexes.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    original = audit.infile_path.read_text().replace("Same.", "Hello.")
    audit.infile_path.write_text(original)
    assert audit.json_path is not None
    audit.json_path.write_text(
        json.dumps(
            [
                {
                    "query": {"subtitles": [{"index": 1, "text": "Hello."}]},
                    "answer": {
                        "revisions": [{"index": 1, "text": "Hallo.", "note": "Model"}]
                    },
                }
            ]
        )
    )
    audit = AuditSession(
        audit.infile_path,
        audit.outfile_path,
        json_path=audit.json_path,
        language=Language.eng,
    )
    audit = _materialize_output(audit)
    row = audit.rows()[0]
    assert row.shared_indexes == (1, 2)
    text = create_app(audit).test_client().get("/").get_data(as_text=True)
    assert "Shared JSON decision" in text and "1, 2" in text
    affected = audit.save(
        row.key,
        reviewed="Hello again.",
        review_note="Fixed",
        notes="",
        finding="ok",
        verified=True,
        version=0,
    )
    assert len(affected) == 2
    assert [r.reviewed for r in audit.rows()] == ["Hello again."] * 2
    assert not audit.rows()[1].verified
    assert audit.rows()[1].version == 1


def test_failed_file_save_does_not_commit_text_or_progress(tmp_path: Path):
    """An output write failure leaves native decisions and progress unchanged.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    assert audit.json_path is not None
    before = audit.json_path.read_bytes()
    row = audit.rows()[0]
    with patch(
        "scinoephile.web.audit_review.session.open_atomic_text_file",
        side_effect=OSError("disk failure"),
    ):
        with raises(ScinoephileError, match="disk failure"):
            audit.save(
                row.key,
                reviewed="Changed",
                review_note="Correction",
                notes="",
                finding="ok",
                verified=True,
                version=0,
            )
    assert audit.json_path.read_bytes() == before
    assert not audit.outfile_path.exists()
    assert audit.rows()[0] == row


def test_web_edits_escape_content_and_require_csrf(tmp_path: Path):
    """Save editable text via ordinary forms and reject stale or cross-origin posts.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    audit = _materialize_output(audit)
    client = create_app(audit).test_client()
    row = audit.rows()[0]
    assert client.post(f"/rows/{row.key}", data={}).status_code == 403
    text = client.get("/").get_data(as_text=True)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in text
    assert 'name="reviewed"' in text and 'name="review_note"' in text
    assert 'name="track"' not in text
    with client.session_transaction() as session:
        csrf = session["csrf"]
    data = dict(
        csrf=csrf,
        version="0",
        reviewed="Hello, corrected.",
        review_note="Human note",
        notes="",
        finding="ok",
        verified="on",
    )
    assert (
        client.post(
            f"/rows/{row.key}", data=data, headers={"Origin": "https://evil.example"}
        ).status_code
        == 403
    )
    assert client.post(f"/rows/{row.key}", data=data).status_code == 303
    assert "Hello, corrected." in audit.outfile_path.read_text()
    conflict = client.post(
        f"/rows/{row.key}", data=data, headers={"HX-Request": "true"}
    )
    assert conflict.status_code == 409
    assert conflict.headers["HX-Retarget"] == "#messages"
    assert (
        client.get("/export").get_json()["rows"][0]["reviewed"] == "Hello, corrected."
    )
    assert client.get("/audit-review-assets/audit-review.css").status_code == 200
    assert client.get("/static/htmx.min.js").status_code == 200


def test_htmx_updates_one_row_without_replacing_other_forms(tmp_path: Path):
    """Keep unrelated forms intact when saving removes a row from its filter.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    client = create_app(audit).test_client()
    client.get("/?verification=unverified")
    with client.session_transaction() as session:
        csrf = session["csrf"]
    response = client.post(
        f"/rows/{audit.rows()[0].key}?verification=unverified",
        data=dict(
            csrf=csrf,
            version="0",
            reviewed="Hallo.",
            review_note="model explanation",
            notes="",
            finding="ok",
            verified="on",
        ),
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert 'id="block-1" hx-swap-oob="delete"' in text
    assert 'id="form-' + audit.rows()[1].key not in text
    assert 'id="workspace"' not in text


def test_review_serve_cli_accepts_subtitles_and_optional_json(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Dispatch direct subtitle paths through the nested command tree.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: test patch fixture
    """
    audit = _make_session(tmp_path)
    calls = []

    def fake_serve(loaded: AuditSession, *, host: str, port: int):
        """Capture the CLI session configuration.

        Arguments:
            loaded: editable review session
            host: loopback interface
            port: requested port
        """
        calls.append(
            (
                loaded.infile_path,
                loaded.outfile_path,
                loaded.json_path,
                loaded.title,
                host,
                port,
            )
        )

    monkeypatch.setattr(
        "scinoephile.cli.audit.audit_review_serve_cli.serve_audit", fake_serve
    )
    arguments = (
        f'audit review serve --infile "{audit.infile_path}" '
        f'--outfile "{audit.outfile_path}" --language eng --port 5038'
    )
    run_cli_with_args(ScinoephileCli, arguments)
    assert calls[-1][2] is None
    run_cli_with_args(
        ScinoephileCli, f'{arguments} --json "{audit.json_path}" --title "CLI movie"'
    )
    assert calls[-1] == (
        audit.infile_path,
        audit.outfile_path,
        audit.json_path,
        "CLI movie",
        "127.0.0.1",
        5038,
    )


def test_partial_write_failure_restores_existing_files(tmp_path: Path):
    """Restore subtitle bytes and progress when replacing the second file fails.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    row = audit.rows()[0]
    audit.save(
        row.key,
        reviewed="First saved text.",
        review_note="First",
        notes="",
        finding="ok",
        verified=True,
        version=0,
    )
    assert audit.json_path is not None
    before_output = audit.outfile_path.read_bytes()
    before_json = audit.json_path.read_bytes()

    @contextmanager
    def fail_json(file_path: Path) -> Generator[TextIO]:
        """Fail the JSON replace after the subtitle write succeeds.

        Arguments:
            file_path: requested output path
        Yields:
            normal atomic writer for subtitle writes
        Raises:
            OSError: for the JSON write
        """
        if file_path == audit.json_path:
            raise OSError("JSON write failed")
        with open_atomic_text_file(file_path) as handle:
            yield handle

    with patch("scinoephile.web.audit_review.session.open_atomic_text_file", fail_json):
        with raises(ScinoephileError, match="JSON write failed"):
            audit.save(
                row.key,
                reviewed="Unsaved text.",
                review_note="Second",
                notes="",
                finding="ok",
                verified=True,
                version=1,
            )
    assert audit.outfile_path.read_bytes() == before_output
    assert audit.json_path.read_bytes() == before_json
    assert audit.rows()[0].reviewed == "First saved text."
    assert audit.rows()[0].version == 1


def test_historical_queries_and_multiline_edits_round_trip(tmp_path: Path):
    """Keep historical cases unchanged while editing the latest current answer.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    assert audit.json_path is not None
    latest = json.loads(audit.json_path.read_text())[0]
    historical = dict(
        latest,
        answer={
            "revisions": [{"index": 1, "text": "Historical.", "note": "Old answer"}]
        },
    )
    audit.json_path.write_text(json.dumps([historical, latest]))
    audit = AuditSession(
        audit.infile_path,
        audit.outfile_path,
        json_path=audit.json_path,
        language=Language.eng,
    )
    row = audit.rows()[0]
    audit.save(
        row.key,
        reviewed="First line.\nSecond line.",
        review_note="Human",
        notes="",
        finding="ok",
        verified=True,
        version=0,
    )
    assert audit.json_path is not None
    data = json.loads(audit.json_path.read_text())
    assert data[0]["query"] == historical["query"]
    assert data[0]["answer"] == historical["answer"]
    assert data[1]["query"] == latest["query"]
    restored = AuditSession(
        audit.infile_path,
        audit.outfile_path,
        json_path=audit.json_path,
        language=Language.eng,
    )
    assert restored.rows()[0].reviewed == "First line.\nSecond line."
    assert restored.rows()[0].verified


def test_blocks_follow_json_requests_and_keep_filtered_context(tmp_path: Path):
    """Logged queries override pause grouping and remain intact across pages.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    assert len(audit.original.blocks) == 1
    assert len(audit.page(AuditFilters()).blocks) == 2
    assert audit.page(AuditFilters()).blocks[0].first_index == 1
    assert audit.json_path is not None
    audit.json_path.write_text(
        json.dumps(
            [
                {
                    "query": {
                        "subtitles": [
                            {"index": 1, "text": "Hello."},
                            {"index": 2, "text": "Same."},
                        ]
                    },
                    "answer": {
                        "revisions": [{"index": 1, "text": "Hallo.", "note": "Model"}]
                    },
                }
            ]
        )
    )
    audit = AuditSession(
        audit.infile_path,
        audit.outfile_path,
        json_path=audit.json_path,
        language=Language.eng,
    )
    page = audit.page(AuditFilters())
    assert len(page.rows) == 2 and len(page.blocks) == 1
    filtered = audit.page(AuditFilters(changes="changed"))
    block = filtered.blocks[0]
    assert block.count == 2 and len(block.rows) == 1
    assert block.first_index == 1 and block.last_index == 2
    text = (
        create_app(audit).test_client().get("/?changes=changed").get_data(as_text=True)
    )
    assert ">Block 1</a>" in text
    assert 'href="/?q=block+1"' in text
    assert '<span class="block-time">00:00:01 – 00:00:04</span>' in text
    assert "1 of 2 subtitles" in text
    assert '<details id="block-1" class="audit-block">' in text
    assert "<summary>" in text
    assert "block-toggle" not in text
    assert "English #" not in text
    assert "00:00:01.000 – 00:00:02.000" in text


def test_pause_blocks_without_json_and_cli_diff_operations(tmp_path: Path):
    """Use pause blocks without JSON and preserve CLI diff operations.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path, with_json=False)
    assert len(audit.page(AuditFilters()).blocks) == 1
    source = (
        audit.infile_path.read_text()
        .replace("00:00:03,000", "00:00:06,000")
        .replace("00:00:04,000", "00:00:07,000")
    )
    audit.infile_path.write_text(source)
    audit = AuditSession(audit.infile_path, audit.outfile_path, language=Language.eng)
    assert len(audit.page(AuditFilters()).blocks) == 2
    row = audit.rows()[0]
    substitute = replace(row, original="cat", reviewed="cut")
    assert ("a", "substitute") in substitute.differences[0]
    assert ("u", "substitute") in substitute.differences[1]
    inserted = replace(row, original="cat", reviewed="cats")
    assert ("s", "insert") in inserted.differences[1]
    deleted = replace(row, original="cats", reviewed="cat")
    assert ("s", "delete") in deleted.differences[0]


def test_search_by_exact_block_number(tmp_path: Path):
    """Find unloaded blocks while retaining status filters and ordinary search.

    Arguments:
        tmp_path: isolated project directory
    """
    audit = _make_session(tmp_path)
    audit.page_size = 1
    for query in ("block 2", "block:2", "BLOCK #2", " block 2 "):
        page = audit.page(AuditFilters(q=query))
        assert [block.number for block in page.blocks] == [2]
        assert [row.index for row in page.rows] == [2]
    assert audit.page(AuditFilters(q="block 20")).matching == 0
    assert audit.page(AuditFilters(q="block 2", changes="changed")).matching == 0
    assert audit.page(AuditFilters(q="Same")).matching == 1
    assert audit.page(AuditFilters(q="1")).rows[0].index == 1
    client = create_app(audit).test_client()
    response = client.get("/?q=block+2", headers={"HX-Request": "true"})
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert 'id="block-2"' in text and 'id="block-1"' not in text
    assert 'value="block 2"' in text


def _make_session(dir_path: Path, *, with_json: bool = True) -> AuditSession:
    """Write original subtitles, optional native decisions and old audit notes.

    Arguments:
        dir_path: temporary project directory
        with_json: whether to seed existing native proofreading proposals
    Returns:
        editable review session
    """
    source_path = dir_path / "original.srt"
    source_path.write_text(
        "1\n00:00:01,000 --> 00:00:02,000\nHello.\n\n"
        "2\n00:00:03,000 --> 00:00:04,000\nSame.\n",
        encoding="utf-8",
    )
    json_path = None
    if with_json:
        json_path = dir_path / "review.json"
        json_path.write_text(
            json.dumps(
                [
                    {
                        "query": {"subtitles": [{"index": 1, "text": "Hello."}]},
                        "answer": {
                            "revisions": [
                                {
                                    "index": 1,
                                    "text": "Hallo.",
                                    "note": "model explanation",
                                }
                            ]
                        },
                        "verified": True,
                        "few_shot": True,
                    },
                    {
                        "query": {"subtitles": [{"index": 1, "text": "Same."}]},
                        "answer": {"revisions": []},
                    },
                ]
            ),
            encoding="utf-8",
        )
    report_path = dir_path / "audit.md"
    report_path.write_text(
        "| Subtitle | English | Notes | Verified |\n|---|---|---|---|\n"
        "| 1 | unused | Incorrect; <script>alert(1)</script> | |\n"
        "| 2 | unused | OK | |\n",
        encoding="utf-8",
    )
    return AuditSession(
        source_path,
        dir_path / "edited.srt",
        json_path=json_path,
        language=Language.eng,
        report_path=report_path,
    )


def test_loaded_prefix_save_preserves_other_blocks(tmp_path: Path):
    """Keep every loaded block when saving without replacing unrelated forms.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    client = create_app(audit).test_client()
    initial = client.get("/").get_data(as_text=True)
    assert 'id="block-1"' in initial and 'id="block-2"' in initial
    assert "loaded-through" in initial
    assert "<details open" not in initial
    with client.session_transaction() as session:
        csrf = session["csrf"]
    row = audit.rows()[0]
    saved = client.post(
        f"/rows/{row.key}",
        data=dict(
            csrf=csrf,
            version="0",
            reviewed=row.reviewed,
            review_note=row.review_note,
            notes="",
            finding="ok",
        ),
        headers={"HX-Request": "true"},
    ).get_data(as_text=True)
    assert 'id="block-2" hx-swap-oob="delete"' not in saved
    assert 'id="form-' + audit.rows()[1].key not in saved
    filtered = client.get(
        "/?changes=unchanged", headers={"HX-Request": "true", "HX-Target": "workspace"}
    ).get_data(as_text=True)
    assert 'id="workspace"' in filtered and 'id="block-2"' in filtered
    assert 'id="block-1"' not in filtered


def test_audit_statuses_migrate_legacy_progress(tmp_path: Path):
    """Merge legacy verdicts without losing saved notes or human verification.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    assert audit.rows()[0].finding is AuditStatus.review
    assert audit.page(AuditFilters(finding="review")).matching == 1
    for legacy, expected in (
        ("incorrect", AuditStatus.review),
        ("check", AuditStatus.review),
        ("unassessed", AuditStatus.unaudited),
    ):
        row = audit.rows()[0]
        audit.save(
            row.key,
            version=row.version,
            reviewed=row.reviewed,
            review_note=row.review_note,
            notes="Keep this audit note",
            finding="review",
            verified=True,
        )
        with sqlite3.connect(audit.state_path) as db:
            db.execute("UPDATE review_edits SET finding = ?", (legacy,))
        audit = _make_session(tmp_path)
        migrated = audit.rows()[0]
        assert migrated.finding is expected
        assert migrated.notes == "Keep this audit note"
        assert migrated.verified
        assert migrated.version == row.version + 2
        assert AuditFilters(finding=legacy).finding == expected
    assert AuditFilters(finding="flagged").finding == AuditStatus.review
    page = create_app(audit).test_client().get("/").get_data(as_text=True)
    assert 'value="review"' in page
    assert 'value="unaudited"' in page
    assert 'value="incorrect"' not in page
    assert 'value="check"' not in page


def test_domain_assets_and_history_restore(tmp_path: Path):
    """Serve domain-owned assets and restore a complete document for history misses.

    Arguments:
        tmp_path: temporary project directory
    """
    client = create_app(_make_session(tmp_path)).test_client()
    for filename in (
        "audit-review.css",
        "audit-review.js",
        "mdi.LICENSE",
        "apache-2.0.LICENSE",
        "icons/checkbox-blank-outline.svg",
        "icons/checkbox-marked.svg",
        "icons/minus-box-outline.svg",
        "icons/plus-box-outline.svg",
        "icons/filter-outline.svg",
        "icons/filter-remove-outline.svg",
        "icons/magnify.svg",
    ):
        assert client.get(f"/audit-review-assets/{filename}").status_code == 200
    document = client.get(
        "/?finding=review",
        headers={"HX-Request": "true", "HX-History-Restore-Request": "true"},
    ).get_data(as_text=True)
    assert "<!doctype html>" in document
    assert 'src="/static/htmx.min.js"' in document
    assert 'src="/audit-review-assets/audit-review.js"' in document
    assert '<use href="/audit-review-assets/icons/' in document
    assert "<path" not in document
    assert "<style" not in document
    fragment = client.get("/", headers={"HX-Request": "true"}).get_data(as_text=True)
    assert "<!doctype html>" not in fragment


def test_block_batches_use_stable_cursors(tmp_path: Path):
    """Bound initial rendering and append complete blocks without losing source order.

    Arguments:
        tmp_path: temporary project directory
    """
    source = tmp_path / "all.srt"
    source.write_text(
        "".join(
            f"{index}\n00:00:{index * 5:02d},000 --> "
            f"00:00:{index * 5 + 1:02d},000\nLine {index}.\n\n"
            for index in range(1, 9)
        ),
        encoding="utf-8",
    )
    audit = AuditSession(source, tmp_path / "edited.srt", language=Language.eng)
    page = audit.page(AuditFilters())
    assert len(page.rows) == 5 and len(page.blocks) == 5
    assert page.matching == 8 and page.last_block == 5 and page.has_more
    text = create_app(audit).test_client().get("/").get_data(as_text=True)
    assert text.count('class="audit-row"') == 5
    assert '<details id="block-8"' not in text
    assert "<details open" not in text
    assert "loaded-through" in text and 'hx-trigger="intersect once"' in text
    client = create_app(audit).test_client()
    batch = client.get(
        "/?after=5", headers={"HX-Request": "true", "HX-Target": "load-more"}
    ).get_data(as_text=True)
    assert batch.count('class="audit-row"') == 3
    assert '<details id="block-8"' in batch and 'id="workspace"' not in batch
    assert 'id="loaded-through" name="through" value="8"' in batch
    assert 'hx-trigger="intersect once"' not in batch
    assert batch.count("hx-get=") == 3
    prefix = audit.page(AuditFilters(), through=8)
    assert len(prefix.blocks) == 8 and not prefix.has_more
    assert page.rows[0].differences == ([("Line 1.", "match")], [("Line 1.", "match")])


def test_changed_proofreading_requires_note_before_any_write(tmp_path: Path):
    """Reject incomplete text/note pairs without committing progress or output.

    Arguments:
        tmp_path: temporary project directory
    """
    for with_json in (False, True):
        directory = tmp_path / str(with_json)
        directory.mkdir()
        audit = _make_session(directory, with_json=with_json)
        row = audit.rows()[0]
        before_json = None
        if audit.json_path is not None:
            before_json = audit.json_path.read_bytes()
        for note in ("", "   "):
            with raises(ValueError, match="A note is required"):
                audit.save(
                    row.key,
                    reviewed="Corrected text",
                    review_note=note,
                    notes="",
                    finding="ok",
                    verified=True,
                    version=0,
                )
        assert not audit.outfile_path.exists()
        assert audit.rows()[0] == row
        if audit.json_path is not None:
            assert audit.json_path.read_bytes() == before_json


def test_autosave_acknowledges_without_replacing_editable_fields(tmp_path: Path):
    """Acknowledge autosave with a new version and diffs, preserving focused drafts.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    audit = _materialize_output(audit)
    client = create_app(audit).test_client()
    initial = client.get("/").get_data(as_text=True)
    assert 'hx-trigger="submit, review:save"' in initial
    row = audit.rows()[0]
    with client.session_transaction() as session:
        csrf = session["csrf"]
    values = dict(
        csrf=csrf,
        version="0",
        reviewed="Hello, corrected.",
        review_note="Corrected punctuation",
        notes="Checked",
        finding="review",
        verified="on",
    )
    response = client.post(
        f"/rows/{row.key}",
        data=values,
        headers={"HX-Request": "true", "HX-Target": f"sync-{row.key}"},
    )
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert f'id="sync-{row.key}"' in text
    assert f'id="version-{row.key}"' in text and 'value="1"' in text
    assert f'id="proofread-diff-{row.key}"' in text
    assert "<textarea" not in text and "<form" not in text
    assert 'id="filter-verification" hx-swap-oob="outerHTML"' in text
    assert "Verified (1)" in text and "Unverified (1)" in text
    assert audit.rows()[0].verified
    assert audit.rows()[0].review_note == "Corrected punctuation"
    values["version"] = "1"
    values["review_note"] = " "
    rejected = client.post(
        f"/rows/{row.key}",
        data=values,
        headers={"HX-Request": "true", "HX-Target": f"sync-{row.key}"},
    )
    assert rejected.status_code == 409
    assert "A note is required" in rejected.get_data(as_text=True)
    assert audit.rows()[0].version == 1


def test_autosave_retains_incrementally_loaded_scope(tmp_path: Path):
    """Acknowledge a late-block save without deleting earlier blocks or drafts.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_session(tmp_path)
    audit.page_size = 1
    client = create_app(audit).test_client()
    first = client.get("/").get_data(as_text=True)
    assert 'id="block-1"' in first and 'id="block-2"' not in first
    second = client.get(
        "/?after=1", headers={"HX-Request": "true", "HX-Target": "load-more"}
    ).get_data(as_text=True)
    assert 'id="block-2"' in second and 'id="block-1"' not in second
    with client.session_transaction() as session:
        csrf = session["csrf"]
    row = audit.rows()[1]
    result = client.post(
        f"/rows/{row.key}?through=1",
        data=dict(
            csrf=csrf,
            through="2",
            version="0",
            reviewed=row.reviewed,
            review_note=row.review_note,
            notes="",
            finding="ok",
        ),
        headers={"HX-Request": "true", "HX-Target": f"sync-{row.key}"},
    ).get_data(as_text=True)
    assert 'id="loaded-through" name="through" value="2"' in result
    assert 'id="block-2" hx-swap-oob="delete"' not in result
    assert f'id="form-{audit.rows()[0].key}"' not in result
    assert "<textarea" not in result
    ordinary = client.post(
        f"/rows/{row.key}?through=2",
        data=dict(
            csrf=csrf,
            version="1",
            reviewed=row.reviewed,
            review_note=row.review_note,
            notes="",
            finding="ok",
        ),
    )
    assert ordinary.status_code == 303 and "through=2" in ordinary.location


def test_bulk_verification_covers_unloaded_matches(tmp_path: Path):
    """Verify the complete filter selection without rewriting subtitle artifacts.

    Arguments:
        tmp_path: isolated project directory
    """
    audit = _materialize_output(_make_session(tmp_path))
    audit.page_size = 1
    filters = AuditFilters(verification="unverified")
    assert len(audit.page(filters).rows) == 1
    before = audit.rows()
    assert audit.json_path is not None
    artifacts = {
        p: p.read_bytes()
        for p in (audit.infile_path, audit.outfile_path, audit.json_path)
    }
    assert audit.verify_visible(filters, audit.verification_token(filters)) == 2
    assert audit.page(filters).matching == 0
    for old, current in zip(before, audit.rows(), strict=True):
        assert current == replace(old, verified=True, version=old.version + 1)
    assert all(p.read_bytes() == content for p, content in artifacts.items())
    reopened = AuditSession(
        audit.infile_path,
        audit.outfile_path,
        json_path=audit.json_path,
        language=Language.eng,
    )
    assert all(row.verified for row in reopened.rows())


def test_bulk_verification_filters_and_stale_selection(tmp_path: Path):
    """Respect every filter and reject stale selections and active jobs.

    Arguments:
        tmp_path: isolated project directory
    """
    audit = _make_session(tmp_path)
    filters = AuditFilters(
        changes="unchanged", finding="ok", verification="unverified", q="Same"
    )
    token = audit.verification_token(filters)
    with raises(ValueError, match="Run proofreading"):
        audit.verify_visible(filters, token)
    audit = _materialize_output(audit)
    token = audit.verification_token(filters)
    with patch.object(audit, "_auditing_running", True):
        with raises(ValueError, match="Wait for proofreading"):
            audit.verify_visible(filters, token)
    assert audit.verify_visible(filters, token) == 1
    assert not audit.rows()[0].verified and audit.rows()[1].verified
    with raises(ValueError, match="matching subtitles changed"):
        audit.verify_visible(filters, token)
    assert audit.rows()[0].version == 0
    assert audit.rows()[1].version == 1


def test_bulk_verification_http_and_native_form(tmp_path: Path):
    """Protect bulk writes and support HTMX and ordinary redirects.

    Arguments:
        tmp_path: isolated project directory
    """
    audit = _materialize_output(_make_session(tmp_path))
    client = create_app(audit).test_client()
    html = client.get("/").get_data(as_text=True)
    assert 'aria-label="Operations"' in html and "Verify All Visible" in html
    assert html.index('aria-label="Operations"') < html.index("data-toggle-blocks")
    assert client.post("/verify-visible").status_code == 403
    with client.session_transaction() as session:
        csrf = session["csrf"]
    filters = AuditFilters(changes="unchanged", finding="ok", verification="unverified")
    url = "/verify-visible?changes=unchanged&finding=ok&verification=unverified"
    token = audit.verification_token(filters)
    stale = client.post(
        url, data=dict(csrf=csrf, selection="stale"), headers={"HX-Request": "true"}
    )
    assert stale.status_code == 409
    assert not any(row.verified for row in audit.rows())
    result = client.post(
        url, data=dict(csrf=csrf, selection=token), headers={"HX-Request": "true"}
    )
    assert result.status_code == 200
    assert "No rows match" in result.get_data(as_text=True)
    assert not audit.rows()[0].verified and audit.rows()[1].verified
    native = client.post(
        "/verify-visible",
        data=dict(csrf=csrf, selection=audit.verification_token(AuditFilters())),
    )
    assert native.status_code == 303
    assert "changes=all" in native.location
    assert all(row.verified for row in audit.rows())


def test_review_verdict_requires_audit_notes_before_writing(tmp_path: Path):
    """Reject empty explanations in manual Review saves and allow empty OK notes.

    Arguments:
        tmp_path: isolated project directory
    """
    audit = _materialize_output(_make_session(tmp_path))
    row = audit.rows()[0]
    assert audit.json_path is not None
    artifacts = {
        p: p.read_bytes()
        for p in (audit.infile_path, audit.outfile_path, audit.json_path)
    }
    client = create_app(audit).test_client()
    client.get("/")
    with client.session_transaction() as session:
        csrf = session["csrf"]
    for status in ("review", "incorrect", "check"):
        for notes in ("", "   \n"):
            with raises(ValueError, match="Audit notes are required"):
                audit.save(
                    row.key,
                    reviewed=row.reviewed,
                    review_note=row.review_note,
                    notes=notes,
                    finding=status,
                    verified=True,
                    version=row.version,
                )
            response = client.post(
                f"/rows/{row.key}",
                data=dict(
                    csrf=csrf,
                    reviewed=row.reviewed,
                    review_note=row.review_note,
                    notes=notes,
                    finding=status,
                    verified="on",
                    version=str(row.version),
                ),
                headers={"HX-Request": "true"},
            )
            assert response.status_code == 409
            assert "Audit notes are required" in response.get_data(as_text=True)
            assert audit.rows()[0] == row
            assert all(p.read_bytes() == content for p, content in artifacts.items())
    audit.save(
        row.key,
        reviewed=row.reviewed,
        review_note=row.review_note,
        notes="",
        finding="ok",
        verified=True,
        version=row.version,
    )
    assert audit.rows()[0].verified and audit.rows()[0].notes == ""


def test_bulk_verification_rejects_review_without_notes(tmp_path: Path):
    """Do not let bulk verification bypass validation of older incomplete rows.

    Arguments:
        tmp_path: isolated project directory
    """
    audit = _materialize_output(_make_session(tmp_path))
    with sqlite3.connect(audit.state_path) as db:
        row = audit.rows()[0]
        db.execute(
            "INSERT OR REPLACE INTO review_edits VALUES (?, ?, ?, ?, ?, ?, ?)",
            (row.key, row.reviewed, row.review_note, " ", "review", 0, 1),
        )
    filters = AuditFilters()
    with raises(ValueError, match="Audit notes are required"):
        audit.verify_visible(filters, audit.verification_token(filters))
    assert not any(row.verified for row in audit.rows())


def test_ok_verdict_rejects_audit_notes_before_writing(tmp_path: Path):
    """Keep invalid OK drafts out of subtitle artifacts and saved progress.

    Arguments:
        tmp_path: isolated project directory
    """
    audit = _materialize_output(_make_session(tmp_path))
    row = audit.rows()[0]
    assert audit.json_path is not None
    artifacts = {
        p: p.read_bytes()
        for p in (audit.infile_path, audit.outfile_path, audit.json_path)
    }
    client = create_app(audit).test_client()
    client.get("/")
    with client.session_transaction() as session:
        csrf = session["csrf"]
    for notes in ("Old audit explanation", "   "):
        with raises(ValueError, match="Clear audit notes"):
            audit.save(
                row.key,
                reviewed=row.reviewed,
                review_note=row.review_note,
                notes=notes,
                finding="ok",
                verified=True,
                version=row.version,
            )
        for headers in ({}, {"HX-Request": "true"}):
            response = client.post(
                f"/rows/{row.key}",
                data=dict(
                    csrf=csrf,
                    reviewed=row.reviewed,
                    review_note=row.review_note,
                    notes=notes,
                    finding="ok",
                    verified="on",
                    version=str(row.version),
                ),
                headers=headers,
            )
            assert response.status_code == 409
            assert "Clear audit notes" in response.get_data(as_text=True)
    assert audit.rows()[0] == row
    assert all(p.read_bytes() == content for p, content in artifacts.items())
    audit.save(
        row.key,
        reviewed=row.reviewed,
        review_note=row.review_note,
        notes="",
        finding="ok",
        verified=False,
        version=row.version,
    )
    assert audit.rows()[0].finding == AuditStatus.ok
    assert audit.rows()[0].notes == ""


def test_bulk_verification_rejects_ok_with_notes(tmp_path: Path):
    """Reject older incomplete OK rows without discarding their existing notes.

    Arguments:
        tmp_path: isolated project directory
    """
    audit = _materialize_output(_make_session(tmp_path))
    row = audit.rows()[1]
    with sqlite3.connect(audit.state_path) as db:
        db.execute(
            "INSERT OR REPLACE INTO review_edits VALUES (?, ?, ?, ?, ?, ?, ?)",
            (row.key, row.reviewed, row.review_note, "Retained note", "ok", 0, 1),
        )
    filters = AuditFilters()
    with raises(ValueError, match="Clear audit notes"):
        audit.verify_visible(filters, audit.verification_token(filters))
    assert not any(row.verified for row in audit.rows())
    assert audit.rows()[1].notes == "Retained note"


def _materialize_output(audit: AuditSession) -> AuditSession:
    """Give editor UI tests an actual completed proofreading output.

    Arguments:
        audit: fixture whose native decisions supply the proposed text
    Returns:
        reopened session with output and optional imported audit notes
    """
    output = Series.load(audit.infile_path)
    for subtitle, row in zip(output, audit.rows(), strict=True):
        subtitle.text = row.reviewed.replace("\n", "\\N")
    audit.outfile_path.write_text(output.to_string("srt"), encoding="utf-8")
    report_path = audit.infile_path.parent / "audit.md"
    return AuditSession(
        audit.infile_path,
        audit.outfile_path,
        json_path=audit.json_path,
        language=Language.eng,
        report_path=report_path,
    )


def test_draft_diff_preview_does_not_require_notes_or_persist(tmp_path: Path):
    """Preview invalid unsaved drafts with escaped spans and no artifact writes.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _materialize_output(_make_session(tmp_path))
    client = create_app(audit).test_client()
    client.get("/")
    row = audit.rows()[1]
    paths = [audit.infile_path, audit.outfile_path, audit.json_path, audit.state_path]
    before = [p.read_bytes() for p in paths if p is not None]
    assert client.post(f"/rows/{row.key}/preview", data={}).status_code == 403
    with client.session_transaction() as session:
        csrf = session["csrf"]
    response = client.post(
        f"/rows/{row.key}/preview",
        data={
            "csrf": csrf,
            "reviewed": "Same. <script>Draft</script>",
            "review_note": "",
        },
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert f'id="original-diff-{row.key}" hx-swap-oob="outerHTML"' in html
    assert f'id="proofread-diff-{row.key}"' in html
    assert "diff-insert" in html and "&lt;script&gt;" in html
    assert "<script>" not in html and "<textarea" not in html
    assert before == [p.read_bytes() for p in paths if p is not None]
    assert audit.rows()[1] == row
    reverted = client.post(
        f"/rows/{row.key}/preview", data={"csrf": csrf, "reviewed": row.original}
    ).get_data(as_text=True)
    assert "diff-insert" not in reverted and "diff-delete" not in reverted
    assert (
        client.post(
            f"/rows/{row.key}/preview", data={"csrf": csrf, "reviewed": "x" * 1001}
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/rows/missing/preview", data={"csrf": csrf, "reviewed": "Draft"}
        ).status_code
        == 404
    )
