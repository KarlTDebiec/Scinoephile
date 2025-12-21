#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for dual pair matters."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.llms.base import Prompt

__all__ = ["DualPairPrompt"]


class DualPairPrompt(Prompt, ABC):
    """Text for LLM correspondence for dual pair matters."""

    # Query fields
    reference_1_field: ClassVar[str] = "reference_1"
    """Field name for reference text 1."""

    reference_1_description: ClassVar[str] = "Known reference text 1"
    """Description of reference_1 field."""

    reference_2_field: ClassVar[str] = "reference_2"
    """Field name for reference text 2."""

    reference_2_description: ClassVar[str] = "Known reference text 2"
    """Description of reference_2 field."""

    target_1_field: ClassVar[str] = "target_1"
    """Field name for target text 1."""

    target_1_description: ClassVar[str] = "Target text 1"
    """Description of target_1 field."""

    target_2_field: ClassVar[str] = "target_2"
    """Field name for target text 2."""

    target_2_description: ClassVar[str] = "Target text 2"
    """Description of target_2 field."""

    # Query validation errors
    target_1_target_2_missing_error: ClassVar[str] = (
        "Query must have target_1, target_2, or both."
    )
    """Error when target_1 and target_2 fields are missing."""

    # Answer fields
    target_1_shifted_field: ClassVar[str] = "target_1_shifted"
    """Field name for shifted target text 1."""

    target_1_shifted_description: ClassVar[str] = "Shifted target text 1"
    """Description of target_1_shifted field."""

    target_2_shifted_field: ClassVar[str] = "target_2_shifted"
    """Field name for shifted target text 2."""

    target_2_shifted_description: ClassVar[str] = "Shifted target text 2"
    """Description of target_2_shifted field."""

    # Test case validation errors
    target_1_target_2_unchanged_error: ClassVar[str] = (
        "Answer's target_1_shifted and target_2_shifted are equal to query's target_1 "
        "and target_2; if no shift is needed, target_1_shifted and target_2_shifted "
        "must be empty strings."
    )
    """Error when target_1 and target_2 are unchanged and not both omitted."""

    target_characters_changed_error_template: ClassVar[str] = (
        "Answer's concatenated target_1_shifted and target_2_shifted does not match "
        "query's concatenated target_1 and target_2:\n"
        "Expected: {expected}\n"
        "Received: {received}"
    )
    """Error template when shifted target characters do not match original."""

    @classmethod
    def target_characters_changed_error(cls, expected: str, received: str) -> str:
        """Error when shifted target characters do not match original.

        Arguments:
            expected: expected concatenated target characters
            received: received concatenated target characters
        Returns:
            formatted error message
        """
        return cls.target_characters_changed_error_template.format(
            expected=expected, received=received
        )
