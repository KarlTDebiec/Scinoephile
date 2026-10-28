#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Offline independent audits, durable findings, conflicts and HTTP controls."""

from __future__ import annotations

import json
from pathlib import Path
from threading import Event
from typing import Any, Unpack
from unittest.mock import Mock

from pydantic import ValidationError
from pytest import MonkeyPatch, mark, raises

from scinoephile.core import Language
from scinoephile.core.llms import Answer, ChatCompletionKwargs, LLMProvider
from scinoephile.core.llms.tool_box import ToolBox
from scinoephile.llms.review_audit import ReviewAuditTestCase
from scinoephile.web.audit_review import auditing
from scinoephile.web.audit_review.app import create_app
from scinoephile.web.audit_review.auditing import AuditingJob
from scinoephile.web.audit_review.session import AuditSession, AuditStatus


class _Provider(LLMProvider):
    """Offline structured audit provider with gates and deterministic failures."""

    def __init__(self):
        """Initialize recorded context and worker controls."""
        self.completion_metrics = []
        self.entered = Event()
        self.release = Event()
        self.release.set()
        self.queries = []
        self.fail_at = 0

    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer],
        tool_box: ToolBox | None = None,
        **kwargs: Unpack[ChatCompletionKwargs],
    ) -> str:
        """Return complete findings without network calls.

        Arguments:
            messages: prompt and structured query
            response_format: audit answer schema
            tool_box: unused tool configuration
            **kwargs: shared request metadata
        Returns:
            one valid finding per input subtitle
        Raises:
            RuntimeError: if a requested gate or simulated failure occurs
        """
        self.entered.set()
        if not self.release.wait(10):
            raise RuntimeError("Worker gate timed out")
        query = json.loads(messages[1]["content"])
        self.queries.append(query)
        if self.fail_at == len(self.queries):
            raise RuntimeError("Intentional audit failure")
        findings = []
        for subtitle in query["subtitles"]:
            status = "ok"
            note = ""
            if subtitle["index"] == 1:
                status = "review"
                note = "Check this correction against context."
            findings.append(
                {"index": subtitle["index"], "status": status, "note": note}
            )
        return response_format.model_validate({"findings": findings}).model_dump_json()


def _setup(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> tuple[AuditSession, _Provider, Mock]:
    """Create two completed subtitle blocks and an isolated provider.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: provider factory replacement
    Returns:
        session, offline provider and factory recorder
    """
    source = (
        "1\n00:00:01,000 --> 00:00:02,000\nHello.\n\n"
        "2\n00:00:02,100 --> 00:00:03,000\nSame.\n\n"
        "3\n00:00:10,000 --> 00:00:11,000\nBye.\n"
    )
    infile_path = tmp_path / "source.srt"
    outfile_path = tmp_path / "output.srt"
    infile_path.write_text(source, encoding="utf-8")
    outfile_path.write_text(source, encoding="utf-8")
    json_path = tmp_path / "review.json"
    json_path.write_text("[]\n", encoding="utf-8")
    audit = AuditSession(
        infile_path, outfile_path, json_path=json_path, language=Language.eng
    )
    provider = _Provider()
    factory = Mock(return_value=provider)
    monkeypatch.setattr(auditing, "get_provider", factory)
    return audit, provider, factory


def _join(job: AuditingJob):
    """Wait for bounded completion of an offline worker.

    Arguments:
        job: running background audit
    """
    assert job._thread is not None
    job._thread.join(15)
    assert not job._thread.is_alive()


def test_audit_persists_findings_preserving_text_and_human_state(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Audit full context, preserve human decisions and leave all subtitle files intact.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline provider replacement
    """
    audit, provider, factory = _setup(tmp_path, monkeypatch)
    human = audit.rows()[1]
    audit.save(
        human.key,
        reviewed=human.reviewed,
        review_note="",
        notes="Human finding",
        finding="review",
        verified=True,
        version=human.version,
    )
    paths = [audit.infile_path, audit.outfile_path, audit.json_path]
    before = [p.read_bytes() for p in paths if p is not None]
    job = AuditingJob(audit)
    job.start("openai", "gpt-6-luna", "xhigh")
    _join(job)
    assert job.snapshot().status == "complete", job.snapshot().error
    assert job.snapshot().completed == 2
    factory.assert_called_once_with(
        "openai", model="gpt-6-luna", reasoning_effort="xhigh"
    )
    assert len(provider.queries[0]["subtitles"]) == 2
    assert [row.finding for row in audit.rows()] == [
        AuditStatus.review,
        AuditStatus.review,
        AuditStatus.ok,
    ]
    assert audit.rows()[1].verified and audit.rows()[1].notes == "Human finding"
    assert not audit.rows()[0].verified and not audit.rows()[2].verified
    assert before == [p.read_bytes() for p in paths if p is not None]
    restored = AuditSession(
        audit.infile_path,
        audit.outfile_path,
        json_path=audit.json_path,
        language=Language.eng,
    )
    assert restored.rows() == audit.rows()
    assert not AuditingJob(restored).snapshot().available


def test_audit_partial_failure_resumes_only_remaining_blocks(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Keep published blocks after failure and retry only unaudited blocks.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline provider replacement
    """
    audit, provider, _ = _setup(tmp_path, monkeypatch)
    provider.fail_at = 2
    job = AuditingJob(audit)
    job.start("openai", "", "")
    _join(job)
    assert job.snapshot().status == "error" and job.snapshot().completed == 1
    assert audit.rows()[2].finding == AuditStatus.unaudited
    provider.fail_at = 0
    job.start("openai", "", "")
    _join(job)
    assert job.snapshot().status == "complete" and job.snapshot().total == 1
    assert [s["index"] for s in provider.queries[-1]["subtitles"]] == [3]


def test_audit_rejects_missing_output_duplicate_runs_edits_and_external_change(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Reserve current output and reject concurrent or stale publication.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline provider replacement
    """
    audit, provider, _ = _setup(tmp_path, monkeypatch)
    provider.release.clear()
    job = AuditingJob(audit)
    job.start("openai", "", "")
    assert provider.entered.wait(5)
    try:
        with raises(ValueError, match="current operation"):
            job.start("openai", "", "")
        row = audit.rows()[0]
        with raises(ValueError, match="finish before editing"):
            audit.save(
                row.key,
                reviewed=row.reviewed,
                review_note="",
                notes="",
                finding="ok",
                verified=True,
                version=row.version,
            )
        audit.outfile_path.write_text("External change", encoding="utf-8")
    finally:
        provider.release.set()
        _join(job)
    assert job.snapshot().status == "error"
    assert all(row.finding == AuditStatus.unaudited for row in audit.rows())
    assert audit.outfile_path.read_text() == "External change"
    audit.outfile_path.unlink()
    with raises(ValueError, match="before auditing"):
        job.start("openai", "", "")


def test_audit_http_csrf_polling_and_completion(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Expose an accessible card, enforce CSRF and poll without manual refresh.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline provider replacement
    """
    audit, provider, _ = _setup(tmp_path, monkeypatch)
    provider.release.clear()
    app = create_app(audit)
    client = app.test_client()
    html = client.get("/").get_data(as_text=True)
    assert 'id="auditing"' not in html and "Audit</button>" in html
    setup = client.get("/?reaudit=1").get_data(as_text=True)
    assert 'aria-label="Run audit"' in setup and 'name="rerun"' not in setup
    assert client.post("/auditing", data={}).status_code == 403
    with client.session_transaction() as state:
        csrf = state["csrf"]
    data = {
        "csrf": csrf,
        "provider": "openai",
        "model": "gpt-6-luna",
        "effort": "xhigh",
    }
    invalid = client.post(
        "/auditing", data={**data, "effort": "bad"}, headers={"HX-Request": "true"}
    )
    assert "bad" in invalid.get_data(as_text=True)
    response = client.post("/auditing", data=data, headers={"HX-Request": "true"})
    assert response.headers["HX-Refresh"] == "true"
    progress = client.get("/auditing", headers={"HX-Request": "true"}).get_data(
        as_text=True
    )
    assert "every 5s" in progress and "clipboard-text-clock-outline.svg" in progress
    hidden_progress = client.get(
        "/auditing?reaudit=0", headers={"HX-Request": "true"}
    ).get_data(as_text=True)
    assert (
        'aria-label="Auditing" hidden' in hidden_progress
        and "every 5s" in hidden_progress
    )
    assert "clipboard-text-clock-outline.svg" in client.get("/?reaudit=0").get_data(
        as_text=True
    )
    assert "disabled" in client.get("/").get_data(as_text=True)
    provider.release.set()
    _join(app.extensions["review_auditing"])
    assert (
        client.get("/auditing", headers={"HX-Request": "true"}).headers["HX-Refresh"]
        == "true"
    )
    assert 'aria-label="Run audit"' not in client.get("/").get_data(as_text=True)


@mark.parametrize(
    "findings",
    [
        [],
        [{"index": 1, "status": "unaudited", "note": ""}],
        [{"index": 1, "status": "review", "note": ""}],
        [{"index": 2, "status": "ok", "note": ""}],
        [{"index": 1, "status": "ok", "note": "unexpected"}],
    ],
)
def test_audit_schema_rejects_incomplete_or_ambiguous_findings(
    findings: list[dict[str, object]],
):
    """Reject omissions, wrong indexes, unaudited answers and missing concern notes.

    Arguments:
        findings: invalid structured findings
    """
    with raises(ValidationError):
        ReviewAuditTestCase.model_validate(
            {
                "query": {
                    "language": "eng",
                    "subtitles": [
                        {"index": 1, "original": "Hi.", "proofread": "Hi.", "note": ""}
                    ],
                },
                "answer": {"findings": findings},
            }
        )


def test_reaudit_uses_saved_edits_and_preserves_verified_rows(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Replace all verdicts using current text while retaining verification marks.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline provider replacement
    """
    audit, provider, _ = _setup(tmp_path, monkeypatch)
    job = AuditingJob(audit)
    job.start("openai", "gpt-6-luna", "xhigh")
    _join(job)
    for row in audit.rows():
        audit.save(
            row.key,
            reviewed=f"Edited {row.index}.",
            review_note="Human proofreading",
            notes="Previous audit concern",
            finding="review",
            verified=row.index == 2,
            version=row.version,
        )
    verified = audit.rows()[1]
    paths = [audit.infile_path, audit.outfile_path, audit.json_path]
    before = [p.read_bytes() for p in paths if p is not None]
    provider.queries.clear()
    job.start("openai", "gpt-6-luna", "xhigh", rerun=True)
    _join(job)
    assert job.snapshot().status == "complete", job.snapshot().error
    assert job.snapshot().rerun and job.snapshot().total == 2
    assert len(provider.queries) == 2
    assert [item["proofread"] for item in provider.queries[0]["subtitles"]] == [
        "Edited 1.",
        "Edited 2.",
    ]
    assert provider.queries[0]["subtitles"][0]["original"] == "Hello."
    assert provider.queries[1]["subtitles"][0]["proofread"] == "Edited 3."
    rows = audit.rows()
    assert rows[1].verified == verified.verified
    assert rows[1].reviewed == verified.reviewed
    assert rows[1].review_note == verified.review_note
    assert rows[1].finding == AuditStatus.ok and rows[1].notes == ""
    assert rows[1].version == verified.version + 1
    assert rows[0].notes == "Check this correction against context."
    assert rows[2].finding == AuditStatus.ok and rows[2].notes == ""
    assert rows[2].review_note == "Human proofreading"
    assert before == [p.read_bytes() for p in paths if p is not None]
    for row in rows:
        if not row.verified:
            audit.save(
                row.key,
                reviewed=row.reviewed,
                review_note=row.review_note,
                finding=row.finding,
                notes=row.notes,
                verified=True,
                version=row.version,
            )
    assert all(row.verified for row in audit.rows())
    client = create_app(audit).test_client()
    html = client.get("/").get_data(as_text=True)
    button = html.split("Re-audit</button>")[0].rsplit("<button", 1)[1]
    assert "disabled" not in button
    setup = client.get("/?reaudit=1").get_data(as_text=True)
    assert 'aria-label="Run re-audit (1/3)"' in setup
    provider.queries.clear()
    job.start("openai", "", "", rerun=True)
    _join(job)
    assert job.snapshot().status == "complete", job.snapshot().error
    assert len(provider.queries) == 2
    assert all(row.verified for row in audit.rows())


def test_reaudit_http_is_whole_file_and_keeps_failed_blocks(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Offer explicit setup and retain old findings until fresh responses arrive.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline provider replacement
    """
    audit, provider, _ = _setup(tmp_path, monkeypatch)
    for row in audit.rows():
        audit.save(
            row.key,
            reviewed=row.reviewed,
            review_note="",
            finding="review",
            notes="Old concern",
            verified=False,
            version=row.version,
        )
    app = create_app(audit)
    client = app.test_client()
    html = client.get("/?reaudit=1&q=does-not-match").get_data(as_text=True)
    assert "Re-audit</button>" in html
    assert 'name="rerun" value="on"' in html
    assert 'aria-label="Run re-audit (1/3)"' in html
    assert "clipboard-refresh-outline.svg" in html
    assert provider.queries == []
    assert client.post("/auditing", data={"rerun": "on"}).status_code == 403
    with client.session_transaction() as state:
        csrf = state["csrf"]
    data = {
        "csrf": csrf,
        "provider": "openai",
        "model": "gpt-6-luna",
        "effort": "xhigh",
        "rerun": "on",
    }
    invalid = client.post(
        "/auditing", data={**data, "effort": "bad"}, headers={"HX-Request": "true"}
    )
    assert 'name="rerun" value="on"' in invalid.get_data(as_text=True)
    for _ in range(2):
        prepared = client.post("/auditing", data=data, headers={"HX-Request": "true"})
        assert prepared.status_code == 200
        with client.session_transaction() as state:
            confirmation = state["rerun_confirmations"]["auditing"]
            data["confirmation"] = confirmation["token"]
    ready_at = confirmation["ready_at"]
    monkeypatch.setattr("scinoephile.web.audit_review.app.time", lambda: ready_at + 1)
    provider.release.clear()
    provider.fail_at = 2
    response = client.post(
        "/auditing?q=does-not-match", data=data, headers={"HX-Request": "true"}
    )
    assert response.headers["HX-Refresh"] == "true"
    assert provider.entered.wait(5)
    try:
        assert all(row.notes == "Old concern" for row in audit.rows())
        progress = client.get("/auditing", headers={"HX-Request": "true"})
        assert "Re-auditing 0 of 2" in progress.get_data(as_text=True)
    finally:
        provider.release.set()
        _join(app.extensions["review_auditing"])
    assert len(provider.queries) == 2
    assert audit.rows()[0].notes == "Check this correction against context."
    assert audit.rows()[2].notes == "Old concern"
    error = client.get("/").get_data(as_text=True)
    assert 'aria-label="Run re-audit (1/3)"' in error
    assert "Intentional audit failure" in error


@mark.parametrize(
    "operation,extension,prefix",
    [
        ("auditing", "review_auditing", "clipboard-text-play"),
        ("proofreading", "audit_proofreading", "text-box-play"),
    ],
)
@mark.parametrize("htmx", [False, True])
def test_rerun_confirmation(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    operation: str,
    extension: str,
    prefix: str,
    htmx: bool,
):
    """Enforce three clicks and the delay even without JS; bind consent to settings.

    Arguments:
        tmp_path: temporary subtitle project
        monkeypatch: clock and worker replacements
        operation: protected worker endpoint
        extension: worker application key
        prefix: submit icon family
        htmx: whether the request uses progressive enhancement
    """
    audit, _, _ = _setup(tmp_path, monkeypatch)
    row = audit.rows()[0]
    audit.save(
        row.key,
        reviewed=row.reviewed,
        review_note="",
        finding="ok",
        notes="",
        verified=False,
        version=row.version,
    )
    app = create_app(audit)
    start = Mock()
    monkeypatch.setattr(app.extensions[extension], "start", start)
    now = [1000.0]
    monkeypatch.setattr("scinoephile.web.audit_review.app.time", lambda: now[0])
    client = app.test_client()
    client.get("/")
    with client.session_transaction() as state:
        csrf = state["csrf"]
    data = dict(csrf=csrf, provider="openai", model="model-one", effort="xhigh")
    headers = {}
    if htmx:
        headers["HX-Request"] = "true"
    url = f"/{operation}"
    before = [
        p.read_bytes()
        for p in (audit.infile_path, audit.outfile_path, audit.state_path)
    ]
    first = client.post(url, data=data, headers=headers)
    first_html = first.get_data(as_text=True)
    assert all(
        value in first_html
        for value in (
            "(2/3)",
            f"{prefix}-alert-outline.svg#icon",
            'class="is-confirming"',
        )
    )
    assert "<small>" not in first_html
    with client.session_transaction() as state:
        data["confirmation"] = state["rerun_confirmations"][operation]["token"]
    second = client.post(url, data=data, headers=headers)
    second_html = second.get_data(as_text=True)
    assert all(
        value in second_html
        for value in (
            'data-rerun-ready-at="1003.0"',
            f"{prefix}-double-alert-outline.svg#icon",
            'class="is-confirming"',
        )
    )
    assert "<small>" not in second_html
    with client.session_transaction() as state:
        data["confirmation"] = state["rerun_confirmations"][operation]["token"]
    client.post(url, data=data, headers=headers)
    start.assert_not_called()
    assert before == [
        p.read_bytes()
        for p in (audit.infile_path, audit.outfile_path, audit.state_path)
    ]
    now[0] = 1004.0
    data["model"] = "model-two"
    changed = client.post(url, data=data, headers=headers)
    assert "(2/3)" in changed.get_data(as_text=True)
    start.assert_not_called()
    with client.session_transaction() as state:
        data["confirmation"] = state["rerun_confirmations"][operation]["token"]
    client.post(url, data=data, headers=headers)
    with client.session_transaction() as state:
        data["confirmation"] = state["rerun_confirmations"][operation]["token"]
    now[0] += 3
    client.post(url, data=data, headers=headers)
    start.assert_called_once_with("openai", "model-two", "xhigh", rerun=True)
    start.reset_mock()
    client.post(url, data=data, headers=headers)
    start.assert_not_called()


@mark.parametrize("audited", [False, True])
@mark.parametrize("htmx", [False, True])
def test_operation_panels_toggle_independently(
    tmp_path: Path, monkeypatch: MonkeyPatch, audited: bool, htmx: bool
):
    """Toggle each card independently while data, not visibility, controls reruns.

    Arguments:
        tmp_path: temporary subtitle project
        monkeypatch: offline provider replacements
        audited: whether previous audit findings exist
        htmx: whether the request asks for a workspace fragment
    """
    audit, _, _ = _setup(tmp_path, monkeypatch)
    if audited:
        row = audit.rows()[0]
        audit.save(
            row.key,
            reviewed=row.reviewed,
            review_note="",
            finding="ok",
            notes="",
            verified=False,
            version=row.version,
        )
    client = create_app(audit).test_client()
    headers = {}
    if htmx:
        headers["HX-Request"] = "true"
    closed = client.get("/", headers=headers).get_data(as_text=True)
    assert 'id="proofreading"' not in closed and 'id="auditing"' not in closed
    opened = client.get("/?reproofread=1&reaudit=1", headers=headers).get_data(
        as_text=True
    )
    assert 'id="proofreading"' in opened and 'id="auditing"' in opened
    assert opened.count('aria-expanded="true"') == 2
    assert (
        'name="reproofread" value="0"' in opened
        and 'name="reaudit" value="0"' in opened
    )
    panel = opened.split('<section id="auditing"')[1].split("</section>")[0]
    if audited:
        assert (
            "Re-audit</button>" in opened and "clipboard-refresh-outline.svg" in opened
        )
        assert 'aria-label="Run re-audit (1/3)"' in panel
    else:
        assert "Audit</button>" in opened and "clipboard-text-eye-outline.svg" in opened
        assert 'aria-label="Run audit"' in panel and "data-rerun-icon" not in panel
    proofread_closed = client.get(
        "/?reproofread=0&reaudit=1", headers=headers
    ).get_data(as_text=True)
    assert (
        'id="proofreading"' not in proofread_closed
        and 'id="auditing"' in proofread_closed
    )
    audit_closed = client.get("/?reproofread=1&reaudit=0", headers=headers).get_data(
        as_text=True
    )
    assert 'id="auditing"' not in audit_closed and 'id="proofreading"' in audit_closed
