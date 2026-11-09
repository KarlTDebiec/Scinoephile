#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Run the same proofreading audit from the browser or command line."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from scinoephile.core.llms import LLMProvider, Queryer
from scinoephile.lang.eng.review_audit import ReviewAuditPromptEng
from scinoephile.llms.review_audit import ReviewAuditManager, ReviewAuditSubtitle
from scinoephile.web.audit_review.models import AuditRow
from scinoephile.web.audit_review.session import AuditSession

__all__ = ["run_audit"]


def run_audit(
    audit: AuditSession,
    blocks: tuple[tuple[AuditRow, ...], ...],
    provider: LLMProvider,
    *,
    rerun: bool = False,
    additional_context: str | None = None,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
    on_block: Callable[[], None] | None = None,
):
    """Request findings for reserved context blocks and save each completed block.

    Arguments:
        audit: session with an active audit reservation
        blocks: immutable blocks reserved for this run
        provider: configured LLM provider
        rerun: replace previous verdicts while retaining human verification
        additional_context: extra instructions to include with each request
        cache_root_path: optional root directory for LLM responses
        overwrite_cache: request new answers even when cached responses exist
        on_block: optional progress callback after saving each block
    """
    test_case_cls = ReviewAuditManager.get_test_case_cls(ReviewAuditPromptEng)
    queryer = Queryer(
        test_case_cls,
        provider=provider,
        additional_context=additional_context,
        cache_root_path=cache_root_path,
        overwrite_cache=overwrite_cache,
    )
    for block in blocks:
        query = test_case_cls.query_cls(
            language=audit.language.code,
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
        audit.publish_audit(
            block,
            {item.index: (item.status, item.note) for item in result.answer.findings},
            rerun=rerun,
        )
        if on_block is not None:
            on_block()
