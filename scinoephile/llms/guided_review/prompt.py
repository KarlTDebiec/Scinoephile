#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for guided review."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.llms import Prompt

__all__ = ["GuidedReviewPrompt"]


class GuidedReviewPrompt(Prompt, ABC):
    """Text for reviewing target blocks using guide blocks."""

    # Query fields
    target_pfx: ClassVar[str] = "target_"
    """Prefix for target fields in query."""

    target_desc_tpl: ClassVar[str] = "Target subtitle {idx} to review"
    """Description template for target fields in query."""

    guide_pfx: ClassVar[str] = "guide_"
    """Prefix for guide fields in query."""

    guide_desc_tpl: ClassVar[str] = "Guide subtitle {idx}"
    """Description template for guide fields in query."""

    # Answer fields
    output_pfx: ClassVar[str] = "output_"
    """Prefix for output fields in answer."""

    output_desc_tpl: ClassVar[str] = (
        'Revised target subtitle {idx}, or "" if no change is needed'
    )
    """Description template for output fields in answer."""

    note_pfx: ClassVar[str] = "note_"
    """Prefix for note fields in answer."""

    note_desc_tpl: ClassVar[str] = (
        'Explanation of the revision to target subtitle {idx}, or ""'
    )
    """Description template for note fields in answer."""

    # Test case errors
    note_missing_err_tpl: ClassVar[str] = (
        "Target subtitle {idx} is revised, but no note is provided."
    )
    """Error template when note is missing for a revision."""

    output_missing_err_tpl: ClassVar[str] = (
        "Target subtitle {idx} is unchanged, but a note is provided."
    )
    """Error template when output is missing for a note."""

    @classmethod
    def guide(cls, idx: int) -> str:
        """Name of guide field in query."""
        return f"{cls.guide_pfx}{idx}"

    @classmethod
    def guide_desc(cls, idx: int) -> str:
        """Description of guide field in query."""
        return cls.guide_desc_tpl.format(idx=idx)

    @classmethod
    def note(cls, idx: int) -> str:
        """Name of note field in answer."""
        return f"{cls.note_pfx}{idx}"

    @classmethod
    def note_desc(cls, idx: int) -> str:
        """Description of note field in answer."""
        return cls.note_desc_tpl.format(idx=idx)

    @classmethod
    def note_missing_err(cls, idx: int) -> str:
        """Error when note is missing for a revision."""
        return cls.note_missing_err_tpl.format(idx=idx)

    @classmethod
    def output(cls, idx: int) -> str:
        """Name of output field in answer."""
        return f"{cls.output_pfx}{idx}"

    @classmethod
    def output_desc(cls, idx: int) -> str:
        """Description of output field in answer."""
        return cls.output_desc_tpl.format(idx=idx)

    @classmethod
    def output_missing_err(cls, idx: int) -> str:
        """Error when output is missing for a note."""
        return cls.output_missing_err_tpl.format(idx=idx)

    @classmethod
    def target(cls, idx: int) -> str:
        """Name of target field in query."""
        return f"{cls.target_pfx}{idx}"

    @classmethod
    def target_desc(cls, idx: int) -> str:
        """Description of target field in query."""
        return cls.target_desc_tpl.format(idx=idx)
