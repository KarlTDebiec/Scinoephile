#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""ABC for LLM correspondence text for fusion."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.llms import Prompt

__all__ = ["FusionPrompt"]


class FusionPrompt(Prompt, ABC):
    """ABC for LLM correspondence text for fusion."""

    # Query fields
    source_one_field: ClassVar[str] = "one"
    """Field name for OCR source one."""

    source_one_description: ClassVar[str] = "Subtitle text from OCR source one"
    """Description of source one field."""

    source_two_field: ClassVar[str] = "two"
    """Field name for OCR source two."""

    source_two_description: ClassVar[str] = "Subtitle text from OCR source two"
    """Description of source two field."""

    # Query validation errors
    source_one_missing_error: ClassVar[str] = (
        "Subtitle text from OCR source one is required."
    )
    """Error message when source one field is missing."""

    source_two_missing_error: ClassVar[str] = (
        "Subtitle text from OCR source two is required."
    )
    """Error message when source two field is missing."""

    sources_equal_error: ClassVar[str] = (
        "Subtitle text from both OCR sources must differ."
    )
    """Error message when source one and two fields are equal."""

    # Answer fields
    fused_field: ClassVar[str] = "fused"
    """Field name for fused subtitle text."""

    fused_description: ClassVar[str] = "Merged subtitle text"
    """Description of fused field."""

    note_field: ClassVar[str] = "note"
    """Field name for explanation of changes."""

    note_description: ClassVar[str] = "Explanation of changes made"
    """Description of note field."""

    # Answer validation errors
    fused_missing_error: ClassVar[str] = "Merged subtitle text is required."
    """Error message when fused field is missing."""

    note_missing_error: ClassVar[str] = "Explanation of changes made is required."
    """Error message when note field is missing."""
