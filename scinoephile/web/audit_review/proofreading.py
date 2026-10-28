#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""One background proofreading run for a source-backed audit editor."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import RLock, Thread

from scinoephile.core.llms import LLMProvider, ReasoningEffort
from scinoephile.lang.review.standard import get_reviewer
from scinoephile.llms.providers.registry import (
    DEFAULT_PROVIDER_NAME,
    get_provider,
    get_provider_names,
)

from .session import AuditSession

__all__ = ["ProofreadingJob", "ProofreadingState"]

logger = getLogger(__name__)


@dataclass(frozen=True)
class ProofreadingState:
    """Snapshot of configuration and progress for one local run."""

    status: str = "ready"
    """Ready, running, complete, or error."""
    available: bool = True
    """Whether the configured subtitle output is absent."""
    completed: int = 0
    """Number of completed source blocks."""
    total: int = 0
    """Number of source blocks to proofread."""
    provider: str = DEFAULT_PROVIDER_NAME
    """Selected provider name."""
    model: str = ""
    """Entered model override, blank for the provider default."""
    effort: str = ""
    """Requested reasoning effort, blank for the provider default."""
    rerun: bool = False
    """Whether this run replaces existing proofreading from original OCR."""
    error: str = ""
    """Failure message retained for retry."""


class ProofreadingJob:
    """Serialize proofreading starts and expose immutable progress snapshots."""

    def __init__(self, audit: AuditSession):
        """Initialize a worker owner without starting requests.

        Arguments:
            audit: session whose output may be created
        """
        self.audit = audit
        """Source-backed review session."""
        self._lock = RLock()
        self._state = ProofreadingState()
        self._thread: Thread | None = None

    def snapshot(self) -> ProofreadingState:
        """Read current progress and the actual output-file availability.

        Returns:
            thread-safe progress snapshot
        """
        with self._lock:
            return replace(self._state, available=not self.audit.outfile_path.exists())

    def start(
        self, provider_name: str, model_name: str, effort: str, *, rerun: bool = False
    ):
        """Validate settings and start one background run from the original OCR.

        Arguments:
            provider_name: registered LLM provider
            model_name: optional model identifier override
            effort: shared reasoning level or blank for the provider default
            rerun: generate fresh decisions to replace existing proofreading
        Raises:
            ValueError: if configuration or session state prevents a run
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
            self.audit.begin_proofreading(rerun=rerun)
            self._state = ProofreadingState(
                status="running",
                total=len(self.audit.original.blocks),
                provider=provider_name,
                model=model_name,
                effort=effort,
                rerun=rerun,
            )
            try:
                self._thread = Thread(
                    target=self._run,
                    args=(provider, rerun),
                    daemon=True,
                    name="subtitle-proofreading",
                )
                self._thread.start()
            except Exception:
                self.audit.end_proofreading()
                self._state = replace(
                    self._state, status="error", error="Unable to start proofreading"
                )
                raise

    def _run(self, provider: LLMProvider, rerun: bool):
        """Review blocks into temporary decisions, publishing only complete output.

        Arguments:
            provider: configured provider shared across source blocks
            rerun: bypass old decisions and response caches
        """
        try:
            with TemporaryDirectory(prefix="scinoephile-review-") as directory:
                decisions_path = Path(directory) / "review.json"
                if (
                    not rerun
                    and self.audit.json_path is not None
                    and self.audit.json_path.exists()
                ):
                    decisions_path.write_bytes(self.audit.json_path.read_bytes())
                reviewer = get_reviewer(
                    self.audit.language,
                    provider=provider,
                    current_test_cases_path=decisions_path,
                    overwrite_cache=rerun,
                )
                source = deepcopy(self.audit.original)
                for index in range(len(source.blocks)):
                    reviewer.process(source, start_at_idx=index, stop_at_idx=index + 1)
                    with self._lock:
                        self._state = replace(self._state, completed=index + 1)
                self.audit.publish_proofreading(decisions_path, rerun=rerun)
            with self._lock:
                self._state = replace(self._state, status="complete")
        except Exception as exc:
            logger.exception("Subtitle proofreading failed")
            with self._lock:
                self._state = replace(self._state, status="error", error=str(exc))
        finally:
            self.audit.end_proofreading()
