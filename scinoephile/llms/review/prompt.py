#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for review matters."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["ReviewPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class ReviewPrompt(Prompt):
    """Text for LLM correspondence for review matters."""

    # Query fields
    subtitles: str = "subtitles"
    """Name of subtitles field in query."""

    subtitles_desc: str = "Subtitles to review, in order."
    """Description of subtitles field in query."""

    # Answer fields
    revisions: str = "revisions"
    """Name of revisions field in answer."""

    revisions_desc: str = (
        "Revised subtitles; include only subtitles that require revision."
    )
    """Description of revisions field in answer."""

    # Subtitle fields
    index: str = "index"
    """Name of index field in subtitle and revision items."""

    index_desc: str = "One-based subtitle index."
    """Description of index field in subtitle and revision items."""

    text: str = "text"
    """Name of text field in subtitle and revision items."""

    subtitle_text_desc: str = "Subtitle text to review."
    """Description of text field in subtitle items."""

    revision_text_desc: str = "Full revised subtitle text."
    """Description of text field in revision items."""

    note: str = "note"
    """Name of note field in revision items."""

    note_desc: str = "Note explaining the revision."
    """Description of note field in revision items."""

    # Query errors
    subtitle_indices_err: str = (
        "Query subtitle indexes must be consecutive, ordered, and begin at 1."
    )
    """Error when query subtitle indexes are invalid."""

    # Answer errors
    revision_indices_err: str = (
        "Answer revision indexes must be unique and in ascending order."
    )
    """Error when answer revision indexes are invalid."""

    # Test case errors
    revision_index_missing_err_tpl: str = (
        "Answer revision index {idx} does not correspond to a query subtitle."
    )
    """Error template when a revision index is absent from the query."""

    revision_unmodified_err_tpl: str = (
        "Answer revision {idx} is unmodified relative to query subtitle {idx}; "
        "unchanged subtitles must be omitted from revisions."
    )
    """Error template when a revision is unmodified."""

    def revision_index_missing_err(self, idx: int) -> str:
        """Get error when a revision index is absent from the query.

        Arguments:
            idx: one-based subtitle index
        Returns:
            error message
        """
        return self.revision_index_missing_err_tpl.format(idx=idx)

    def revision_unmodified_err(self, idx: int) -> str:
        """Get error when a revision is unmodified.

        Arguments:
            idx: one-based subtitle index
        Returns:
            error message
        """
        return self.revision_unmodified_err_tpl.format(idx=idx)
