#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM correspondence text for dual track / single subtitle review."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.llms.base import Prompt

__all__ = ["DualSinglePrompt"]


class DualSinglePrompt(Prompt, ABC):
    """ABC for LLM correspondence text for dual track / single subtitle review."""

    # Query fields
    source_one_field: ClassVar[str] = "one"
    """Name of source one field in query."""

    source_one_description: ClassVar[str] = "Subtitle text from source one"
    """Description of source one field in query."""

    source_two_field: ClassVar[str] = "two"
    """Name for source two field in query."""

    source_two_description: ClassVar[str] = "Subtitle text from source two"
    """Description of source two field in query."""

    # Query validation errors
    source_one_missing_error: ClassVar[str] = (
        "Subtitle text from source one is required."
    )
    """Error when source one field is missing from query."""

    source_two_missing_error: ClassVar[str] = (
        "Subtitle text from source two is required."
    )
    """Error when source two field is missing from query."""

    sources_equal_error: ClassVar[str] = "Subtitle text from two sources must differ."
    """Error when source one and two fields are equal in query."""

    # Answer fields
    output_field: ClassVar[str] = "output"
    """Name of output field in answer."""

    output_description: ClassVar[str] = "Output subtitle text"
    """Description of output field in answer."""

    note_field: ClassVar[str] = "note"
    """Name of note field in answer."""

    note_description: ClassVar[str] = "Explanation of output"
    """Description of note field in answer."""

    # Answer validation errors
    output_missing_error: ClassVar[str] = "Output subtitle text is required."
    """Error when output field is missing from answer."""

    note_missing_error: ClassVar[str] = "Explanation of output is required."
    """Error when note field is missing from answer."""
