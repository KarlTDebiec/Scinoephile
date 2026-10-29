#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Offline background proofreading, output publication, and web setup tests."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Event
from typing import Any, Unpack
from unittest.mock import Mock

from pytest import MonkeyPatch, mark, raises

from scinoephile.core import Language
from scinoephile.core.cache.identity import CacheIdentity
from scinoephile.core.llms import Answer, ChatCompletionKwargs, LLMProvider
from scinoephile.core.llms.tool_box import ToolBox
from scinoephile.core.subtitles import Series
from scinoephile.lang.review.standard import get_reviewer
from scinoephile.web.audit_review import proofreading
from scinoephile.web.audit_review.app import create_app
from scinoephile.web.audit_review.proofreading import ProofreadingJob
from scinoephile.web.audit_review.session import AuditSession


class _Provider(LLMProvider):
    """Offline provider exercising the real review processor and native JSON."""

    def __init__(self):
        """Initialize call recording and optional worker gates."""
        self.completion_metrics = []
        self.calls = 0
        self.entered = Event()
        self.release = Event()
        self.release.set()
        self.fail = False
        self.configuration = "default"
        self.queries: list[str] = []

    @property
    def cache_identity(self) -> CacheIdentity:
        """Effective offline request configuration used by the real response cache."""
        return {**super().cache_identity, "configuration": self.configuration}

    def chat_completion(
        self,
        messages: list[dict[str, Any]],
        response_format: type[Answer],
        tool_box: ToolBox | None = None,
        **kwargs: Unpack[ChatCompletionKwargs],
    ) -> str:
        """Return a validated review answer without accessing an API.

        Arguments:
            messages: rendered prompt messages
            response_format: native answer model
            tool_box: unused tool configuration
            **kwargs: request metadata
        Returns:
            structured answer in the prompt's aliases
        Raises:
            RuntimeError: for an intentional provider failure or test timeout
        """
        self.entered.set()
        if not self.release.wait(5):
            raise RuntimeError("Worker gate timed out")
        if self.fail:
            raise RuntimeError("Intentional provider failure")
        self.calls += 1
        self.queries.append(messages[-1]["content"])
        revisions = []
        if self.calls == 1:
            revisions = [
                {"index": 1, "text": "Hello there.", "note": "Corrected wording."}
            ]
        return response_format.model_validate(
            {"revisions": revisions}, by_name=True
        ).model_dump_json(by_alias=True)


def _setup(
    tmp_path: Path, monkeypatch: MonkeyPatch, *, with_json: bool = True
) -> tuple[AuditSession, _Provider, Mock]:
    """Create fresh subtitles and an offline provider for a real background run.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: patched provider factory and shared example loading
        with_json: whether a destination JSON is supplied
    Returns:
        session, offline provider, and recorded provider factory
    """
    infile_path = tmp_path / "source.srt"
    infile_path.write_text(
        "1\n00:00:01,000 --> 00:00:02,000\nHello.\n\n"
        "2\n00:00:10,000 --> 00:00:11,000\nSame.\n",
        encoding="utf-8",
    )
    json_path = None
    if with_json:
        json_path = tmp_path / "review.json"
    audit = AuditSession(
        infile_path,
        tmp_path / "reviewed.srt",
        json_path=json_path,
        language=Language.eng,
    )
    provider = _Provider()
    factory = Mock(return_value=provider)
    monkeypatch.setattr(proofreading, "get_provider", factory)

    def reviewer(*args: Any, **kwargs: Any):
        """Construct the real processor without loading shared training examples.

        Arguments:
            *args: normal language arguments
            **kwargs: native worker configuration
        Returns:
            real review processor
        """
        return get_reviewer(*args, shared_test_cases=[], **kwargs)

    monkeypatch.setattr(proofreading, "get_reviewer", reviewer)
    return audit, provider, factory


def _join(job: ProofreadingJob):
    """Wait for a bounded offline worker completion.

    Arguments:
        job: started background run
    """
    assert job._thread is not None
    job._thread.join(10)
    assert not job._thread.is_alive()


@mark.parametrize("with_json", [False, True])
def test_background_run_publishes_output_and_resumes_notes(
    tmp_path: Path, monkeypatch: MonkeyPatch, with_json: bool
):
    """Publish complete SRT/native decisions, including notes without a JSON path.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline dependency patches
        with_json: whether native JSON output is configured
    """
    audit, provider, factory = _setup(tmp_path, monkeypatch, with_json=with_json)
    original = audit.infile_path.read_bytes()
    job = ProofreadingJob(audit)
    job.start("openai", "gpt-6-luna", "xhigh")
    _join(job)
    assert job.snapshot().status == "complete", job.snapshot().error
    assert job.snapshot().completed == job.snapshot().total == 2
    factory.assert_called_once_with(
        "openai", model="gpt-6-luna", reasoning_effort="xhigh"
    )
    assert provider.calls == 2
    assert [s.text for s in Series.load(audit.outfile_path)] == [
        "Hello there.",
        "Same.",
    ]
    assert audit.infile_path.read_bytes() == original
    resumed = AuditSession(
        audit.infile_path,
        audit.outfile_path,
        json_path=audit.json_path,
        language=Language.eng,
    )
    assert resumed.rows()[0].review_note == "Corrected wording."
    assert resumed.rows()[0].block_number == 1
    with raises(ValueError, match="already exists"):
        job.start("openai", "", "")


def test_running_job_rejects_duplicates_and_edits(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Serialize starts and prevent edits before atomic output publication.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline dependency patches
    """
    audit, provider, _ = _setup(tmp_path, monkeypatch)
    provider.release.clear()
    job = ProofreadingJob(audit)
    job.start("openai", "", "")
    assert provider.entered.wait(5)
    try:
        with raises(ValueError, match="already running"):
            job.start("openai", "", "")
        row = audit.rows()[0]
        with raises(ValueError, match="Wait for proofreading"):
            audit.save(
                row.key,
                reviewed=row.reviewed,
                review_note="",
                notes="",
                finding="ok",
                verified=False,
                version=row.version,
            )
        assert not audit.outfile_path.exists()
    finally:
        provider.release.set()
        _join(job)


def test_failure_and_retry_keep_absent_output(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Failed requests leave source/destination decisions intact and permit retry.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline dependency patches
    """
    audit, provider, _ = _setup(tmp_path, monkeypatch)
    assert audit.json_path is not None
    audit.json_path.write_text("[]\n", encoding="utf-8")
    audit = AuditSession(
        audit.infile_path,
        audit.outfile_path,
        json_path=audit.json_path,
        language=Language.eng,
    )
    provider.fail = True
    job = ProofreadingJob(audit)
    job.start("openai", "", "")
    _join(job)
    assert job.snapshot().status == "error"
    assert not audit.outfile_path.exists()
    assert audit.json_path is not None and audit.json_path.read_text() == "[]\n"
    provider.fail = False
    job.start("openai", "", "")
    _join(job)
    assert job.snapshot().status == "complete"


def test_external_output_is_never_replaced(tmp_path: Path, monkeypatch: MonkeyPatch):
    """Detect output creation during a run instead of overwriting another writer.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline dependency patches
    """
    audit, provider, _ = _setup(tmp_path, monkeypatch)
    provider.release.clear()
    job = ProofreadingJob(audit)
    job.start("openai", "", "")
    assert provider.entered.wait(5)
    audit.outfile_path.write_text("External work", encoding="utf-8")
    provider.release.set()
    _join(job)
    assert job.snapshot().status == "error"
    assert audit.outfile_path.read_text() == "External work"
    assert audit.json_path is not None and not audit.json_path.exists()


def test_card_http_csrf_progress_completion_and_validation(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Run through the protected HTTP form and refresh only after completion.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline dependency patches
    """
    audit, provider, factory = _setup(tmp_path, monkeypatch)
    provider.release.clear()
    app = create_app(audit)
    client = app.test_client()
    client.get("/")
    assert client.post("/proofreading", data={}).status_code == 403
    with client.session_transaction() as session:
        csrf = session["csrf"]
    data = {
        "csrf": csrf,
        "provider": "openai",
        "model": "gpt-6-luna",
        "effort": "xhigh",
    }
    invalid = client.post(
        "/proofreading", data={**data, "effort": "typo"}, headers={"HX-Request": "true"}
    )
    assert invalid.status_code == 409
    factory.assert_not_called()
    response = client.post("/proofreading", data=data, headers={"HX-Request": "true"})
    assert response.status_code == 200 and response.headers["HX-Refresh"] == "true"
    progress = client.get("/proofreading", headers={"HX-Request": "true"}).get_data(
        as_text=True
    )
    assert 'hx-trigger="every 5s"' in progress
    assert provider.entered.wait(5)
    provider.release.set()
    job = app.extensions["audit_proofreading"]
    _join(job)
    assert (
        client.get("/proofreading", headers={"HX-Request": "true"}).headers[
            "HX-Refresh"
        ]
        == "true"
    )


@mark.parametrize("with_json", [False, True])
def test_reproofread_reloads_one_block_and_preserves_progress(
    tmp_path: Path, monkeypatch: MonkeyPatch, with_json: bool
):
    """Reload OCR, reuse unchanged authored blocks, and migrate verified progress.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline dependency patches
        with_json: whether native decisions have a configured destination
    """
    audit, provider, _ = _setup(tmp_path, monkeypatch, with_json=with_json)
    job = ProofreadingJob(audit)
    job.start("openai", "gpt-6-luna", "xhigh")
    _join(job)
    assert provider.calls == 2
    for row in audit.rows():
        text, note = row.reviewed, row.review_note
        if row.index == 1:
            text, note = "Human edited text.", "Human explanation."
        audit.save(
            row.key,
            reviewed=text,
            review_note=note,
            notes="",
            finding="ok",
            verified=True,
            version=row.version,
        )
    old_rows = audit.rows()
    audit.infile_path.write_text(
        audit.infile_path.read_text().replace("Same.", "Corrected OCR."),
        encoding="utf-8",
    )
    assert audit.input_changed
    before = {
        p: p.read_bytes()
        for p in [audit.outfile_path, audit.json_path]
        if p is not None
    }
    provider.fail = True
    job.start("openai", "gpt-6-luna", "xhigh", rerun=True)
    _join(job)
    assert job.snapshot().status == "error"
    assert audit.rows() == old_rows
    assert all(p.read_bytes() == value for p, value in before.items())
    assert not list(tmp_path.glob("*.before-reproofread-*"))
    provider.fail = False
    job.start("openai", "gpt-6-luna", "xhigh", rerun=True)
    _join(job)
    assert job.snapshot().status == "complete", job.snapshot().error
    assert provider.calls == 3
    assert "Corrected OCR." in provider.queries[-1]
    rows = audit.rows()
    assert rows[0].reviewed == "Human edited text."
    assert rows[0].review_note == "Human explanation."
    assert rows[0].verified and rows[0].finding == "ok"
    assert rows[1].original == rows[1].reviewed == "Corrected OCR."
    assert rows[1].finding == "unaudited" and not rows[1].verified
    assert not audit.input_changed
    backups = list(tmp_path.glob("*.before-reproofread-*"))
    assert len(backups) == 1
    assert (backups[0] / "proofread.srt").read_bytes() == before[audit.outfile_path]
    with sqlite3.connect(backups[0] / "review.sqlite3") as db:
        assert (
            db.execute("SELECT COUNT(*) FROM review_edits WHERE verified=1").fetchone()[
                0
            ]
            == 2
        )
    reopened = AuditSession(
        audit.infile_path,
        audit.outfile_path,
        json_path=audit.json_path,
        language=Language.eng,
    )
    assert reopened.rows() == rows
    assert reopened.proofreading_settings["effort"] == "xhigh"
    again = ProofreadingJob(reopened)
    again.start("openai", "gpt-6-luna", "xhigh", rerun=True)
    _join(again)
    assert again.snapshot().status == "complete", again.snapshot().error
    assert provider.calls == 3
    assert reopened.rows()[0].reviewed == "Human edited text."


def test_reproofread_restart_keeps_previous_baseline_until_publication(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Resume progress after OCR changes, then reject further edits during the run.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline dependency patches
    """
    audit, provider, _ = _setup(tmp_path, monkeypatch)
    job = ProofreadingJob(audit)
    job.start("openai", "gpt-6-luna", "xhigh")
    _join(job)
    audit.infile_path.write_text(
        audit.infile_path.read_text().replace("Same.", "New OCR.")
    )
    reopened = AuditSession(
        audit.infile_path,
        audit.outfile_path,
        json_path=audit.json_path,
        language=Language.eng,
    )
    assert reopened.input_changed
    assert reopened.rows()[1].original == "Same."
    old_output = reopened.outfile_path.read_bytes()
    provider.release.clear()
    provider.entered.clear()
    job = ProofreadingJob(reopened)
    job.start("openai", "gpt-6-luna", "xhigh", rerun=True)
    assert provider.entered.wait(5)
    reopened.infile_path.write_text(
        reopened.infile_path.read_text().replace("New OCR.", "Newer OCR.")
    )
    provider.release.set()
    _join(job)
    assert job.snapshot().status == "error"
    assert reopened.outfile_path.read_bytes() == old_output
    assert reopened.rows()[1].original == "Same."


def test_reproofread_changed_configuration_does_not_reuse_native_answers(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Changing model or reasoning invalidates unverified native decision reuse.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline dependency patches
    """
    audit, provider, _ = _setup(tmp_path, monkeypatch)
    job = ProofreadingJob(audit)
    job.start("openai", "model-one", "low")
    _join(job)
    assert provider.calls == 2
    provider.configuration = "different effective model and reasoning"
    job.start("openai", "model-two", "xhigh", rerun=True)
    _join(job)
    assert job.snapshot().status == "complete", job.snapshot().error
    assert provider.calls == 4


def test_reproofread_rejects_structural_input_changes(
    tmp_path: Path, monkeypatch: MonkeyPatch
):
    """Avoid matching old review approvals to different timings or subtitle positions.

    Arguments:
        tmp_path: temporary project directory
        monkeypatch: offline dependency patches
    """
    audit, provider, _ = _setup(tmp_path, monkeypatch)
    job = ProofreadingJob(audit)
    job.start("openai", "gpt-6-luna", "xhigh")
    _join(job)
    audit.infile_path.write_text(
        audit.infile_path.read_text().replace("00:00:10,000", "00:00:09,000")
    )
    with raises(ValueError, match="counts and timings"):
        job.start("openai", "gpt-6-luna", "xhigh", rerun=True)
    assert provider.calls == 2 and not audit.proofreading_running
