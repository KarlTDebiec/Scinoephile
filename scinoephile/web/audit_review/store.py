#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""JSON representation of saved audit progress."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace
from typing import Annotated, Self

from pydantic import BaseModel, Field

from .models import AuditRow, AuditStatus

__all__ = ["AuditProgress", "SavedAuditRow"]


class SavedAuditRow(BaseModel):
    """Progress for a specific proofread version of a subtitle."""

    reviewed: str
    """Proofread text to which the audit applies."""
    review_note: str
    """Proofreading explanation at the time of the audit."""
    notes: str
    """Independent audit notes."""
    finding: AuditStatus
    """Independent audit verdict."""
    verified: bool
    """Whether a human has checked the subtitle."""
    version: int = Field(ge=0)
    """Version used to reject stale edits."""


class AuditProgress(BaseModel):
    """Published source and independently editable audit findings."""

    source: list[str]
    """Exact original SRT split into lines for readable Git diffs."""
    proofreading: dict[str, str] = Field(default_factory=dict)
    """Settings and provenance for the last published proofreading run."""
    rows: dict[Annotated[int, Field(ge=1)], SavedAuditRow] = Field(default_factory=dict)
    """Saved findings keyed by one-based subtitle number."""

    def apply(self, rows: list[AuditRow], *, match_review_note: bool) -> list[AuditRow]:
        """Restore versions and progress that still applies to each subtitle.

        Arguments:
            rows: current rows built from subtitle and proofreading files
            match_review_note: whether the saved note must match native decisions
        Returns:
            current rows with applicable saved progress
        """
        loaded = []
        for row in rows:
            saved = self.rows.get(row.index)
            current = row
            if saved is not None:
                current = replace(row, version=saved.version)
                if saved.reviewed == row.reviewed and (
                    not match_review_note or saved.review_note == row.review_note
                ):
                    current = replace(
                        current,
                        review_note=saved.review_note,
                        notes=saved.notes,
                        finding=saved.finding,
                        verified=saved.verified,
                    )
            loaded.append(current)
        return loaded

    def with_rows(self, rows: Iterable[AuditRow]) -> Self:
        """Create a candidate snapshot with the supplied subtitle updates.

        Arguments:
            rows: rows to save with their final version numbers
        Returns:
            updated progress with subtitle keys in numeric order
        """
        saved = self.rows.copy()
        for row in rows:
            saved[row.index] = SavedAuditRow(
                reviewed=row.reviewed,
                review_note=row.review_note,
                notes=row.notes,
                finding=row.finding,
                verified=row.verified,
                version=row.version,
            )
        return self.model_copy(update={"rows": dict(sorted(saved.items()))})
