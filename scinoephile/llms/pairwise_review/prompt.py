#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for pairwise review."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.llms import Prompt

__all__ = ["PairwiseReviewPrompt"]


class PairwiseReviewPrompt(Prompt, ABC):
    """Text for reviewing one subtitle against one reference subtitle."""

    __slots__ = ()

    # Query fields
    target: ClassVar[str] = "target"
    """Name of target field in query."""

    target_desc: ClassVar[str] = "Subtitle text to review"
    """Description of target field in query."""

    reference: ClassVar[str] = "reference"
    """Name of reference field in query."""

    reference_desc: ClassVar[str] = "Corresponding reference subtitle text"
    """Description of reference field in query."""

    # Answer fields
    output: ClassVar[str] = "output"
    """Name of output field in answer."""

    output_desc: ClassVar[str] = (
        'Revised target subtitle, "" if unchanged, or "�" if it should be removed'
    )
    """Description of output field in answer."""

    note: ClassVar[str] = "note"
    """Name of note field in answer."""

    note_desc: ClassVar[str] = "Explanation of the revision, or an empty string"
    """Description of note field in answer."""

    # Test case errors
    note_missing_err: ClassVar[str] = "The target is revised, but no note is provided."
    """Error when note is missing for a revision."""

    output_missing_err: ClassVar[str] = (
        "The target is unchanged, but a note is provided."
    )
    """Error when output is missing for a note."""
