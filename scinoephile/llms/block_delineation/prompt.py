#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for block-level transcription delineation."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["BlockDelineationPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class BlockDelineationPrompt(Prompt):
    """Text and field aliases for block-level delineation."""

    guides: str = "guides"
    """Name of guide subtitles field in query."""
    guides_desc: str = "Complete indexed guide subtitles for one block."
    """Description of guide subtitles field in query."""
    targets: str = "targets"
    """Name of initial target subtitles field in query."""
    targets_desc: str = "Complete indexed initial target assignment for one block."
    """Description of initial target subtitles field in query."""
    changes: str = "changes"
    """Name of sparse target changes field in answer."""
    changes_desc: str = "Only target subtitles whose text must change."
    """Description of sparse target changes field in answer."""
    index: str = "index"
    """Name of index field in subtitle items."""
    index_desc: str = "One-based guide subtitle index."
    """Description of subtitle item indexes."""
    text: str = "text"
    """Name of text field in subtitle items."""
    guide_text_desc: str = "Guide subtitle text."
    """Description of guide subtitle text."""
    target_text_desc: str = "Initially assigned target subtitle text."
    """Description of initial target subtitle text."""
    change_text_desc: str = "Replacement target text for this changed index."
    """Description of changed target subtitle text."""
    guide_indices_err: str = (
        "Query guide indexes must be consecutive, ordered, and begin at 1."
    )
    """Error when query guide indexes are invalid."""
    target_indices_err: str = (
        "Query target indexes must correspond exactly to query guide indexes."
    )
    """Error when query target indexes do not match guides."""
    change_indices_err: str = (
        "Answer change indexes must be unique and in ascending order."
    )
    """Error when answer change indexes are invalid."""
    change_index_missing_err: str = (
        "Every answer change index must correspond to a query guide index."
    )
    """Error when an answer change index is absent from the guide."""
    target_chars_changed_err_tpl: str = (
        "Reconstructed block target text does not preserve the query target "
        "characters in order:\nExpected: {expected}\nReceived: {received}"
    )
    """Error template when reconstructed target characters differ."""

    def target_chars_changed_err(self, expected: str, received: str) -> str:
        """Get an error for changed block target characters.

        Arguments:
            expected: expected concatenated target characters
            received: received concatenated target characters
        Returns:
            formatted error message
        """
        return self.target_chars_changed_err_tpl.format(
            expected=expected, received=received
        )
