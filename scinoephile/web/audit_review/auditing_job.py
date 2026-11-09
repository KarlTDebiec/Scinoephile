#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Background subtitle audit job using the shared LLM executor."""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import partial

from scinoephile.core.llms import LLMProvider, Queryer
from scinoephile.lang.eng.review_audit import ReviewAuditPromptEng
from scinoephile.llms.providers.registry import DEFAULT_PROVIDER_NAME
from scinoephile.llms.review_audit import ReviewAuditManager, ReviewAuditSubtitle
from scinoephile.web.jobs import BackgroundJob, BackgroundJobState

from .job_settings import get_job_provider
from .models import AuditRow, AuditStatus
from .session import AuditSession

__all__ = ["AuditingJob", "AuditingState"]


@dataclass(frozen=True)
class AuditingState(BackgroundJobState):
    """Immutable configuration and progress for the independent audit card."""

    available: bool = False
    """Whether proofreading exists and unaudited subtitles remain."""
    has_output: bool = False
    """Whether persisted audit findings exist and a new full run would replace them."""
    provider: str = DEFAULT_PROVIDER_NAME
    """Registered provider selected in the form."""
    model: str = ""
    """Model override, blank for the provider default."""
    effort: str = ""
    """Reasoning override, blank for the provider default."""
    rerun: bool = False
    """Whether this run replaces existing findings across the entire file."""


class AuditingJob(BackgroundJob[AuditingState]):
    """Run independent audits without modifying subtitle text or verification."""

    def __init__(self, audit: AuditSession):
        """Initialize without contacting a provider.

        Arguments:
            audit: session whose independent audit state will be updated
        """
        self.audit = audit
        """Source-backed session owning independent audit state."""
        super().__init__(AuditingState(), thread_name="proofreading-audit")

    def snapshot(self) -> AuditingState:
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
                AuditingState(
                    total=len(blocks),
                    provider=provider_name,
                    model=model_name,
                    effort=effort,
                    rerun=rerun,
                ),
                work=partial(self._run, provider, blocks, rerun),
                release=self.audit.end_auditing,
                start_error="Unable to start audit",
            )

    def _run(
        self,
        provider: LLMProvider,
        blocks: tuple[tuple[AuditRow, ...], ...],
        rerun: bool,
    ):
        """Audit full context blocks and persist each completed block independently.

        Arguments:
            provider: configured provider shared across requests
            blocks: immutable reserved context blocks
            rerun: replace all findings, retaining verification marks
        """
        test_case_cls = ReviewAuditManager.get_test_case_cls(ReviewAuditPromptEng)
        queryer = Queryer(test_case_cls, provider=provider)
        for block in blocks:
            query = test_case_cls.query_cls(
                language=self.audit.language.code,
                subtitles=[
                    ReviewAuditSubtitle(
                        index=row.index,
                        original=row.original,
                        proofread=row.reviewed,
                        note=row.review_note,
                    )
                    for row in block
                ],
            )
            result = queryer(test_case_cls(query=query))
            assert result.answer is not None
            self.audit.publish_audit(
                block,
                {
                    item.index: (item.status, item.note)
                    for item in result.answer.findings
                },
                rerun=rerun,
            )
            self._advance()
