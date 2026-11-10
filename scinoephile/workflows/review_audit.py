#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Workflow for running a proofreading audit to completion."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from scinoephile.llms.providers.registry import get_provider
from scinoephile.operations.review_audit.project import ReviewAuditProject
from scinoephile.operations.review_audit.run import run_audit

__all__ = ["run_review_audit"]


def run_review_audit(
    audit: ReviewAuditProject,
    *,
    provider_name: str,
    provider_kwargs: Mapping[str, str | None],
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
        provider_name: provider to use for audit requests
        provider_kwargs: provider constructor options
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
        provider = get_provider(provider_name, **provider_kwargs)
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
