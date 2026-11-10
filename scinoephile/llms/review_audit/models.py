#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Pydantic models for independent proofreading audits."""

from __future__ import annotations

from typing import ClassVar, Literal, Self

from pydantic import Field, model_validator

from scinoephile.core.llms import Answer, Query, TestCase
from scinoephile.core.llms.models import LLMModel

from .prompt import ReviewAuditPrompt

__all__ = [
    "ReviewAuditAnswer",
    "ReviewAuditFinding",
    "ReviewAuditQuery",
    "ReviewAuditSubtitle",
    "ReviewAuditTestCase",
]


class ReviewAuditSubtitle(LLMModel):
    """One original/proofread pair and its existing proofreading explanation."""

    index: int = Field(ge=1, description="One-based subtitle number in the full input.")
    """One-based subtitle number in the full input."""
    original: str = Field(description="Original subtitle text before proofreading.")
    """Original subtitle text before proofreading."""
    proofread: str = Field(description="Current proofread text to assess.")
    """Current proofread text to assess."""
    note: str = Field(description="Explanation of the proofreading edit, if present.")
    """Explanation of the proofreading edit."""


class ReviewAuditFinding(LLMModel):
    """An explicit audit verdict without authority to change subtitle text."""

    index: int = Field(ge=1, description="Index of the corresponding input subtitle.")
    """One-based subtitle number in the full input."""
    status: Literal["review", "ok"] = Field(
        description="Use review for a concern requiring human attention, otherwise ok."
    )
    """Whether a human should review the subtitle."""
    note: str = Field(description="Concern in English for review, empty for ok.")
    """Specific concern, empty for an OK verdict."""

    @model_validator(mode="after")
    def validate_note(self) -> Self:
        """Require an explanation for Review and none for OK.

        Returns:
            validated finding
        Raises:
            ValueError: if the note contradicts the verdict
        """
        if self.status == "review" and not self.note.strip():
            raise ValueError("Review findings require a note")
        if self.status == "ok" and self.note.strip():
            raise ValueError("OK findings must have an empty note")
        return self


class ReviewAuditQuery(Query):
    """One complete context block for independent proofreading audit."""

    language: str = Field(description="Language code shared by the subtitle pairs.")
    """Language code for all subtitle pairs."""
    subtitles: list[ReviewAuditSubtitle] = Field(
        min_length=1,
        description="Original and proofread subtitle pairs in source order.",
    )
    """Original/proofread pairs in their source order."""

    @model_validator(mode="after")
    def validate_subtitle_indexes(self) -> Self:
        """Require unique subtitle indexes in source order.

        Returns:
            validated audit query
        Raises:
            ValueError: if subtitle indexes repeat or are out of order
        """
        indexes = [subtitle.index for subtitle in self.subtitles]
        if indexes != sorted(set(indexes)):
            raise ValueError("Audit subtitle indexes must be unique and increasing")
        return self


class ReviewAuditAnswer(Answer):
    """Complete per-subtitle findings for one context block."""

    findings: list[ReviewAuditFinding] = Field(
        description="One finding per input subtitle, in the same order."
    )
    """Exactly one finding for every queried subtitle."""


class ReviewAuditTestCase(TestCase[ReviewAuditQuery, ReviewAuditAnswer]):
    """Cacheable audit query and strictly matched findings."""

    operation: ClassVar[str] = "review_audit"
    """Separate cache namespace from proofreading."""
    query_cls: ClassVar[type[ReviewAuditQuery]] = ReviewAuditQuery
    """Query model used by the shared query executor."""
    answer_cls: ClassVar[type[ReviewAuditAnswer]] = ReviewAuditAnswer
    """Structured answer model used by the provider."""
    prompt: ClassVar[ReviewAuditPrompt] = ReviewAuditPrompt()
    """Text for LLM correspondence and validation errors."""
    query: ReviewAuditQuery
    """Context block to assess."""
    answer: ReviewAuditAnswer | None = None
    """Validated audit findings when available."""
    draft: bool = False
    """Whether a human has entered findings for only part of this block."""

    @model_validator(mode="after")
    def validate_findings(self) -> Self:
        """Require full coverage unless the case is a partial human draft.

        Returns:
            matched test case
        Raises:
            ValueError: if indexes are invalid or a draft is marked verified
        """
        if self.draft and (self.answer is None or self.verified):
            raise ValueError("Audit drafts require findings and cannot be verified")
        if self.answer is not None:
            expected = [subtitle.index for subtitle in self.query.subtitles]
            actual = [finding.index for finding in self.answer.findings]
            if self.draft:
                if not 0 < len(actual) < len(expected):
                    raise ValueError("Audit drafts must have some findings missing")
                expected = [index for index in expected if index in actual]
            if actual != expected:
                raise ValueError(self.prompt.finding_indices_err)
        return self
