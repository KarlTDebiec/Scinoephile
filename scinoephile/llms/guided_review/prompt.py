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
    target_pfx: str = "target_"
    """Prefix for target fields in query."""

    target_desc_tpl: str = "Target subtitle {idx} to review"
    """Description template for target fields in query."""

    guide_pfx: str = "guide_"
    """Prefix for guide fields in query."""

    guide_desc_tpl: str = "Guide subtitle {idx}"
    """Description template for guide fields in query."""

    # Answer fields
    output_pfx: str = "output_"
    """Prefix for output fields in answer."""

    output_desc_tpl: str = 'Revised target subtitle {idx}, or "" if no change is needed'
    """Description template for output fields in answer."""

    note_pfx: str = "note_"
    """Prefix for note fields in answer."""

    note_desc_tpl: str = 'Explanation of the revision to target subtitle {idx}, or ""'
    """Description template for note fields in answer."""

    # Test case errors
    note_missing_err_tpl: str = (
        "Target subtitle {idx} is revised, but no note is provided."
    )
    """Error template when note is missing for a revision."""

    output_missing_err_tpl: str = (
        "Target subtitle {idx} is unchanged, but a note is provided."
    )
    """Error template when output is missing for a note."""

    def guide(self, idx: int) -> str:
        """Name of guide field in query."""
        return f"{self.guide_pfx}{idx}"

    def guide_desc(self, idx: int) -> str:
        """Description of guide field in query."""
        return self.guide_desc_tpl.format(idx=idx)

    def note(self, idx: int) -> str:
        """Name of note field in answer."""
        return f"{self.note_pfx}{idx}"

    def note_desc(self, idx: int) -> str:
        """Description of note field in answer."""
        return self.note_desc_tpl.format(idx=idx)

    def note_missing_err(self, idx: int) -> str:
        """Error when note is missing for a revision."""
        return self.note_missing_err_tpl.format(idx=idx)

    def output(self, idx: int) -> str:
        """Name of output field in answer."""
        return f"{self.output_pfx}{idx}"

    def output_desc(self, idx: int) -> str:
        """Description of output field in answer."""
        return self.output_desc_tpl.format(idx=idx)

    def output_missing_err(self, idx: int) -> str:
        """Error when output is missing for a note."""
        return self.output_missing_err_tpl.format(idx=idx)

    def target(self, idx: int) -> str:
        """Name of target field in query."""
        return f"{self.target_pfx}{idx}"

    def target_desc(self, idx: int) -> str:
        """Description of target field in query."""
        return self.target_desc_tpl.format(idx=idx)
