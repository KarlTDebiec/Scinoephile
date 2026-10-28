#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Background independent proofreading audit using the shared LLM executor."""

from __future__ import annotations

from dataclasses import dataclass, replace
from logging import getLogger
from threading import RLock, Thread

from scinoephile.core.llms import LLMProvider, Queryer, ReasoningEffort
from scinoephile.llms.providers.registry import (
    DEFAULT_PROVIDER_NAME,
    get_provider,
    get_provider_names,
)
from scinoephile.llms.review_audit import (
    ReviewAuditQuery,
    ReviewAuditSubtitle,
    ReviewAuditTestCase,
)

from .session import AuditRow, AuditSession, AuditStatus

__all__ = ["AuditingJob", "AuditingState"]

logger = getLogger(__name__)


@dataclass(frozen=True)
class AuditingState:
    """Immutable configuration and progress for the independent audit card."""

    status: str = "ready"
    """Ready, running, complete or error."""
    available: bool = False
    """Whether proofreading exists and unaudited subtitles remain."""
    has_output: bool = False
    """Whether persisted audit findings exist and a new full run would replace them."""
    completed: int = 0
    """Context blocks durably audited in this run."""
    total: int = 0
    """Context blocks selected for this run."""
    provider: str = DEFAULT_PROVIDER_NAME
    """Registered provider selected in the form."""
    model: str = ""
    """Model override, blank for the provider default."""
    effort: str = ""
    """Reasoning override, blank for the provider default."""
    rerun: bool = False
    """Whether this run replaces existing findings across the entire file."""
    error: str = ""
    """Latest failure explanation for retry."""


class AuditingJob:
    """Run independent audits without modifying subtitle text or verification."""

    def __init__(self, audit: AuditSession):
        """Initialize without contacting a provider.

        Arguments:
            audit: session whose independent audit state will be updated
        """
        self.audit = audit
        """Source-backed session owning independent audit state."""
        self._lock = RLock()
        self._state = AuditingState()
        self._thread: Thread | None = None

    def snapshot(self) -> AuditingState:
        """Get current progress and whether unaudited subtitles remain.

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
        if provider_name not in get_provider_names():
            raise ValueError("Choose a supported LLM provider")
        model_name = model_name.strip()
        if len(model_name) > 200 or any(ord(char) < 32 for char in model_name):
            raise ValueError("Use a model identifier of up to 200 characters")
        options: dict[str, str | None] = {"model": model_name or None}
        if effort:
            options["reasoning_effort"] = ReasoningEffort(effort)
        provider = get_provider(provider_name, **options)
        with self._lock:
            blocks = self.audit.begin_auditing(rerun=rerun)
            self._state = AuditingState(
                status="running",
                total=len(blocks),
                provider=provider_name,
                model=model_name,
                effort=effort,
                rerun=rerun,
            )
            try:
                self._thread = Thread(
                    target=self._run,
                    args=(provider, blocks, rerun),
                    daemon=True,
                    name="proofreading-audit",
                )
                self._thread.start()
            except Exception:
                self.audit.end_auditing()
                self._state = replace(
                    self._state, status="error", error="Unable to start audit"
                )
                raise

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
        try:
            queryer = Queryer(
                ReviewAuditTestCase, provider=provider, overwrite_cache=rerun
            )
            for block in blocks:
                query = ReviewAuditQuery(
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
                result = queryer(ReviewAuditTestCase(query=query))
                assert result.answer is not None
                self.audit.publish_audit(
                    block,
                    {
                        item.index: (item.status, item.note)
                        for item in result.answer.findings
                    },
                    rerun=rerun,
                )
                with self._lock:
                    self._state = replace(
                        self._state, completed=self._state.completed + 1
                    )
            with self._lock:
                self._state = replace(self._state, status="complete")
        except Exception as exc:
            logger.exception("Independent proofreading audit failed")
            with self._lock:
                self._state = replace(self._state, status="error", error=str(exc))
        finally:
            self.audit.end_auditing()
