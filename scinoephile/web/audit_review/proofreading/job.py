#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Background proofreading job for a source-backed audit editor."""

from __future__ import annotations

import json
from dataclasses import replace
from functools import partial
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory

from scinoephile.core.llms import LLMProvider
from scinoephile.core.subtitles import Series
from scinoephile.lang.review.standard import get_reviewer
from scinoephile.llms.providers.registry import DEFAULT_PROVIDER_NAME
from scinoephile.llms.review import ReviewProcessor
from scinoephile.review_audit.exceptions import InvalidReviewSubtitleError
from scinoephile.review_audit.project import ReviewAuditProject
from scinoephile.review_audit.proofreading_decisions import ProofreadingDecisions
from scinoephile.web.audit_review.job_settings import get_job_provider
from scinoephile.web.jobs import BackgroundJob

from . import state

__all__ = ["ProofreadingJob"]


class ProofreadingJob(BackgroundJob[state.ProofreadingJobState]):
    """Serialize proofreading starts and expose immutable progress snapshots."""

    def __init__(self, audit: ReviewAuditProject):
        """Initialize a worker owner without starting requests.

        Arguments:
            audit: session whose output may be created
        """
        self.audit = audit
        """Source-backed review session."""
        saved = audit.proofreading_settings
        super().__init__(
            state.ProofreadingJobState(
                provider=saved.get("provider", DEFAULT_PROVIDER_NAME),
                model=saved.get("model", ""),
                effort=saved.get("effort", ""),
            ),
            thread_name="subtitle-proofreading",
        )
        self._refresh_cache = False

    def snapshot(self) -> state.ProofreadingJobState:
        """Read progress and the actual output-file availability.

        Returns:
            immutable proofreading card state
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
        Raises:
            ValueError: if existing decisions contain a revision that cannot be saved
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
            existing = ProofreadingDecisions(
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
            overwrite_cache=self._refresh_cache,
        )
        settings = {
            "provider": self._state.provider,
            "model": self._state.model,
            "effort": self._state.effort,
            "context": context,
        }
        identity = self._get_proofreading_request_identity(reviewer, provider, settings)
        reuse = not rerun or saved.get("request_identity") == identity
        if not reuse and decisions_path.exists():
            decisions_path.unlink()
            reviewer = get_reviewer(
                self.audit.language,
                provider=provider,
                current_test_cases_path=decisions_path,
                additional_context=context or None,
                overwrite_cache=self._refresh_cache,
            )
            identity = self._get_proofreading_request_identity(
                reviewer, provider, settings
            )
        settings["request_identity"] = identity
        existing = ProofreadingDecisions(source, self.audit.language, decisions_path)
        try:
            existing.normalize_srt_revisions()
        except InvalidReviewSubtitleError as exc:
            raise ValueError(
                f"{exc} Correct the existing proofreading decisions before retrying."
            ) from exc
        known = {case.query.key for case in existing.cases if case.answer is not None}
        return reviewer, settings, known

    def _run(self, provider: LLMProvider, rerun: bool, source: Series):
        """Review blocks into temporary decisions, publishing only complete output.

        Arguments:
            provider: configured provider shared across source blocks
            rerun: replace saved output while reusing compatible decisions and caches
            source: current OCR snapshot reserved at the start of this run
        Raises:
            InvalidReviewSubtitleError: if a generated revision cannot be saved
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
                    self._advance()
                self.audit.publish_proofreading(
                    decisions_path, rerun=rerun, settings=settings
                )
        except InvalidReviewSubtitleError:
            self._refresh_cache = True
            raise
        self._refresh_cache = False

    @staticmethod
    def _get_proofreading_request_identity(
        reviewer: ReviewProcessor, provider: LLMProvider, settings: dict[str, str]
    ) -> str:
        """Hash the request configuration to decide whether to reuse saved decisions.

        Arguments:
            reviewer: configured proofreading processor
            provider: effective provider configuration
            settings: requested settings, excluding any previous request identity
        Returns:
            SHA-256 hash of the proofreading request configuration
        """
        provenance = {
            **settings,
            "provider_identity": provider.cache_identity,
            "system_prompt": reviewer.queryer.system_prompt,
            "query_schema": reviewer.test_case_cls.query_cls.model_json_schema(),
            "answer_schema": reviewer.test_case_cls.answer_cls.model_json_schema(),
        }
        return sha256(json.dumps(provenance, sort_keys=True).encode()).hexdigest()
