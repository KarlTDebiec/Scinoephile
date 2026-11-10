#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Background proofreading job for a source-backed audit editor."""

from __future__ import annotations

from dataclasses import replace
from functools import partial
from pathlib import Path
from tempfile import TemporaryDirectory

from scinoephile.core.llms import LLMProvider
from scinoephile.core.llms.utils import save_test_cases_to_json
from scinoephile.core.subtitles import Series
from scinoephile.lang.review.standard import get_reviewer
from scinoephile.llms.review import ReviewManager
from scinoephile.operations.review_audit.exceptions import InvalidReviewSubtitleError
from scinoephile.operations.review_audit.project import ReviewAuditProject
from scinoephile.operations.review_audit.proofreading_decisions import (
    ProofreadingDecisions,
)
from scinoephile.web.audit_review.job_settings import get_job_provider
from scinoephile.web.jobs import BackgroundJob

from . import state

__all__ = ["ProofreadingJob"]


class ProofreadingJob(BackgroundJob[state.ProofreadingJobState]):
    """Run proofreading in the background and report progress."""

    def __init__(self, audit: ReviewAuditProject):
        """Set up a proofreading job for the open project.

        Arguments:
            audit: session whose output may be created
        """
        self.audit = audit
        """Subtitle project to proofread."""
        super().__init__(
            state.ProofreadingJobState(), thread_name="subtitle-proofreading"
        )
        self._refresh_cache = False

    def snapshot(self) -> state.ProofreadingJobState:
        """Report progress and whether a first proofreading run is available.

        Returns:
            immutable proofreading card state
        """
        with self._lock:
            return replace(self._state, available=not self.audit.outfile_path.exists())

    def start(
        self, provider_name: str, model_name: str, effort: str, *, rerun: bool = False
    ):
        """Start proofreading the original subtitles in a background thread.

        Arguments:
            provider_name: registered LLM provider
            model_name: optional model identifier override
            effort: shared reasoning level or blank for the provider default
            rerun: replace output using matching reusable results
        Raises:
            ValueError: if configuration or session state prevents a run
        """
        provider, model_name = get_job_provider(provider_name, model_name, effort)
        with self._lock:
            source = self.audit.begin_proofreading(rerun=rerun)
            self._start_worker(
                state.ProofreadingJobState(
                    total=len(source.blocks),
                    provider=provider_name,
                    model=model_name,
                    effort=effort,
                    rerun=rerun,
                ),
                work=partial(self._run, provider, rerun, source),
                release=self.audit.end_proofreading,
                start_error="Unable to start proofreading",
            )

    def _run(self, provider: LLMProvider, rerun: bool, source: Series):
        """Review blocks into temporary decisions, publishing only complete output.

        Arguments:
            provider: configured provider shared across source blocks
            rerun: replace saved output while reusing compatible decisions and caches
            source: original subtitles reserved for this run
        Raises:
            InvalidReviewSubtitleError: if a generated revision cannot be saved
        """
        try:
            with TemporaryDirectory(prefix="scinoephile-review-") as directory:
                decisions_path = Path(directory) / "review.json"
                existing = ProofreadingDecisions(
                    source, self.audit.language, self.audit.proofreading_json_path
                )
                try:
                    existing.normalize_srt_revisions()
                except InvalidReviewSubtitleError as exc:
                    raise ValueError(
                        f"{exc} Correct the existing proofreading decisions "
                        "before retrying."
                    ) from exc
                save_test_cases_to_json(decisions_path, existing.cases, ReviewManager)
                reviewer = get_reviewer(
                    self.audit.language,
                    provider=provider,
                    current_test_cases_path=decisions_path,
                    overwrite_cache=self._refresh_cache,
                )
                for index in range(len(source.blocks)):
                    reviewer.process(source, start_at_idx=index, stop_at_idx=index + 1)
                    self._advance()
                self.audit.publish_proofreading(decisions_path, rerun=rerun)
        except InvalidReviewSubtitleError:
            self._refresh_cache = True
            raise
        self._refresh_cache = False
