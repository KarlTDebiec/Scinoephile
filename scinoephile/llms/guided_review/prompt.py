#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for guided review."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["GuidedReviewPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class GuidedReviewPrompt(Prompt):
    """Text for reviewing target blocks using guide blocks."""

    # Query fields
    targets: str = "targets"
    """Name of targets field in query."""

    targets_desc: str = "Target subtitles to review, in order."
    """Description of targets field in query."""

    guides: str = "guides"
    """Name of guides field in query."""

    guides_desc: str = "Guide subtitles for the same passage, in order."
    """Description of guides field in query."""

    # Answer fields
    revisions: str = "revisions"
    """Name of revisions field in answer."""

    revisions_desc: str = (
        "Revised target subtitles; include only targets that require revision."
    )
    """Description of revisions field in answer."""

    # Subtitle fields
    index: str = "index"
    """Name of index field in target, guide, and revision items."""

    index_desc: str = "One-based subtitle index."
    """Description of index field in target, guide, and revision items."""

    text: str = "text"
    """Name of text field in target, guide, and revision items."""

    target_text_desc: str = "Target subtitle text to review."
    """Description of text field in target items."""

    guide_text_desc: str = "Guide subtitle text."
    """Description of text field in guide items."""

    revision_text_desc: str = (
        'Full revised target subtitle text, or "�" to delete the target.'
    )
    """Description of text field in revision items."""

    note: str = "note"
    """Name of note field in revision items."""

    note_desc: str = "Note explaining the target subtitle revision."
    """Description of note field in revision items."""

    # Query errors
    target_indices_err: str = (
        "Query target indexes must be consecutive, ordered, and begin at 1."
    )
    """Error when query target indexes are invalid."""

    guide_indices_err: str = (
        "Query guide indexes must be consecutive, ordered, and begin at 1."
    )
    """Error when query guide indexes are invalid."""

    # Answer errors
    revision_indices_err: str = (
        "Answer revision indexes must be unique and in ascending order."
    )
    """Error when answer revision indexes are invalid."""

    # Test case errors
    revision_index_missing_err_tpl: str = (
        "Answer revision index {idx} does not correspond to a query target."
    )
    """Error template when a revision index is absent from query targets."""

    revision_unmodified_err_tpl: str = (
        "Answer revision {idx} is unmodified relative to query target {idx}; "
        "unchanged targets must be omitted from revisions."
    )
    """Error template when a revision is unmodified."""

    def revision_index_missing_err(self, idx: int) -> str:
        """Get error when a revision index is absent from query targets.

        Arguments:
            idx: one-based target subtitle index
        Returns:
            error message
        """
        return self.revision_index_missing_err_tpl.format(idx=idx)

    def revision_unmodified_err(self, idx: int) -> str:
        """Get error when a revision is unmodified.

        Arguments:
            idx: one-based target subtitle index
        Returns:
            error message
        """
        return self.revision_unmodified_err_tpl.format(idx=idx)
