#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""One background proofreading run for a source-backed audit editor."""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from hashlib import sha256
from logging import getLogger
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import RLock, Thread

from scinoephile.core.llms import LLMProvider, ReasoningEffort
from scinoephile.core.subtitles import Series
from scinoephile.lang.review.standard import get_reviewer
from scinoephile.llms.providers.registry import (
    DEFAULT_PROVIDER_NAME,
    get_provider,
    get_provider_names,
)
from scinoephile.llms.review import ReviewProcessor

from .decisions import ReviewDecisions
from .session import AuditSession

__all__ = ["ProofreadingJob", "ProofreadingState", "get_proofreading_request_identity"]

logger = getLogger(__name__)


def get_proofreading_request_identity(
    reviewer: ReviewProcessor, provider: LLMProvider, settings: dict[str, str]
) -> str:
    """Identify the request configuration associated with authored decisions.

    Arguments:
        reviewer: configured proofreading processor and shared examples
        provider: effective non-secret provider configuration
        settings: requested settings, excluding any previous request identity
    Returns:
        provenance digest; response-cache ownership remains with the query executor
    """
    provenance = {
        **settings,
        "provider_identity": provider.cache_identity,
        "system_prompt": reviewer.queryer.system_prompt,
        "query_schema": reviewer.test_case_cls.query_cls.model_json_schema(),
        "answer_schema": reviewer.test_case_cls.answer_cls.model_json_schema(),
    }
    return sha256(json.dumps(provenance, sort_keys=True).encode()).hexdigest()


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
        saved = audit.proofreading_settings
        self._state = ProofreadingState(
            provider=saved.get("provider", DEFAULT_PROVIDER_NAME),
            model=saved.get("model", ""),
            effort=saved.get("effort", ""),
        )
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
            rerun: replace output using current OCR and matching reusable results
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
            source = self.audit.begin_proofreading(rerun=rerun)
            self._state = ProofreadingState(
                status="running",
                total=len(source.blocks),
                provider=provider_name,
                model=model_name,
                effort=effort,
                rerun=rerun,
            )
            try:
                self._thread = Thread(
                    target=self._run,
                    args=(provider, rerun, source),
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

    def _prepare_reviewer(
        self, provider: LLMProvider, source: Series, decisions_path: Path, rerun: bool
    ) -> tuple[ReviewProcessor, dict[str, str], set[tuple]]:
        """Prepare native decisions and determine which answered queries remain valid.

        Arguments:
            provider: effective provider for this run
            source: freshly loaded OCR snapshot
            decisions_path: temporary native decision log
            rerun: whether existing output is being replaced
        Returns:
            reviewer, run provenance, and reusable authored query keys
        """
        saved = self.audit.proofreading_settings
        context = saved.get("context", "")
        if self.audit.json_path is not None and self.audit.json_path.exists():
            decisions_path.write_bytes(self.audit.json_path.read_bytes())
        elif self.audit.decisions is not None:
            decisions_path.write_text(
                self.audit.decisions.serialize(), encoding="utf-8"
            )
        elif self.audit.outfile_path.exists():
            existing = ReviewDecisions(
                self.audit.original, self.audit.language, decisions_path
            )
            for row in self.audit.rows():
                if row.changed:
                    existing.edit(row.index - 1, row.reviewed, row.review_note)
            decisions_path.write_text(existing.serialize(), encoding="utf-8")
        reviewer = get_reviewer(
            self.audit.language,
            provider=provider,
            current_test_cases_path=decisions_path,
            additional_context=context or None,
            overwrite_cache=False,
        )
        settings = {
            "provider": self._state.provider,
            "model": self._state.model,
            "effort": self._state.effort,
            "context": context,
        }
        identity = get_proofreading_request_identity(reviewer, provider, settings)
        reuse = not rerun or saved.get("request_identity") == identity
        if not reuse and decisions_path.exists():
            decisions_path.unlink()
            reviewer = get_reviewer(
                self.audit.language,
                provider=provider,
                current_test_cases_path=decisions_path,
                additional_context=context or None,
                overwrite_cache=False,
            )
            identity = get_proofreading_request_identity(reviewer, provider, settings)
        settings["request_identity"] = identity
        known = {
            case.query.key
            for case in ReviewDecisions(
                source, self.audit.language, decisions_path
            ).cases
            if case.answer is not None
        }
        return reviewer, settings, known

    def _run(self, provider: LLMProvider, rerun: bool, source: Series):
        """Review blocks into temporary decisions, publishing only complete output.

        Arguments:
            provider: configured provider shared across source blocks
            rerun: replace saved output while reusing compatible decisions and caches
            source: current OCR snapshot reserved at the start of this run
        """
        try:
            with TemporaryDirectory(prefix="scinoephile-review-") as directory:
                decisions_path = Path(directory) / "review.json"
                reviewer, settings, known = self._prepare_reviewer(
                    provider, source, decisions_path, rerun
                )
                for index, block in enumerate(source.blocks):
                    query = reviewer.test_case_cls.query_cls.model_validate(
                        {
                            "subtitles": [
                                {
                                    "index": number,
                                    "text": subtitle.text_with_newline.strip(),
                                }
                                for number, subtitle in enumerate(block, 1)
                            ]
                        }
                    )
                    if query.key not in known:
                        reviewer.process(
                            source, start_at_idx=index, stop_at_idx=index + 1
                        )
                    with self._lock:
                        self._state = replace(self._state, completed=index + 1)
                self.audit.publish_proofreading(
                    decisions_path, rerun=rerun, settings=settings
                )
            with self._lock:
                self._state = replace(self._state, status="complete")
        except Exception as exc:
            logger.exception("Subtitle proofreading failed")
            with self._lock:
                self._state = replace(self._state, status="error", error=str(exc))
        finally:
            self.audit.end_proofreading()
