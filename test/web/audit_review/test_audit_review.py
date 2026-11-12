#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Editable review sessions, native decision persistence, HTTP and CLI tests."""

from __future__ import annotations

import json
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path
from typing import TextIO
from unittest.mock import patch

from bs4 import BeautifulSoup
from pytest import MonkeyPatch, mark, raises

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common.file import open_atomic_text_file
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.dependencies.web import import_werkzeug_serving
from scinoephile.core.llms.utils import load_test_cases_from_json
from scinoephile.core.subtitles import Series
from scinoephile.lang.review.standard import DEFAULT_PROMPTS
from scinoephile.llms.review import ReviewManager
from scinoephile.operations.review_audit.filters import AuditFilters
from scinoephile.operations.review_audit.project import ReviewAuditProject
from scinoephile.operations.review_audit.rows import AuditStatus
from scinoephile.web.audit_review.app import create_app, serve_audit
from scinoephile.web.audit_review.workspace import get_audit_page


def test_dependent_filter_counts(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Count all options against other filters and search, before pagination.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: configure a single block per page
    """
    audit = _make_project(tmp_path)
    rows = audit.rows()
    rows = [rows[0], replace(rows[1], verified=True)]
    counts = AuditFilters(proofreading="unchanged").counts(rows)
    assert counts["proofreading"] == {
        "all": 2,
        "unchanged": 1,
        "unchanged-unverified": 1,
        "unchanged-verified": 0,
        "changed": 1,
        "changed-unverified": 0,
        "changed-verified": 1,
    }
    assert counts["audit"]["ok"] == counts["audit"]["ok-verified"] == 1
    assert counts["audit"]["ok-unverified"] == counts["audit"]["review"] == 0

    filters = AuditFilters(proofreading="changed-verified", audit="review-unverified")
    assert [filters.matches(row) for row in rows] == [True, False]
    counts = filters.counts(rows)
    assert counts["audit"]["review"] == counts["audit"]["review-unverified"] == 1
    assert counts["proofreading"]["changed-verified"] == 1
    assert counts["proofreading"]["unchanged"] == 0
    counts = AuditFilters(q="model explanation").counts(rows)
    assert counts["proofreading"]["all"] == counts["audit"]["review"] == 1
    assert AuditFilters(q="no matching subtitles").counts(rows)["audit"]["all"] == 0
    monkeypatch.setattr("scinoephile.web.blocks._PAGE_SIZE", 1)
    page = get_audit_page(audit.rows(), AuditFilters(), after=1)
    assert page.filter_counts["proofreading"]["all"] == 2

    client = create_app(audit).test_client()
    html = BeautifulSoup(client.get("/").data, "html.parser")
    selectors = html.select("#filters select")
    assert [select["name"] for select in selectors] == ["proofreading", "audit"]
    for select in selectors:
        assert [option["value"] for option in select.select("option")] == list(
            page.filter_counts[str(select["name"])]
        )
    toolbar = html.select('nav[aria-label="Operations"] .operation-group button')
    assert [button.get_text(strip=True) for button in toolbar] == [
        "Proofread",
        "Verify visible proofreading",
        "Audit",
        "Verify visible audit",
    ]
    footer = html.select_one(".audit-row footer")
    assert footer is not None
    assert [field["name"] for field in footer.select("input, select")] == [
        "proofreading_verified",
        "finding",
        "verified",
    ]


def test_edit_updates_native_answers_and_survives_restart(tmp_path: Path):
    """Save edited text and native answers without changing queries or originals.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_project(tmp_path)
    source_bytes = audit.infile_path.read_bytes()
    original_json = json.loads(audit.proofreading_json_path.read_text())
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
    restored = ReviewAuditProject(
        audit.infile_path,
        audit.outfile_path,
        proofreading_json_path=audit.proofreading_json_path,
        audit_json_path=audit.audit_json_path,
        language=Language.eng,
    )
    assert restored.rows()[0].reviewed == "Hello there."
    assert restored.rows()[0].review_note == "Human correction"
    assert restored.rows()[0].verified
    assert not restored.rows()[0].proofreading_verified
    assert (
        get_audit_page(restored.rows(), AuditFilters(audit="ok-unverified")).matching
        == 1
    )
    saved_json = json.loads(audit.proofreading_json_path.read_text())
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
        audit.proofreading_json_path, ReviewManager, DEFAULT_PROMPTS[Language.eng]
    )
    assert cases[0].answer is not None
    assert cases[0].answer.revisions[0].text == "Hello there."


def test_revert_removes_sparse_revision(tmp_path: Path):
    """An edit restoring the original text removes the native sparse revision.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_project(tmp_path)
    row = audit.rows()[0]
    audit.save(
        row.key,
        reviewed=row.original,
        review_note="",
        notes="Rejected proposal",
        finding="review",
        verified=True,
        version=0,
    )
    assert json.loads(audit.proofreading_json_path.read_text())[0]["answer"] == {
        "revisions": []
    }
    assert audit.rows()[0].verified and not audit.rows()[0].changed


def test_empty_case_files_and_rebuildable_srt(tmp_path: Path):
    """Create both case files and rebuild the SRT from the saved proofreading.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_project(tmp_path, with_json=False)
    assert audit.proofreading_json_path == tmp_path / "proofreading.json"
    assert audit.audit_json_path == tmp_path / "audit.json"
    assert json.loads(audit.proofreading_json_path.read_bytes()) == []
    assert json.loads(audit.audit_json_path.read_bytes()) == []
    assert not audit.outfile_path.exists()

    row = audit.rows()[0]
    audit.save(
        row.key,
        reviewed="Edited manually.",
        review_note="Manual correction",
        notes="",
        finding="unaudited",
        verified=False,
        version=row.version,
        proofreading_verified=True,
    )
    output = audit.outfile_path.read_bytes()
    audit.outfile_path.unlink()
    reopened = ReviewAuditProject(
        audit.infile_path,
        audit.outfile_path,
        proofreading_json_path=audit.proofreading_json_path,
        audit_json_path=audit.audit_json_path,
        language=Language.eng,
    )
    assert reopened.outfile_path.read_bytes() == output
    assert reopened.rows()[0].reviewed == "Edited manually."
    assert all(row.proofreading_verified for row in reopened.rows())
    assert not any(row.verified for row in reopened.rows())
    assert json.loads(audit.proofreading_json_path.read_bytes())[0]["verified"]
    assert json.loads(audit.audit_json_path.read_bytes()) == []


def test_rejects_conflicting_srt_without_proofreading_cases(tmp_path: Path):
    """Keep an existing SRT when the native case file cannot explain its edits.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_project(tmp_path, with_json=False)
    output = audit.infile_path.read_text().replace("Hello.", "Existing edit.")
    audit.outfile_path.write_text(output, encoding="utf-8")
    with raises(ScinoephileError, match="disagree with the proofreading JSON"):
        ReviewAuditProject(
            audit.infile_path,
            audit.outfile_path,
            proofreading_json_path=audit.proofreading_json_path,
            audit_json_path=audit.audit_json_path,
            language=Language.eng,
        )
    assert audit.outfile_path.read_text(encoding="utf-8") == output
    assert json.loads(audit.proofreading_json_path.read_bytes()) == []


def test_rejects_aliases_bad_output_and_external_edits(tmp_path: Path):
    """Reject unsafe paths and externally changed files rather than overwriting.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_project(tmp_path)
    with raises(ScinoephileError, match="differ"):
        ReviewAuditProject(
            audit.infile_path,
            audit.infile_path,
            proofreading_json_path=audit.proofreading_json_path,
            audit_json_path=audit.audit_json_path,
        )
    with raises(ScinoephileError, match="differ"):
        ReviewAuditProject(
            audit.infile_path,
            audit.outfile_path,
            proofreading_json_path=audit.proofreading_json_path,
            audit_json_path=audit.proofreading_json_path,
        )
    with raises(ScinoephileError, match="SRT"):
        ReviewAuditProject(
            audit.infile_path,
            tmp_path / "output.txt",
            proofreading_json_path=audit.proofreading_json_path,
            audit_json_path=audit.audit_json_path,
        )
    audit.proofreading_json_path.write_text(
        audit.proofreading_json_path.read_text() + " "
    )
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
    assert "Hallo." in audit.outfile_path.read_text()
    assert audit.rows()[0].version == 0


def test_shared_json_decisions_are_explicit_and_update_linked_rows(tmp_path: Path):
    """Repeated queries share native answers with visible affected row indexes.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_linked_project(tmp_path)
    row = audit.rows()[0]
    assert row.shared_indexes == (1, 2)
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
    linked = audit.rows()[1]
    assert not linked.verified and linked.finding is AuditStatus.unaudited
    assert linked.notes == ""
    assert linked.version == 1
    blocks = audit.begin_auditing()
    assert [[item.index for item in block] for block in blocks] == [[2]]
    audit.end_auditing()


def test_failed_file_save_does_not_commit_text_or_progress(tmp_path: Path):
    """An output write failure leaves native decisions and progress unchanged.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_project(tmp_path)
    before = audit.proofreading_json_path.read_bytes()
    before_output = audit.outfile_path.read_bytes()
    row = audit.rows()[0]
    with patch(
        "scinoephile.operations.review_audit.project_files.open_atomic_text_file",
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
    assert audit.proofreading_json_path.read_bytes() == before
    assert audit.outfile_path.read_bytes() == before_output
    assert audit.rows()[0] == row


def test_web_edits_escape_content_and_require_csrf(tmp_path: Path):
    """Save editable text via ordinary forms and reject stale or cross-origin posts.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_project(tmp_path)
    audit = _materialize_output(audit)
    client = create_app(audit).test_client()
    row = audit.rows()[0]
    assert client.post(f"/rows/{row.key}", data={}).status_code == 403
    assert client.get("/", headers={"Host": "evil.example"}).status_code == 400
    assert (
        client.get("/export", headers={"Sec-Fetch-Site": "cross-site"}).status_code
        == 403
    )
    text = client.get("/").get_data(as_text=True)
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in text
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
    response = client.post(
        f"/rows/{row.key}", data=data, headers={"Origin": "http://localhost"}
    )
    assert response.status_code == 303
    assert "Hello, corrected." in audit.outfile_path.read_text()
    conflict = client.post(
        f"/rows/{row.key}", data=data, headers={"HX-Request": "true"}
    )
    assert conflict.status_code == 409
    assert conflict.headers["HX-Retarget"] == "#messages"
    assert (
        client.get("/export").get_json()[0]["query"]["subtitles"][0]["proofread"]
        == "Hello, corrected."
    )


def test_htmx_updates_one_row_without_replacing_other_forms(tmp_path: Path):
    """Keep unrelated forms intact when saving removes a row from its filter.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_project(tmp_path)
    client = create_app(audit).test_client()
    client.get("/?audit=review-unverified")
    with client.session_transaction() as session:
        csrf = session["csrf"]
    response = client.post(
        f"/rows/{audit.rows()[0].key}?audit=review-unverified",
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


def test_review_session_wraps_path_resolution_errors(tmp_path: Path):
    """Report path resolution failures as project errors.

    Arguments:
        tmp_path: temporary project directory
    """
    error = PermissionError("Unable to resolve subtitle path")
    with (
        patch.object(Path, "resolve", side_effect=error),
        raises(ScinoephileError, match="Unable to open review editor") as exc,
    ):
        ReviewAuditProject(
            tmp_path / "source.srt",
            tmp_path / "edited.srt",
            proofreading_json_path=tmp_path / "proofreading.json",
            audit_json_path=tmp_path / "audit.json",
        )

    assert exc.value.__cause__ is error


def test_review_serve_wraps_server_io_errors(tmp_path: Path):
    """Report server I/O failures with the requested address.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_project(tmp_path)
    error = OSError("Socket unavailable")
    with (
        patch.object(import_werkzeug_serving(), "make_server", side_effect=error),
        raises(ScinoephileError, match=r"127\.0\.0\.1:5038: Socket unavailable") as exc,
    ):
        serve_audit(audit, port=5038)

    assert exc.value.__cause__ is error


def test_review_serve_cli_requires_both_case_files(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Open the two specified case files through the nested command tree.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: test patch fixture
    """
    audit = _make_project(tmp_path)
    calls = []

    def fake_serve(
        loaded: ReviewAuditProject, *, title: str | None, host: str, port: int
    ):
        """Capture the CLI session configuration.

        Arguments:
            loaded: editable review audit project
            title: optional editor title
            host: loopback interface
            port: requested port
        """
        calls.append(
            (
                loaded.infile_path,
                loaded.outfile_path,
                loaded.proofreading_json_path,
                loaded.audit_json_path,
                title,
                host,
                port,
            )
        )

    monkeypatch.setattr(
        "scinoephile.cli.audit.review.audit_review_serve_cli.serve_audit", fake_serve
    )
    arguments = (
        f'audit review -v serve --infile "{audit.infile_path}" '
        f'--outfile "{audit.outfile_path}" --language eng --port 5038'
    )
    proofreading_arg = f'--proofreading-json "{audit.proofreading_json_path}"'
    audit_arg = f'--audit-json "{audit.audit_json_path}"'
    for json_arg in (proofreading_arg, audit_arg):
        with raises(SystemExit) as exc:
            run_cli_with_args(ScinoephileCli, f"{arguments} {json_arg}")
        assert exc.value.code == 2
    assert not calls
    run_cli_with_args(
        ScinoephileCli,
        f'{arguments} {proofreading_arg} {audit_arg} --title "CLI movie"',
    )
    assert calls[-1] == (
        audit.infile_path,
        audit.outfile_path,
        audit.proofreading_json_path,
        audit.audit_json_path,
        "CLI movie",
        "127.0.0.1",
        5038,
    )


@mark.parametrize("failed_path", ["proofreading_json_path", "audit_json_path"])
def test_partial_write_failure_restores_existing_files(
    tmp_path: Path, failed_path: str
):
    """Restore subtitle files and audit progress when replacing either JSON fails.

    Arguments:
        tmp_path: temporary project directory
        failed_path: session attribute for the JSON whose replacement fails
    """
    audit = _make_project(tmp_path)
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
    before_output = audit.outfile_path.read_bytes()
    before_json = audit.proofreading_json_path.read_bytes()
    before_progress = audit.audit_json_path.read_bytes()

    @contextmanager
    def fail_json(file_path: Path) -> Generator[TextIO]:
        """Fail the selected replace after the subtitle write succeeds.

        Arguments:
            file_path: requested output path
        Yields:
            normal atomic writer for the other files
        Raises:
            OSError: for the JSON write
        """
        if file_path == getattr(audit, failed_path):
            raise OSError("JSON write failed")
        with open_atomic_text_file(file_path) as handle:
            yield handle

    with patch(
        "scinoephile.operations.review_audit.project_files.open_atomic_text_file",
        fail_json,
    ):
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
    assert audit.proofreading_json_path.read_bytes() == before_json
    assert audit.audit_json_path.read_bytes() == before_progress
    assert audit.rows()[0].reviewed == "First saved text."
    assert audit.rows()[0].version == 1


def test_historical_queries_and_multiline_edits_round_trip(tmp_path: Path):
    """Keep historical cases unchanged while editing the latest current answer.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_project(tmp_path)
    latest = json.loads(audit.proofreading_json_path.read_text())[0]
    historical = dict(
        latest,
        answer={
            "revisions": [{"index": 1, "text": "Historical.", "note": "Old answer"}]
        },
    )
    audit.proofreading_json_path.write_text(json.dumps([historical, latest]))
    audit = ReviewAuditProject(
        audit.infile_path,
        audit.outfile_path,
        proofreading_json_path=audit.proofreading_json_path,
        audit_json_path=audit.audit_json_path,
        language=Language.eng,
    )
    row = audit.rows()[0]
    audit.save(
        row.key,
        reviewed="第一行。\nSecond line.",
        review_note="Human",
        notes="",
        finding="ok",
        verified=True,
        version=0,
    )
    data = json.loads(audit.proofreading_json_path.read_text())
    assert data[0]["query"] == historical["query"]
    assert data[0]["answer"] == historical["answer"]
    assert data[1]["query"] == latest["query"]
    restored = ReviewAuditProject(
        audit.infile_path,
        audit.outfile_path,
        proofreading_json_path=audit.proofreading_json_path,
        audit_json_path=audit.audit_json_path,
        language=Language.eng,
    )
    assert restored.rows()[0].reviewed == "第一行。\nSecond line."
    assert restored.rows()[0].verified


@mark.parametrize("reviewed", ["New text ", "New text\n", r"First line\NSecond line"])
def test_rejects_edits_that_cannot_round_trip_in_srt(tmp_path: Path, reviewed: str):
    """Keep the SRT and JSON in agreement after rejecting lossy text.

    Arguments:
        tmp_path: temporary project directory
        reviewed: text that the SRT serializer would change
    """
    audit = _materialize_output(_make_project(tmp_path))
    paths = [audit.outfile_path, audit.proofreading_json_path]
    before = [path.read_bytes() for path in paths]
    row = audit.rows()[0]
    with raises(ValueError, match="cannot be saved unchanged in SRT"):
        audit.save(
            row.key,
            reviewed=reviewed,
            review_note="Manual",
            notes="",
            finding="ok",
            verified=True,
            version=row.version,
        )
    assert [path.read_bytes() for path in paths] == before
    restored = ReviewAuditProject(
        audit.infile_path,
        audit.outfile_path,
        proofreading_json_path=audit.proofreading_json_path,
        audit_json_path=audit.audit_json_path,
        language=audit.language,
    )
    assert restored.rows()[0].reviewed == row.reviewed
    assert restored.rows()[0].version == row.version


def test_saved_cases_use_source_blocks_and_keep_filtered_context(tmp_path: Path):
    """Ignore partial queries and retain the source block when filtering rows.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_project(tmp_path, with_json=False)
    assert len(audit.original.blocks) == 1
    audit.proofreading_json_path.write_text(
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
                },
                {
                    "query": {"subtitles": [{"index": 1, "text": "Same."}]},
                    "answer": {
                        "revisions": [{"index": 1, "text": "Else.", "note": "Old"}]
                    },
                },
            ]
        )
    )
    audit = ReviewAuditProject(
        audit.infile_path,
        audit.outfile_path,
        proofreading_json_path=audit.proofreading_json_path,
        audit_json_path=audit.audit_json_path,
        language=Language.eng,
    )
    page = get_audit_page(audit.rows(), AuditFilters())
    assert len(page.rows) == 2 and len(page.blocks) == 1
    assert [row.reviewed for row in page.rows] == ["Hallo.", "Same."]
    filtered = get_audit_page(audit.rows(), AuditFilters(proofreading="changed"))
    block = filtered.blocks[0]
    assert block.count == 2 and len(block.rows) == 1
    assert block.first_index == 1 and block.last_index == 2


def test_search_by_exact_block_number(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Find unloaded blocks while retaining status filters and ordinary search.

    Arguments:
        tmp_path: isolated project directory
        monkeypatch: configure a single block per page
    """
    audit = _make_project(tmp_path)
    monkeypatch.setattr("scinoephile.web.blocks._PAGE_SIZE", 1)
    for query in ("block 2", "block:2", "BLOCK #2", " block 2 "):
        page = get_audit_page(audit.rows(), AuditFilters(q=query))
        assert [block.number for block in page.blocks] == [2]
        assert [row.index for row in page.rows] == [2]
    assert get_audit_page(audit.rows(), AuditFilters(q="block 20")).matching == 0
    assert (
        get_audit_page(
            audit.rows(), AuditFilters(q="block 2", proofreading="changed")
        ).matching
        == 0
    )
    assert get_audit_page(audit.rows(), AuditFilters(q="Same")).matching == 1
    assert get_audit_page(audit.rows(), AuditFilters(q="1")).rows[0].index == 1
    client = create_app(audit).test_client()
    response = client.get("/?q=block+2", headers={"HX-Request": "true"})
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert 'id="block-2"' in text and 'id="block-1"' not in text
    assert 'value="block 2"' in text


def _make_linked_project(dir_path: Path) -> ReviewAuditProject:
    """Create two blocks linked by a shared proofreading decision.

    Arguments:
        dir_path: temporary project directory
    Returns:
        editable review session with matching source text in both blocks
    """
    audit = _make_project(dir_path)
    original = audit.infile_path.read_text(encoding="utf-8").replace("Same.", "Hello.")
    audit.infile_path.write_text(original, encoding="utf-8")
    audit.outfile_path.unlink()
    audit.proofreading_json_path.write_text(
        json.dumps(
            [
                {
                    "query": {"subtitles": [{"index": 1, "text": "Hello."}]},
                    "answer": {
                        "revisions": [{"index": 1, "text": "Hallo.", "note": "Model"}]
                    },
                }
            ]
        ),
        encoding="utf-8",
    )
    return _materialize_output(
        ReviewAuditProject(
            audit.infile_path,
            audit.outfile_path,
            proofreading_json_path=audit.proofreading_json_path,
            audit_json_path=audit.audit_json_path,
            language=Language.eng,
        )
    )


def _make_project(dir_path: Path, *, with_json: bool = True) -> ReviewAuditProject:
    """Write original subtitles and optional native proofreading and audit cases.

    Arguments:
        dir_path: temporary project directory
        with_json: whether to prepopulate both case files
    Returns:
        editable review session
    """
    source_path = dir_path / "original.srt"
    second_start = 3
    if with_json:
        second_start = 8
    source_path.write_text(
        "1\n00:00:01,000 --> 00:00:02,000\nHello.\n\n"
        f"2\n00:00:{second_start:02d},000 --> "
        f"00:00:{second_start + 1:02d},000\nSame.\n",
        encoding="utf-8",
    )
    proofreading_json_path = dir_path / "proofreading.json"
    audit_json_path = dir_path / "audit.json"
    if with_json:
        proofreading_json_path.write_text(
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
        findings = [
            (
                1,
                "Hello.",
                "Hallo.",
                "model explanation",
                "review",
                "Incorrect; <script>alert(1)</script>",
            ),
            (2, "Same.", "Same.", "", "ok", ""),
        ]
        audit_json_path.write_text(
            json.dumps(
                [
                    {
                        "query": {
                            "language": "eng",
                            "subtitles": [
                                {
                                    "index": index,
                                    "original": original,
                                    "proofread": proofread,
                                    "note": proof_note,
                                }
                            ],
                        },
                        "answer": {
                            "findings": [
                                {"index": index, "status": status, "note": note}
                            ]
                        },
                    }
                    for index, original, proofread, proof_note, status, note in findings
                ]
            ),
            encoding="utf-8",
        )
    return ReviewAuditProject(
        source_path,
        dir_path / "edited.srt",
        proofreading_json_path=proofreading_json_path,
        audit_json_path=audit_json_path,
        language=Language.eng,
    )


def test_history_restore_returns_full_document(tmp_path: Path):
    """Return a complete document for history misses and fragments for normal HTMX.

    Arguments:
        tmp_path: temporary project directory
    """
    client = create_app(_make_project(tmp_path)).test_client()
    document = client.get(
        "/?finding=review",
        headers={"HX-Request": "true", "HX-History-Restore-Request": "true"},
    ).get_data(as_text=True)
    assert "<!doctype html>" in document.lower()
    assert 'href="/static/editor.css"' in document
    stylesheet = client.get("/static/editor.css")
    assert stylesheet.status_code == 200 and stylesheet.mimetype == "text/css"
    fragment = client.get("/", headers={"HX-Request": "true"}).get_data(as_text=True)
    assert "<!doctype html>" not in fragment.lower()


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
    audit = ReviewAuditProject(
        source,
        tmp_path / "edited.srt",
        proofreading_json_path=tmp_path / "proofreading.json",
        audit_json_path=tmp_path / "audit.json",
        language=Language.eng,
    )
    page = get_audit_page(audit.rows(), AuditFilters())
    assert len(page.rows) == 5 and len(page.blocks) == 5
    assert page.matching == 8 and page.last_block == 5 and page.has_more
    text = create_app(audit).test_client().get("/").get_data(as_text=True)
    assert text.count('class="audit-row subtitle-row"') == 5
    assert '<details id="block-8"' not in text
    assert "loaded-through" in text and 'hx-trigger="intersect once"' in text
    client = create_app(audit).test_client()
    batch = client.get(
        "/?after=5", headers={"HX-Request": "true", "HX-Target": "load-more"}
    ).get_data(as_text=True)
    assert batch.count('class="audit-row subtitle-row"') == 3
    assert '<details id="block-8"' in batch and 'id="workspace"' not in batch
    assert (
        BeautifulSoup(batch, "html.parser").select_one(
            'input#loaded-through[name="through"][value="8"]'
        )
        is not None
    )
    assert 'hx-trigger="intersect once"' not in batch
    appended = BeautifulSoup(batch, "html.parser")
    for operation in ("proofreading", "audit"):
        form = appended.select_one(f"#verify-visible-{operation}")
        assert form is not None and form["hx-swap-oob"] == "outerHTML"
        assert "through=8" in str(form["action"])
    native = client.get("/?after=5").get_data(as_text=True)
    assert native.count('class="audit-row subtitle-row"') == 8
    prefix = get_audit_page(audit.rows(), AuditFilters(), through=8)
    assert len(prefix.blocks) == 8 and not prefix.has_more


def test_changed_proofreading_requires_note_before_any_write(tmp_path: Path):
    """Reject incomplete text/note pairs without committing progress or output.

    Arguments:
        tmp_path: temporary project directory
    """
    for with_json in (False, True):
        directory = tmp_path / str(with_json)
        directory.mkdir()
        audit = _make_project(directory, with_json=with_json)
        row = audit.rows()[0]
        before_json = audit.proofreading_json_path.read_bytes()
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
        if with_json:
            assert "Hallo." in audit.outfile_path.read_text()
        else:
            assert not audit.outfile_path.exists()
        assert audit.rows()[0] == row
        assert audit.proofreading_json_path.read_bytes() == before_json


def test_autosave_acknowledges_without_replacing_editable_fields(tmp_path: Path):
    """Acknowledge autosave with a new version and diffs, preserving focused drafts.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_project(tmp_path)
    audit = _materialize_output(audit)
    client = create_app(audit).test_client()
    client.get("/")
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
    assert "<textarea" not in text
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


@mark.parametrize(
    ("notes", "expected_finding"),
    [("Old concern", AuditStatus.unaudited), ("Updated concern", AuditStatus.review)],
)
def test_autosave_clears_old_approval_after_text_edit(
    tmp_path: Path, notes: str, expected_finding: AuditStatus
):
    """Invalidate old approval and retain explicitly changed audit notes.

    Arguments:
        tmp_path: temporary project directory
        notes: unchanged or deliberately changed audit notes
        expected_finding: verdict saved with the new subtitle text
    """
    audit = _materialize_output(_make_project(tmp_path))
    row = audit.rows()[0]
    audit.save(
        row.key,
        reviewed=row.reviewed,
        review_note=row.review_note,
        finding="review",
        notes="Old concern",
        verified=True,
        version=row.version,
    )
    row = audit.rows()[0]
    client = create_app(audit).test_client()
    client.get("/")
    with client.session_transaction() as state:
        csrf = state["csrf"]
    response = client.post(
        f"/rows/{row.key}",
        data=dict(
            csrf=csrf,
            version=row.version,
            reviewed="Hello, corrected.",
            review_note="Corrected punctuation",
            finding=row.finding,
            notes=notes,
            verified="on",
        ),
        headers={"HX-Request": "true", "HX-Target": f"sync-{row.key}"},
    )
    assert response.status_code == 200
    saved = audit.rows()[0]
    assert saved.reviewed == "Hello, corrected."
    assert saved.finding is expected_finding and not saved.verified
    expected_notes = ""
    if expected_finding is AuditStatus.review:
        expected_notes = notes
    assert saved.notes == expected_notes
    html = response.get_data(as_text=True)
    assert f'data-finding="{expected_finding}"' in html
    assert 'data-verified="false"' in html


def test_autosave_inserts_newly_matching_block_in_source_order(tmp_path: Path):
    """Insert a linked block before the existing one when it starts matching.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _make_linked_project(tmp_path)
    first, second = audit.rows()
    audit.save(
        first.key,
        reviewed=first.reviewed,
        review_note=first.review_note,
        notes="",
        finding="ok",
        verified=True,
        version=first.version,
    )
    client = create_app(audit).test_client()
    page = client.get("/?audit=unaudited").get_data(as_text=True)
    assert 'id="block-2"' in page and 'id="block-1"' not in page
    with client.session_transaction() as session:
        csrf = session["csrf"]
    response = client.post(
        f"/rows/{second.key}?audit=unaudited",
        data=dict(
            csrf=csrf,
            through="2",
            version=second.version,
            reviewed="Hello again.",
            review_note="Fixed",
            notes="",
            finding="unaudited",
        ),
        headers={"HX-Request": "true", "HX-Target": f"sync-{second.key}"},
    )
    assert response.status_code == 200
    result = BeautifulSoup(response.data, "html.parser")
    assert result.select_one('[hx-swap-oob="beforebegin:#block-2"] > #block-1')
    assert result.select_one("#block-2") is None


def test_autosave_retains_incrementally_loaded_scope(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Acknowledge a late-block save without deleting earlier blocks or drafts.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: configure a single block per page
    """
    audit = _make_project(tmp_path)
    monkeypatch.setattr("scinoephile.web.blocks._PAGE_SIZE", 1)
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
    assert (
        BeautifulSoup(result, "html.parser").select_one(
            'input#loaded-through[name="through"][value="2"]'
        )
        is not None
    )
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


def test_bulk_verification_only_covers_loaded_blocks(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Approve the loaded audit blocks without rewriting subtitle artifacts.

    Arguments:
        tmp_path: isolated project directory
        monkeypatch: configure a single block per page
    """
    audit = _make_project(tmp_path)
    monkeypatch.setattr("scinoephile.web.blocks._PAGE_SIZE", 1)
    filters = AuditFilters()
    page = get_audit_page(audit.rows(), filters)
    assert len(page.rows) == 1
    before = audit.rows()
    artifacts = {
        p: p.read_bytes()
        for p in (audit.infile_path, audit.outfile_path, audit.proofreading_json_path)
    }
    assert (
        audit.verify_visible(
            filters,
            page.verification["audit"].token,
            through=page.last_block,
            proofreading=False,
        )
        == 1
    )
    assert audit.rows() == [replace(before[0], verified=True, version=1), before[1]]
    assert all(p.read_bytes() == content for p, content in artifacts.items())
    reopened = ReviewAuditProject(
        audit.infile_path,
        audit.outfile_path,
        proofreading_json_path=audit.proofreading_json_path,
        audit_json_path=audit.audit_json_path,
        language=Language.eng,
    )
    assert [row.verified for row in reopened.rows()] == [True, False]


def test_bulk_proofreading_creates_cases_only_for_complete_visible_blocks(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Approve complete visible proofreading and leave the audit JSON untouched.

    Arguments:
        tmp_path: isolated project directory
        monkeypatch: configure a single block per page
    """
    audit = _make_project(tmp_path, with_json=False)
    source = audit.infile_path.read_text(encoding="utf-8")
    source += "\n3\n00:00:10,000 --> 00:00:11,000\nUnloaded.\n"
    audit.infile_path.write_text(source, encoding="utf-8")
    audit.outfile_path.write_text(source, encoding="utf-8")
    audit = ReviewAuditProject(
        audit.infile_path,
        audit.outfile_path,
        proofreading_json_path=audit.proofreading_json_path,
        audit_json_path=audit.audit_json_path,
        language=Language.eng,
    )
    monkeypatch.setattr("scinoephile.web.blocks._PAGE_SIZE", 1)
    client = create_app(audit).test_client()
    filtered = BeautifulSoup(client.get("/?q=Hello").data, "html.parser")
    button = filtered.select_one("#verify-visible-proofreading button")
    assert button is not None and button.has_attr("disabled")

    page = BeautifulSoup(client.get("/").data, "html.parser")
    with client.session_transaction() as session:
        csrf = session["csrf"]
    form = page.select_one("#verify-visible-proofreading")
    assert form is not None
    selection = form.select_one("input[name=selection]")
    assert selection is not None
    token = str(selection["value"])
    url = str(form["action"])
    headers = {"HX-Request": "true"}
    audit_before = audit.audit_json_path.read_bytes()
    output_before = audit.outfile_path.read_bytes()
    prepared = client.post(url, data=dict(csrf=csrf, selection=token), headers=headers)
    assert "Verify 1 proofreading block" in prepared.get_data(as_text=True)
    assert not any(row.proofreading_verified for row in audit.rows())
    result = client.post(
        url, data=dict(csrf=csrf, selection=token, confirm="on"), headers=headers
    )
    assert result.status_code == 200
    assert [row.proofreading_verified for row in audit.rows()] == [True, True, False]
    assert audit.audit_json_path.read_bytes() == audit_before
    assert audit.outfile_path.read_bytes() == output_before
    cases = json.loads(audit.proofreading_json_path.read_bytes())
    assert len(cases) == 1 and cases[0]["verified"]
    assert cases[0]["answer"] == {"revisions": []}


def test_bulk_verification_filters_and_stale_selection(tmp_path: Path):
    """Respect every filter and reject stale selections and active jobs.

    Arguments:
        tmp_path: isolated project directory
    """
    audit = _make_project(tmp_path)
    filters = AuditFilters(proofreading="unchanged", audit="ok-unverified", q="Same")
    token = get_audit_page(audit.rows(), filters).verification["audit"].token
    with patch.object(audit, "_auditing_running", True):
        with raises(ValueError, match="Wait for proofreading"):
            audit.verify_visible(filters, token, through=2, proofreading=False)
    assert audit.verify_visible(filters, token, through=2, proofreading=False) == 1
    assert not audit.rows()[0].verified and audit.rows()[1].verified
    with raises(ValueError, match="visible blocks changed"):
        audit.verify_visible(filters, token, through=2, proofreading=False)
    assert audit.rows()[0].version == 0
    assert audit.rows()[1].version == 1


@mark.parametrize("bulk", [False, True])
def test_proofreading_approval_preserves_separate_audit_blocks(
    tmp_path: Path, bulk: bool
):
    """Keep saved audits when visible text also occurs across hidden block boundaries.

    Arguments:
        tmp_path: isolated project directory
        bulk: approve through the toolbar instead of the subtitle control
    """
    audit = _make_project(tmp_path, with_json=False)
    source = audit.infile_path.read_text(encoding="utf-8")
    source += (
        "\n3\n00:00:10,000 --> 00:00:11,000\nHello.\n"
        "\n4\n00:00:20,000 --> 00:00:21,000\nSame.\n"
    )
    audit.infile_path.write_text(source, encoding="utf-8")
    audit.outfile_path.write_text(source, encoding="utf-8")
    audit = ReviewAuditProject(
        audit.infile_path,
        audit.outfile_path,
        proofreading_json_path=audit.proofreading_json_path,
        audit_json_path=audit.audit_json_path,
        language=Language.eng,
    )
    for row in audit.rows()[2:]:
        audit.save(
            row.key,
            reviewed=row.reviewed,
            review_note="",
            notes="",
            finding="ok",
            verified=True,
            version=row.version,
        )
    audit_content = audit.audit_json_path.read_bytes()

    if bulk:
        filters = AuditFilters(q="block 1")
        page = get_audit_page(audit.rows(), filters)
        assert (
            audit.verify_visible(
                filters,
                page.verification["proofreading"].token,
                through=page.last_block,
                proofreading=True,
            )
            == 1
        )
    else:
        row = audit.rows()[0]
        audit.save(
            row.key,
            reviewed=row.reviewed,
            review_note="",
            notes="",
            finding="unaudited",
            verified=False,
            proofreading_verified=True,
            version=row.version,
        )

    assert [row.proofreading_verified for row in audit.rows()] == [
        True,
        True,
        False,
        False,
    ]
    reopened = ReviewAuditProject(
        audit.infile_path,
        audit.outfile_path,
        proofreading_json_path=audit.proofreading_json_path,
        audit_json_path=audit.audit_json_path,
        language=Language.eng,
    )
    assert reopened.rows() == [replace(row, version=0) for row in audit.rows()]
    assert [row.block_number for row in reopened.rows()] == [1, 1, 2, 3]
    assert [row.verified for row in reopened.rows()] == [False, False, True, True]
    assert reopened.audit_json_path.read_bytes() == audit_content


def test_bulk_verification_http_and_native_form(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Protect bulk writes and support HTMX and ordinary redirects.

    Arguments:
        tmp_path: isolated project directory
        monkeypatch: configure a single block per page
    """
    audit = _materialize_output(_make_project(tmp_path))
    monkeypatch.setattr("scinoephile.web.blocks._PAGE_SIZE", 1)
    client = create_app(audit).test_client()
    client.get("/")
    assert client.post("/verify-visible/audit?through=2").status_code == 403
    with client.session_transaction() as session:
        csrf = session["csrf"]
    filters = AuditFilters(proofreading="unchanged", audit="ok-unverified")
    url = "/verify-visible/audit?proofreading=unchanged&audit=ok-unverified&through=2"
    token = get_audit_page(audit.rows(), filters).verification["audit"].token
    stale = client.post(
        url, data=dict(csrf=csrf, selection="stale"), headers={"HX-Request": "true"}
    )
    assert stale.status_code == 409
    assert not any(row.verified for row in audit.rows())
    prepared = client.post(
        url, data=dict(csrf=csrf, selection=token), headers={"HX-Request": "true"}
    )
    assert prepared.status_code == 200
    confirmation = prepared.get_data(as_text=True)
    assert 'name="confirm" value="on"' in confirmation
    assert "Verify 1 audit block" in confirmation
    assert 'id="workspace"' not in confirmation
    assert not any(row.verified for row in audit.rows())
    result = client.post(
        url,
        data=dict(csrf=csrf, selection=token, confirm="on"),
        headers={"HX-Request": "true"},
    )
    assert result.status_code == 200
    assert result.headers["HX-Retarget"] == "#workspace"
    assert "No rows match" in result.get_data(as_text=True)
    assert not audit.rows()[0].verified and audit.rows()[1].verified
    native = client.post(
        "/verify-visible/audit?through=1",
        data=dict(
            csrf=csrf,
            selection=get_audit_page(audit.rows(), AuditFilters())
            .verification["audit"]
            .token,
        ),
    )
    assert native.status_code == 200
    native_confirmation = native.get_data(as_text=True)
    assert "<!doctype html>" in native_confirmation.lower()
    assert "Verify 1 audit block" in native_confirmation
    assert not audit.rows()[0].verified
    native = client.post(
        "/verify-visible/audit?through=1",
        data=dict(
            csrf=csrf,
            selection=get_audit_page(audit.rows(), AuditFilters())
            .verification["audit"]
            .token,
            confirm="on",
        ),
    )
    assert native.status_code == 303
    assert "proofreading=all" in native.location
    assert all(row.verified for row in audit.rows())


def test_bulk_verification_confirmation_resets_and_rejects_stale_selection(
    tmp_path: Path,
):
    """Keep preparation read-only and reset it when the selection or a row changes.

    Arguments:
        tmp_path: isolated project directory
    """
    audit = _materialize_output(_make_project(tmp_path))
    client = create_app(audit).test_client()
    client.get("/")
    with client.session_transaction() as session:
        csrf = session["csrf"]
    before = audit.rows()
    artifacts = {
        path: path.read_bytes()
        for path in (
            audit.infile_path,
            audit.outfile_path,
            audit.proofreading_json_path,
        )
    }
    token = get_audit_page(audit.rows(), AuditFilters()).verification["audit"].token
    prepared = client.post(
        "/verify-visible/audit?through=2", data=dict(csrf=csrf, selection=token)
    )
    assert 'name="confirm" value="on"' in prepared.get_data(as_text=True)
    assert audit.rows() == before
    assert all(path.read_bytes() == value for path, value in artifacts.items())
    filtered = client.get("/?audit=ok").get_data(as_text=True)
    assert 'name="confirm"' not in filtered
    row = audit.rows()[1]
    saved = client.post(
        f"/rows/{row.key}",
        data=dict(
            csrf=csrf,
            version=row.version,
            reviewed=row.reviewed,
            review_note=row.review_note,
            notes="",
            finding="ok",
        ),
        headers={"HX-Request": "true", "HX-Target": f"sync-{row.key}"},
    )
    assert saved.status_code == 200
    saved_html = saved.get_data(as_text=True)
    assert 'id="verify-visible-audit"' in saved_html
    assert 'name="confirm"' not in saved_html
    selection = get_audit_page(audit.rows(), AuditFilters()).verification["audit"]
    assert f'value="{selection.token}"' in saved_html
    stale = client.post(
        "/verify-visible/audit?through=2",
        data=dict(csrf=csrf, selection=token, confirm="on"),
        headers={"HX-Request": "true"},
    )
    assert stale.status_code == 409
    assert not any(row.verified for row in audit.rows())


@mark.parametrize(
    ("finding", "notes", "error"),
    [
        ("review", " ", "Audit notes are required"),
        ("ok", "Old concern", "Clear audit notes"),
    ],
)
def test_invalid_audit_note_does_not_save(
    tmp_path: Path, finding: str, notes: str, error: str
):
    """Reject invalid verdict/note pairs without changing files or saved progress.

    Arguments:
        tmp_path: isolated project directory
        finding: proposed audit verdict
        notes: invalid audit explanation
        error: expected validation message
    """
    audit = _materialize_output(_make_project(tmp_path))
    row = audit.rows()[0]
    paths = [audit.infile_path, audit.outfile_path, audit.proofreading_json_path]
    before = [p.read_bytes() for p in paths]
    client = create_app(audit).test_client()
    client.get("/")
    with client.session_transaction() as session:
        csrf = session["csrf"]
    response = client.post(
        f"/rows/{row.key}",
        data=dict(
            csrf=csrf,
            reviewed=row.reviewed,
            review_note=row.review_note,
            notes=notes,
            finding=finding,
            verified="on",
            version=str(row.version),
        ),
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 409
    assert error in response.get_data(as_text=True)
    assert audit.rows()[0] == row
    assert before == [p.read_bytes() for p in paths]


@mark.parametrize(("status", "note"), [("review", " "), ("ok", "Old concern")])
def test_open_rejects_invalid_native_findings(tmp_path: Path, status: str, note: str):
    """Reject malformed findings through the standard test-case loader.

    Arguments:
        tmp_path: isolated project directory
        status: stored audit verdict
        note: invalid stored explanation
    """
    audit = _make_project(tmp_path)
    cases = json.loads(audit.audit_json_path.read_bytes())
    cases[0]["answer"]["findings"][0].update(status=status, note=note)
    content = json.dumps(cases)
    audit.audit_json_path.write_text(content, encoding="utf-8")
    with raises(ScinoephileError, match="Unable to open review editor"):
        ReviewAuditProject(
            audit.infile_path,
            audit.outfile_path,
            proofreading_json_path=audit.proofreading_json_path,
            audit_json_path=audit.audit_json_path,
            language=Language.eng,
        )
    assert audit.audit_json_path.read_text(encoding="utf-8") == content


def _materialize_output(audit: ReviewAuditProject) -> ReviewAuditProject:
    """Write the proofread SRT from saved corrections and reopen the project.

    Arguments:
        audit: fixture whose native decisions supply the proposed text
    Returns:
        reopened session with output and optional imported audit notes
    """
    output = Series.load(audit.infile_path)
    for subtitle, row in zip(output, audit.rows(), strict=True):
        subtitle.text = row.reviewed.replace("\n", "\\N")
    audit.outfile_path.write_text(output.to_string("srt"), encoding="utf-8")
    return ReviewAuditProject(
        audit.infile_path,
        audit.outfile_path,
        proofreading_json_path=audit.proofreading_json_path,
        audit_json_path=audit.audit_json_path,
        language=Language.eng,
    )


def test_draft_diff_preview_does_not_require_notes_or_persist(tmp_path: Path):
    """Preview invalid unsaved drafts with escaped spans and no artifact writes.

    Arguments:
        tmp_path: temporary project directory
    """
    audit = _materialize_output(_make_project(tmp_path))
    client = create_app(audit).test_client()
    client.get("/")
    row = audit.rows()[1]
    paths = [
        audit.infile_path,
        audit.outfile_path,
        audit.proofreading_json_path,
        audit.audit_json_path,
    ]
    before = [p.read_bytes() for p in paths]
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
    assert before == [p.read_bytes() for p in paths]
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
