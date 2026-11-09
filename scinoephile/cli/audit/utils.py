#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Utilities for subtitle audit command-line interfaces."""

from __future__ import annotations

from argparse import ArgumentParser
from collections.abc import Sequence
from enum import StrEnum
from pathlib import Path

from scinoephile.analysis.audit.review import ReviewAuditFilters
from scinoephile.core.llms import TestCase
from scinoephile.lang.zho.script.conversion import get_zho_character_variants
from scinoephile.llms.review import ReviewManager

from .audit_cli_base import AuditCliBase

__all__ = ["build_review_audit_filters", "load_review_test_cases"]


def build_review_audit_filters(
    *,
    row_filter: StrEnum,
    character_filter: Sequence[str],
    first_index: int | None,
    last_index: int | None,
    first_block: int | None,
    last_block: int | None,
) -> ReviewAuditFilters:
    """Build review filters from parsed options, including Chinese script variants.

    Arguments:
        row_filter: selected row status filter
        character_filter: character arguments before script expansion
        first_index: first included one-based subtitle index
        last_index: last included one-based subtitle index
        first_block: first included one-based block number
        last_block: last included one-based block number
    Returns:
        validated review audit filters
    """
    characters = ()
    if character_filter:
        characters = get_zho_character_variants(character_filter)
    return ReviewAuditFilters(
        row_filter=row_filter,
        character_filter=characters,
        first_index=first_index,
        last_index=last_index,
        first_block=first_block,
        last_block=last_block,
    )


def load_review_test_cases(
    parser: ArgumentParser, json_path: Path | None
) -> Sequence[TestCase]:
    """Load optional review test cases from JSON.

    Arguments:
        parser: parser used to report user-facing errors
        json_path: optional review JSON path
    Returns:
        loaded review test cases
    """
    if json_path is None:
        return ()
    return AuditCliBase.load_test_cases(
        parser, json_path, ReviewManager, workflow_name="review"
    )
