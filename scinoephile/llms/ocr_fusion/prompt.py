#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for OCR fusion matters."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.llms import Prompt

__all__ = ["OcrFusionPrompt"]


@dataclass(frozen=True, slots=True, kw_only=True)
class OcrFusionPrompt(Prompt):
    """Text for LLM correspondence for OCR fusion matters."""

    # Query fields
    src_1: str = "one"
    """Name of source one field in query."""

    src_1_desc: str = "Subtitle text from source one"
    """Description of source one field in query."""

    src_2: str = "two"
    """Name of source two field in query."""

    src_2_desc: str = "Subtitle text from source two"
    """Description of source two field in query."""

    # Query validation errors
    src_1_missing_err: str = "Subtitle text from source one is required."
    """Error when source one field is missing from query."""

    src_2_missing_err: str = "Subtitle text from source two is required."
    """Error when source two field is missing from query."""

    src_1_src_2_equal_err: str = "Subtitle text from two sources must differ."
    """Error when source one and two fields are equal in query."""

    # Answer fields
    output: str = "output"
    """Name of output field in answer."""

    output_desc: str = "Output subtitle text"
    """Description of output field in answer."""

    note: str = "note"
    """Name of note field in answer."""

    note_desc: str = "Explanation of output"
    """Description of note field in answer."""

    # Answer validation errors
    output_missing_err: str = "Output subtitle text is required."
    """Error when output field is missing from answer."""

    note_missing_err: str = "Explanation of output is required."
    """Error when note field is missing from answer."""
