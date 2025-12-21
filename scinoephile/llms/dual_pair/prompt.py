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
    source_one_sub_one_field: ClassVar[str] = "source_one_sub_one"
    """Field name for source one subtitle one text."""

    source_one_sub_one_desc: ClassVar[str] = "Source one subtitle one text"
    """Description of source_one_sub_one field."""

    source_one_sub_two_field: ClassVar[str] = "source_one_sub_two"
    """Field name for source one subtitle two text."""

    source_one_sub_two_desc: ClassVar[str] = "Source one subtitle two text"
    """Description of source_one_sub_two field."""

    source_two_sub_one_field: ClassVar[str] = "source_two_sub_one"
    """Field name for source two subtitle one text."""

    source_two_sub_one_desc: ClassVar[str] = "Source two subtitle one text"
    """Description of source_two_sub_one field."""

    source_two_sub_two_field: ClassVar[str] = "source_two_sub_two"
    """Field name for source two subtitle two text."""

    source_two_sub_two_desc: ClassVar[str] = "Source two subtitle two text"
    """Description of source_two_sub_two field."""

    # Query validation errors
    source_two_sub_one_sub_two_missing_error: ClassVar[str] = (
        "Query must have source_two_sub_one, source_two_sub_two, or both."
    )
    """Error when source_two_sub_one and source_two_sub_two fields are missing."""

    # Answer fields
    source_two_sub_one_shifted_field: ClassVar[str] = "source_two_sub_one_shifted"
    """Field name for shifted source two subtitle one text."""

    source_two_sub_one_shifted_desc: ClassVar[str] = "Shifted source two subtitle one"
    """Description of source_two_sub_one_shifted field."""

    source_two_sub_two_shifted_field: ClassVar[str] = "source_two_sub_two_shifted"
    """Field name for shifted source two subtitle two text."""

    source_two_sub_two_shifted_desc: ClassVar[str] = "Shifted source two subtitle two"
    """Description of source_two_sub_two_shifted field."""

    # Test case validation errors
    source_two_sub_one_sub_two_unchanged_error: ClassVar[str] = (
        "Answer's source_two_sub_one_shifted and source_two_sub_two_shifted are equal "
        "to query's source_two_sub_one and source_two_sub_two; if no shift is needed, "
        "source_two_sub_one_shifted and source_two_sub_two_shifted must be empty "
        "strings."
    )
    """Error when source_two_sub_one and source_two_sub_two are unchanged."""

    source_two_characters_changed_error_template: ClassVar[str] = (
        "Answer's concatenated source_two_sub_one_shifted and "
        "source_two_sub_two_shifted does not match query's concatenated "
        "source_two_sub_one and source_two_sub_two:\n"
        "Expected: {expected}\n"
        "Received: {received}"
    )
    """Error template when shifted source two characters do not match original."""

    @classmethod
    def source_two_characters_changed_error(cls, expected: str, received: str) -> str:
        """Error when shifted source two characters do not match original.

        Arguments:
            expected: expected concatenated source two characters
            received: received concatenated source two characters
        Returns:
            formatted error message
        """
        return cls.source_two_characters_changed_error_template.format(
            expected=expected, received=received
        )
