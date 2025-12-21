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
    src_1_sub_1_field: ClassVar[str] = "src_1_sub_1"
    """Name of source one subtitle one field in query."""

    src_1_sub_1_desc: ClassVar[str] = "Source one subtitle one text"
    """Description of source one subtitle one field in query."""

    src_1_sub_2_field: ClassVar[str] = "src_1_sub_2"
    """Name of source one subtitle two field in query."""

    src_1_sub_2_desc: ClassVar[str] = "Source one subtitle two text"
    """Description of source one subtitle two field in query."""

    src_2_sub_1_field: ClassVar[str] = "src_2_sub_1"
    """Name of source two subtitle one field in query."""

    src_2_sub_1_desc: ClassVar[str] = "Source two subtitle one text"
    """Description of source two subtitle one field in query."""

    src_2_sub_2_field: ClassVar[str] = "src_2_sub_2"
    """Name of source two subtitle two field in query."""

    src_2_sub_2_desc: ClassVar[str] = "Source two subtitle two text"
    """Description of source two subtitle two field in query."""

    # Query validation errors
    src_2_sub_1_sub_2_missing_error: ClassVar[str] = (
        "Query must have src_2_sub_1, src_2_sub_2, or both."
    )
    """Error when src_2_sub_1 and src_2_sub_2 fields are missing."""

    # Answer fields
    src_2_sub_1_shifted_field: ClassVar[str] = "src_2_sub_1_shifted"
    """Name of shifted source two subtitle one field in answer."""

    src_2_sub_1_shifted_desc: ClassVar[str] = "Shifted source two subtitle one"
    """Description of shifted source two subtitle one field in answer."""

    src_2_sub_2_shifted_field: ClassVar[str] = "src_2_sub_2_shifted"
    """Name of shifted source two subtitle two field in answer."""

    src_2_sub_2_shifted_desc: ClassVar[str] = "Shifted source two subtitle two"
    """Description of shifted source two subtitle two field in answer."""

    # Test case validation errors
    src_2_sub_1_sub_2_unchanged_error: ClassVar[str] = (
        "Answer's src_2_sub_1_shifted and src_2_sub_2_shifted are equal to query's "
        "src_2_sub_1 and src_2_sub_2; if no shift is needed, src_2_sub_1_shifted and "
        "src_2_sub_2_shifted must be empty strings."
    )
    """Error when src_2_sub_1 and src_2_sub_2 are unchanged."""

    src_2_characters_changed_error_template: ClassVar[str] = (
        "Answer's concatenated src_2_sub_1_shifted and src_2_sub_2_shifted does not "
        "match query's concatenated src_2_sub_1 and src_2_sub_2:\n"
        "Expected: {expected}\n"
        "Received: {received}"
    )
    """Error template when shifted source two characters do not match original."""

    @classmethod
    def src_2_characters_changed_error(cls, expected: str, received: str) -> str:
        """Error when shifted source two characters do not match original.

        Arguments:
            expected: expected concatenated source two characters
            received: received concatenated source two characters
        Returns:
            formatted error message
        """
        return cls.src_2_characters_changed_error_template.format(
            expected=expected, received=received
        )
