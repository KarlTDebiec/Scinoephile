#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Run the same proofreading audit from the browser or command line."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from scinoephile.core.llms import LLMProvider, Queryer
from scinoephile.lang.eng.review_audit import ReviewAuditPromptEng
from scinoephile.llms.review_audit import ReviewAuditManager

from .audit_cases import get_audit_query
from .project import ReviewAuditProject
from .rows import AuditRow

__all__ = ["run_audit", "run_audit_selection"]


def run_audit(
    audit: ReviewAuditProject,
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
        rerun: replace previous audit answers
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
        query = test_case_cls.query_cls.model_validate(
            get_audit_query(block).model_dump()
        )
        result = queryer(test_case_cls(query=query))
        audit.publish_audit(block, result, rerun=rerun)
        if on_block is not None:
            on_block()


def run_audit_selection(
    audit: ReviewAuditProject,
    provider: LLMProvider,
    *,
    start_at_idx: int = 0,
    stop_at_idx: int | None = None,
    rerun: bool = False,
    additional_context: str | None = None,
    cache_root_path: Path | None = None,
    overwrite_cache: bool = False,
) -> int:
    """Reserve a selection, audit its blocks, and release the reservation.

    Arguments:
        audit: open proofreading audit project
        provider: configured LLM provider
        start_at_idx: inclusive zero-based first block index
        stop_at_idx: exclusive zero-based end of the block selection
        rerun: replace existing findings for the selected blocks
        additional_context: extra instructions included with each request
        cache_root_path: optional root directory for cached responses
        overwrite_cache: request fresh responses for previously cached blocks
    Returns:
        number of blocks audited
    """
    blocks = audit.begin_auditing(
        rerun=rerun, start_at_idx=start_at_idx, stop_at_idx=stop_at_idx
    )
    try:
        run_audit(
            audit,
            blocks,
            provider,
            rerun=rerun,
            additional_context=additional_context,
            cache_root_path=cache_root_path,
            overwrite_cache=overwrite_cache,
        )
    finally:
        audit.end_auditing()
    return len(blocks)
