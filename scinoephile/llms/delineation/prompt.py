#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for delineation."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["DelineationPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class DelineationPrompt(Prompt):
    """Text for LLM correspondence for delineation."""

    # Query fields
    ref_sub_1: str = "ref_sub_1"
    """Name of reference subtitle one field in query."""

    ref_sub_1_desc: str = "Reference subtitle one text"
    """Description of reference subtitle one field in query."""

    ref_sub_2: str = "ref_sub_2"
    """Name of reference subtitle two field in query."""

    ref_sub_2_desc: str = "Reference subtitle two text"
    """Description of reference subtitle two field in query."""

    target_sub_1: str = "target_sub_1"
    """Name of target subtitle one field in query."""

    target_sub_1_desc: str = "Target subtitle one text"
    """Description of target subtitle one field in query."""

    target_sub_2: str = "target_sub_2"
    """Name of target subtitle two field in query."""

    target_sub_2_desc: str = "Target subtitle two text"
    """Description of target subtitle two field in query."""

    # Query validation errors
    target_subs_missing_err: str = (
        "Query must have target_sub_1, target_sub_2, or both."
    )
    """Error when target subtitle fields are missing."""

    # Answer fields
    target_sub_1_shifted: str = "target_sub_1_shifted"
    """Name of shifted target subtitle one field in answer."""

    target_sub_1_shifted_desc: str = "Shifted target subtitle one"
    """Description of shifted target subtitle one field in answer."""

    target_sub_2_shifted: str = "target_sub_2_shifted"
    """Name of shifted target subtitle two field in answer."""

    target_sub_2_shifted_desc: str = "Shifted target subtitle two"
    """Description of shifted target subtitle two field in answer."""

    # Test case validation errors
    target_subs_unchanged_err: str = (
        "Answer's target_sub_1_shifted and target_sub_2_shifted are equal to query's "
        "target_sub_1 and target_sub_2; if no shift is needed, target_sub_1_shifted "
        "and target_sub_2_shifted must be empty strings."
    )
    """Error when target subtitles are unchanged."""

    target_chars_changed_err_tpl: str = (
        "Answer's concatenated target_sub_1_shifted and target_sub_2_shifted does "
        "not match query's concatenated target_sub_1 and target_sub_2:\n"
        "Expected: {expected}\n"
        "Received: {received}"
    )
    """Error template when shifted target characters do not match original."""

    def target_chars_changed_err(self, expected: str, received: str) -> str:
        """Error when shifted target characters do not match original.

        Arguments:
            expected: expected concatenated target characters
            received: received concatenated shifted target characters
        Returns:
            formatted error message
        """
        return self.target_chars_changed_err_tpl.format(
            expected=expected, received=received
        )
