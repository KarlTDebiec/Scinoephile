#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Background subtitle audit job using the shared LLM executor."""

from __future__ import annotations

from dataclasses import replace
from functools import partial

from scinoephile.review_audit.project import ReviewAuditProject
from scinoephile.review_audit.rows import AuditStatus
from scinoephile.review_audit.run import run_audit
from scinoephile.web.audit_review.job_settings import get_job_provider
from scinoephile.web.jobs import BackgroundJob

from . import state

__all__ = ["AuditingJob"]


class AuditingJob(BackgroundJob[state.AuditingJobState]):
    """Run independent audits without modifying subtitle text or verification."""

    def __init__(self, audit: ReviewAuditProject):
        """Initialize without contacting a provider.

        Arguments:
            audit: session whose independent audit state will be updated
        """
        self.audit = audit
        """Source-backed session owning independent audit state."""
        super().__init__(state.AuditingJobState(), thread_name="proofreading-audit")

    def snapshot(self) -> state.AuditingJobState:
        """Read progress and whether unaudited subtitles remain.

        Returns:
            immutable audit card state
        """
        with self._lock:
            rows = self.audit.rows()
            available = self.audit.outfile_path.exists() and any(
                row.finding == AuditStatus.unaudited and not row.verified
                for row in rows
            )
            has_output = any(row.finding != AuditStatus.unaudited for row in rows)
            return replace(self._state, available=available, has_output=has_output)

    def start(
        self, provider_name: str, model_name: str, effort: str, *, rerun: bool = False
    ):
        """Validate configuration, reserve current output and start one worker.

        Arguments:
            provider_name: registered provider identifier
            model_name: model override or blank
            effort: shared reasoning level or blank
            rerun: re-audit every subtitle, retaining verification marks
        Raises:
            ValueError: if configuration or session state is invalid
        """
        provider, model_name = get_job_provider(provider_name, model_name, effort)
        with self._lock:
            blocks = self.audit.begin_auditing(rerun=rerun)
            self._start_worker(
                state.AuditingJobState(
                    total=len(blocks),
                    provider=provider_name,
                    model=model_name,
                    effort=effort,
                    rerun=rerun,
                ),
                work=partial(
                    run_audit,
                    self.audit,
                    blocks,
                    provider,
                    rerun=rerun,
                    on_block=self._advance,
                ),
                release=self.audit.end_auditing,
                start_error="Unable to start audit",
            )
