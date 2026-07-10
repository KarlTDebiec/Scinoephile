#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for pairwise review."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["PairwiseReviewPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class PairwiseReviewPrompt(Prompt):
    """Text for reviewing one subtitle against one reference subtitle."""

    # Query fields
    target: str = "target"
    """Name of target field in query."""

    target_desc: str = "Subtitle text to review"
    """Description of target field in query."""

    reference: str = "reference"
    """Name of reference field in query."""

    reference_desc: str = "Corresponding reference subtitle text"
    """Description of reference field in query."""

    # Answer fields
    output: str = "output"
    """Name of output field in answer."""

    output_desc: str = (
        'Revised target subtitle, "" if unchanged, or "�" if it should be removed'
    )
    """Description of output field in answer."""

    note: str = "note"
    """Name of note field in answer."""

    note_desc: str = "Explanation of the revision, or an empty string"
    """Description of note field in answer."""

    # Test case errors
    note_missing_err: str = "The target is revised, but no note is provided."
    """Error when note is missing for a revision."""

    output_missing_err: str = "The target is unchanged, but a note is provided."
    """Error when output is missing for a note."""
