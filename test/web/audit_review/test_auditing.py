#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Offline independent audits, durable findings, conflicts and HTTP controls."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from threading import Event
from typing import Any, Unpack
from unittest.mock import Mock

from pydantic import ValidationError
from pytest import MonkeyPatch, mark, raises

from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.core.llms import Answer, ChatCompletionKwargs, LLMProvider
from scinoephile.core.llms.tool_box import ToolBox
from scinoephile.lang.eng.review_audit import ReviewAuditPromptEng
from scinoephile.llms.review_audit import ReviewAuditManager, ReviewAuditQuery
from scinoephile.operations.review_audit.audit_progress import AuditProgress
from scinoephile.operations.review_audit.project import ReviewAuditProject
from scinoephile.operations.review_audit.rows import AuditStatus
from scinoephile.web.audit_review import job_settings
from scinoephile.web.audit_review.app import create_app
from scinoephile.web.audit_review.auditing.job import AuditingJob


class _Provider(LLMProvider):
    """Offline structured audit provider with gates and deterministic failures."""

    def __init__(self):
        """Initialize recorded context and worker controls."""
        self.completion_metrics = []
        self.entered = Event()
        self.release = Event()
        self.release.set()
        self.queries = []
        self.system_prompts: list[str] = []
        self.fail_at = 0
        self.configuration = "default"

    @property
    def cache_identity(self) -> CacheIdentity:
        """Effective offline provider settings included in the response cache."""
        return {**super().cache_identity, "configuration": self.configuration}

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
        self.system_prompts.append(messages[0]["content"])
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
) -> tuple[ReviewAuditProject, _Provider, Mock]:
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
    audit = ReviewAuditProject(
        infile_path, outfile_path, json_path=json_path, language=Language.eng
    )
    provider = _Provider()

    def provider_for_settings(
        provider_name: str,
        *,
        model: str | None = None,
        reasoning_effort: str | None = None,
    ) -> _Provider:
        """Apply requested settings to the offline provider's cache identity.

        Arguments:
            provider_name: requested provider identifier
            model: optional model identifier
            reasoning_effort: optional shared reasoning level
        Returns:
            offline provider with a configuration-aware cache identity
        """
        provider.configuration = json.dumps(
            dict(provider=provider_name, model=model, effort=reasoning_effort),
            sort_keys=True,
        )
        return provider

    factory = Mock(side_effect=provider_for_settings)
    monkeypatch.setattr(job_settings, "get_provider", factory)
    return audit, provider, factory


def _join(job: AuditingJob):
    """Wait for bounded completion of an offline worker.

    Arguments:
        job: running background audit
    """
    assert job._thread is not None
    job._thread.join(15)
    assert not job._thread.is_alive()


def test_audit_commit_serializes_editor_save(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Reject a stale editor save after an overlapping audit commit.

    Arguments:
        tmp_path: temporary project shared by two sessions
        monkeypatch: gate for the first session's write
    """
    audit, _, _ = _setup(tmp_path, monkeypatch)
    editor = ReviewAuditProject(
        audit.infile_path, audit.outfile_path, json_path=audit.json_path
    )
    block = audit.begin_auditing()[0]
    row = editor.rows()[-1]
    writing, release, saving = Event(), Event(), Event()
    write_progress = audit._write_progress

    def hold_commit(progress: AuditProgress, writes: dict[Path, str] | None = None):
        """Pause the audit after its stale-file check.

        Arguments:
            progress: pending audit progress
            writes: optional other files in the commit
        """
        writing.set()
        assert release.wait(5)
        write_progress(progress, writes)

    def save_edit():
        """Attempt to save an independent row from the other session."""
        saving.set()
        editor.save(
            row.key,
            reviewed=row.reviewed,
            review_note=row.review_note,
            notes="Human finding.",
            finding="review",
            verified=True,
            version=row.version,
        )

    monkeypatch.setattr(audit, "_write_progress", hold_commit)
    with ThreadPoolExecutor(max_workers=2) as executor:
        commit = executor.submit(
            audit.publish_audit, block, {item.index: ("ok", "") for item in block}
        )
        try:
            assert writing.wait(5)
            save = executor.submit(save_edit)
            assert saving.wait(5)
            with raises(TimeoutError):
                save.result(timeout=0.25)
        finally:
            release.set()
        commit.result(timeout=5)
        with raises(ValueError, match="outside this session"):
            save.result(timeout=5)
    audit.end_auditing()
    reopened = ReviewAuditProject(
        audit.infile_path, audit.outfile_path, json_path=audit.json_path
    )
    assert all(item.finding == AuditStatus.ok for item in reopened.rows()[: len(block)])
    assert reopened.rows()[-1] == row


def test_audit_progress_is_bound_to_its_language(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Label older JSON on open, preserving findings for the correct language.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline provider replacement
    """
    audit, _, _ = _setup(tmp_path, monkeypatch)
    row = audit.rows()[0]
    audit.save(
        row.key,
        reviewed=row.reviewed,
        review_note=row.review_note,
        notes="Human finding.",
        finding="review",
        verified=True,
        version=row.version,
    )
    progress = json.loads(audit.state_path.read_bytes())
    assert progress.pop("language") == "eng"
    audit.state_path.write_text(json.dumps(progress), encoding="utf-8")

    reopened = ReviewAuditProject(
        audit.infile_path,
        audit.outfile_path,
        json_path=audit.json_path,
        language=Language.eng,
    )
    assert reopened.rows() == audit.rows()
    assert json.loads(audit.state_path.read_bytes())["language"] == "eng"
    before = audit.state_path.read_bytes()
    with raises(ScinoephileError, match="Audit progress uses language eng"):
        ReviewAuditProject(
            audit.infile_path, audit.outfile_path, language=Language.yue_hant
        )
    assert audit.state_path.read_bytes() == before


def test_cli_audit_resumes_in_the_browser(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Run direct LLM requests for selected blocks and resume saved findings.

    Arguments:
        tmp_path: temporary project and response cache
        monkeypatch: offline provider replacement
    """
    audit, provider, factory = _setup(tmp_path, monkeypatch)
    monkeypatch.setattr("scinoephile.workflows.review_audit.get_provider", factory)
    context = tmp_path / "context.txt"
    context.write_text("Check names.", encoding="utf-8")
    assert audit.json_path is not None
    arguments = (
        f'audit review run --original "{audit.infile_path}" '
        f'--reviewed "{audit.outfile_path}" --json "{audit.json_path}" '
        f'--cache-dir "{tmp_path / "cache"}" '
        f'--llm-additional-context-file "{context}" --llm-provider openai '
        "--language eng --llm-model gpt-6-luna --llm-reasoning-effort xhigh"
    )
    files = (audit.infile_path, audit.outfile_path, audit.json_path)
    before = [path.read_bytes() for path in files]
    run_cli_with_args(ScinoephileCli, f"{arguments} --first-block 2 --last-block 2")
    assert [subtitle["index"] for subtitle in provider.queries[0]["subtitles"]] == [3]
    assert "Check names." in provider.system_prompts[0]
    factory.assert_called_once_with(
        "openai", model="gpt-6-luna", reasoning_effort="xhigh"
    )
    run_cli_with_args(ScinoephileCli, arguments)
    assert len(provider.queries) == 2
    assert [subtitle["index"] for subtitle in provider.queries[1]["subtitles"]] == [
        1,
        2,
    ]
    assert [path.read_bytes() for path in files] == before

    reopened = ReviewAuditProject(
        audit.infile_path,
        audit.outfile_path,
        json_path=audit.json_path,
        language=Language.eng,
    )
    assert [row.finding for row in reopened.rows()] == [
        AuditStatus.review,
        AuditStatus.ok,
        AuditStatus.ok,
    ]
    client = create_app(reopened).test_client()
    assert b"Check this correction against context." in client.get("/").data


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
    assert provider.system_prompts == [ReviewAuditPromptEng.base_system_prompt] * 2
    assert [row.finding for row in audit.rows()] == [
        AuditStatus.review,
        AuditStatus.review,
        AuditStatus.ok,
    ]
    assert audit.rows()[1].verified and audit.rows()[1].notes == "Human finding"
    assert not audit.rows()[0].verified and not audit.rows()[2].verified
    assert before == [p.read_bytes() for p in paths if p is not None]
    restored = ReviewAuditProject(
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
    app = create_app(audit)
    job = app.extensions["review_auditing"]
    client = app.test_client()
    client.get("/?reaudit=1")
    with client.session_transaction() as state:
        data = dict(csrf=state["csrf"], provider="openai", model="", effort="")
    assert client.post("/auditing", data=data).status_code == 303
    _join(job)
    assert job.snapshot().status == "error" and job.snapshot().completed == 1
    assert audit.rows()[2].finding == AuditStatus.unaudited
    first = audit.rows()[0]
    audit.save(
        first.key,
        reviewed=first.reviewed,
        review_note=first.review_note,
        finding="review",
        notes="Human finding",
        verified=True,
        version=first.version,
    )
    before = audit.rows()[:2]
    page = client.get("/").get_data(as_text=True)
    assert "Resume audit" in page and "Run full re-audit" in page
    rerun = dict(data, rerun="on")
    for _ in range(2):
        assert client.post("/auditing", data=rerun).status_code == 200
        with client.session_transaction() as state:
            confirmation = state["rerun_confirmations"]["auditing"]
            rerun["confirmation"] = confirmation["token"]
    assert confirmation["stage"] == 2
    provider.fail_at = 0
    assert client.post("/auditing", data=data).status_code == 303
    with client.session_transaction() as state:
        assert "auditing" not in state["rerun_confirmations"]
    _join(job)
    assert job.snapshot().status == "complete" and job.snapshot().total == 1
    assert [s["index"] for s in provider.queries[-1]["subtitles"]] == [3]
    assert audit.rows()[:2] == before


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
    """Reject unauthorized requests and poll background audit completion.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline provider replacement
    """
    audit, provider, factory = _setup(tmp_path, monkeypatch)
    provider.release.clear()
    app = create_app(audit)
    client = app.test_client()
    client.get("/")
    assert client.post("/auditing", data={}).status_code == 403
    with client.session_transaction() as state:
        csrf = state["csrf"]
    data = {
        "csrf": csrf,
        "provider": "openai",
        "model": "gpt-6-luna",
        "effort": "xhigh",
    }
    client.post(
        "/auditing", data={**data, "effort": "bad"}, headers={"HX-Request": "true"}
    )
    factory.assert_not_called()
    response = client.post("/auditing", data=data, headers={"HX-Request": "true"})
    assert response.headers["HX-Refresh"] == "true"
    progress = client.get("/auditing", headers={"HX-Request": "true"}).get_data(
        as_text=True
    )
    assert 'hx-trigger="every 5s"' in progress
    provider.release.set()
    _join(app.extensions["review_auditing"])
    assert (
        client.get("/auditing", headers={"HX-Request": "true"}).headers["HX-Refresh"]
        == "true"
    )


@mark.parametrize("indexes", [(7, 7), (7, 4)])
def test_audit_query_rejects_duplicate_or_reordered_subtitles(indexes: tuple[int, int]):
    """Reject ambiguous subtitle indexes before requesting findings.

    Arguments:
        indexes: duplicate or reordered full-track subtitle indexes
    """
    with raises(
        ValidationError, match="subtitle indexes must be unique and increasing"
    ):
        ReviewAuditQuery.model_validate(
            {
                "language": "eng",
                "subtitles": [
                    {"index": index, "original": "Hi.", "proofread": "Hi.", "note": ""}
                    for index in indexes
                ],
            }
        )


@mark.parametrize(
    ("findings", "message"),
    [
        ([], "Match the query indexes"),
        ([{"index": 1, "status": "unaudited", "note": ""}], "Input should be"),
        (
            [{"index": 1, "status": "review", "note": ""}],
            "Review findings require a note",
        ),
        ([{"index": 2, "status": "ok", "note": ""}], "Match the query indexes"),
        (
            [{"index": 1, "status": "ok", "note": "unexpected"}],
            "OK findings must have an empty note",
        ),
    ],
)
def test_audit_schema_rejects_incomplete_or_ambiguous_findings(
    findings: list[dict[str, object]], message: str
):
    """Reject omissions, wrong indexes, unaudited answers and missing concern notes.

    Arguments:
        findings: invalid structured findings
        message: expected validation feedback
    """
    prompt = replace(
        ReviewAuditPromptEng, finding_indices_err="Match the query indexes"
    )
    test_case_cls = ReviewAuditManager.get_test_case_cls(prompt)
    with raises(ValidationError, match=message):
        test_case_cls.model_validate(
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


@mark.parametrize("change", ["proofread", "note", "model", "reasoning"])
def test_reaudit_reuses_cache_and_invalidates_changed_inputs(
    tmp_path: Path, monkeypatch: MonkeyPatch, change: str
):
    """Reuse persisted responses and request only blocks whose inputs changed.

    Arguments:
        tmp_path: temporary project directory and isolated response cache
        monkeypatch: offline provider factory replacement
        change: changed block content or provider setting
    """
    audit, provider, _ = _setup(tmp_path, monkeypatch)
    if change == "note":
        row = audit.rows()[0]
        audit.save(
            row.key,
            reviewed="Hello!",
            review_note="Initial punctuation correction",
            notes="",
            finding="unaudited",
            verified=False,
            version=row.version,
        )
    job = AuditingJob(audit)
    job.start("openai", "gpt-6-luna", "xhigh")
    _join(job)
    assert job.snapshot().status == "complete", job.snapshot().error
    assert len(provider.queries) == 2
    provider.queries.clear()
    audit = ReviewAuditProject(
        audit.infile_path,
        audit.outfile_path,
        json_path=audit.json_path,
        language=Language.eng,
    )
    job = AuditingJob(audit)
    job.start("openai", "gpt-6-luna", "xhigh", rerun=True)
    _join(job)
    assert job.snapshot().status == "complete", job.snapshot().error
    assert job.snapshot().total == job.snapshot().completed == 2
    assert provider.queries == []

    model = "gpt-6-luna"
    effort = "xhigh"
    expected_calls = 2
    if change in {"proofread", "note"}:
        row = audit.rows()[0]
        text = "Hello again."
        if change == "note":
            text = row.reviewed
        audit.save(
            row.key,
            reviewed=text,
            review_note="A new proofreading explanation",
            notes=row.notes,
            finding=row.finding,
            verified=row.verified,
            version=row.version,
        )
        expected_calls = 1
    elif change == "model":
        model = "other-model"
    else:
        effort = "high"
    job.start("openai", model, effort, rerun=True)
    _join(job)
    assert job.snapshot().status == "complete", job.snapshot().error
    assert len(provider.queries) == expected_calls
    if expected_calls == 1:
        assert [item["index"] for item in provider.queries[0]["subtitles"]] == [1, 2]


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
    client.get("/?reaudit=1&q=does-not-match")
    with client.session_transaction() as state:
        csrf = state["csrf"]
    data = {
        "csrf": csrf,
        "provider": "openai",
        "model": "gpt-6-luna",
        "effort": "xhigh",
        "rerun": "on",
    }
    for _ in range(2):
        prepared = client.post("/auditing", data=data, headers={"HX-Request": "true"})
        assert prepared.status_code == 200
        with client.session_transaction() as state:
            confirmation = state["rerun_confirmations"]["auditing"]
            data["confirmation"] = confirmation["token"]
    ready_at = confirmation["ready_at"]
    monkeypatch.setattr(
        "scinoephile.web.audit_review.rerun_confirmation.time", lambda: ready_at + 1
    )
    provider.release.clear()
    provider.fail_at = 2
    response = client.post(
        "/auditing?q=does-not-match", data=data, headers={"HX-Request": "true"}
    )
    assert response.headers["HX-Refresh"] == "true"
    assert provider.entered.wait(5)
    try:
        assert all(row.notes == "Old concern" for row in audit.rows())
    finally:
        provider.release.set()
        _join(app.extensions["review_auditing"])
    assert len(provider.queries) == 2
    assert audit.rows()[0].notes == "Check this correction against context."
    assert audit.rows()[2].notes == "Old concern"
    error = client.get("/").get_data(as_text=True)
    assert "Intentional audit failure" in error


@mark.parametrize(
    "operation,extension",
    [("auditing", "review_auditing"), ("proofreading", "audit_proofreading")],
)
def test_rerun_confirmation(
    tmp_path: Path, monkeypatch: MonkeyPatch, operation: str, extension: str
):
    """Enforce three clicks and the delay even without JS; bind consent to settings.

    Arguments:
        tmp_path: temporary subtitle project
        monkeypatch: clock and worker replacements
        operation: protected worker endpoint
        extension: worker application key
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
    monkeypatch.setattr(
        "scinoephile.web.audit_review.rerun_confirmation.time", lambda: now[0]
    )
    client = app.test_client()
    client.get("/")
    with client.session_transaction() as state:
        csrf = state["csrf"]
    data = dict(
        csrf=csrf, provider="openai", model="model-one", effort="xhigh", rerun="on"
    )
    url = f"/{operation}"
    before = [
        p.read_bytes()
        for p in (audit.infile_path, audit.outfile_path, audit.state_path)
    ]
    assert client.post(url, data=data).status_code == 200
    with client.session_transaction() as state:
        data["confirmation"] = state["rerun_confirmations"][operation]["token"]
    assert client.post(url, data=data).status_code == 200
    with client.session_transaction() as state:
        data["confirmation"] = state["rerun_confirmations"][operation]["token"]
    client.post(url, data=data)
    start.assert_not_called()
    assert before == [
        p.read_bytes()
        for p in (audit.infile_path, audit.outfile_path, audit.state_path)
    ]
    now[0] = 1004.0
    data["model"] = "model-two"
    assert client.post(url, data=data).status_code == 200
    start.assert_not_called()
    with client.session_transaction() as state:
        data["confirmation"] = state["rerun_confirmations"][operation]["token"]
    client.post(url, data=data)
    with client.session_transaction() as state:
        data["confirmation"] = state["rerun_confirmations"][operation]["token"]
    now[0] += 3
    client.post(url, data=data)
    start.assert_called_once_with("openai", "model-two", "xhigh", rerun=True)
    start.reset_mock()
    client.post(url, data=data)
    start.assert_not_called()


@mark.parametrize("operation", ["proofreading", "auditing"])
def test_operation_settings_remain_accessible_during_other_job(
    tmp_path: Path, monkeypatch: MonkeyPatch, operation: str
):
    """Keep settings accessible while reserving execution for the active worker.

    Arguments:
        tmp_path: temporary subtitle project
        monkeypatch: offline provider replacements
        operation: settings panel to open while the other operation runs
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
    client = create_app(audit).test_client()
    headers = {"HX-Request": "true"}
    toggle = "reaudit"
    if operation == "proofreading":
        toggle = "reproofread"
        audit.begin_auditing(rerun=True)
    else:
        audit.begin_proofreading(rerun=True)
    closed = client.get("/", headers=headers).get_data(as_text=True)
    button = closed.split(f"data-{toggle}>")[1].split("<button")[1].split(">")[0]
    assert 'aria-expanded="false"' in button and "disabled" not in button
    opened = client.get(f"/?{toggle}=1", headers=headers).get_data(as_text=True)
    panel = opened.split(f'<section id="{operation}"')[1].split("</section>")[0]
    assert " hidden" not in panel.split(">")[0]
    assert 'name="model"' in panel
    assert "disabled" in panel.split("<button")[1].split(">")[0]
    if operation == "proofreading":
        with raises(ValueError, match="already running"):
            audit.begin_proofreading(rerun=True)
        audit.end_auditing()
    else:
        with raises(ValueError, match="current operation"):
            audit.begin_auditing(rerun=True)
        audit.end_proofreading()
    ready = client.get(f"/?{toggle}=1", headers=headers).get_data(as_text=True)
    panel = ready.split(f'<section id="{operation}"')[1].split("</section>")[0]
    assert "disabled" not in panel.split("<button")[1].split(">")[0]
