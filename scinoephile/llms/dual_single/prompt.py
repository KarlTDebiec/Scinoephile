#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for dual track / single subtitle matters."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.llms.base import Prompt

__all__ = ["DualSinglePrompt"]


class DualSinglePrompt(Prompt, ABC):
    """Text for LLM correspondence for dual track / single subtitle matters."""

    # Query fields
    src_1: ClassVar[str] = "one"
    """Name of source one field in query."""

    src_1_desc: ClassVar[str] = "Subtitle text from source one"
    """Description of source one field in query."""

    src_2: ClassVar[str] = "two"
    """Name of source two field in query."""

    src_2_desc: ClassVar[str] = "Subtitle text from source two"
    """Description of source two field in query."""

    # Query validation errors
    src_1_missing_err: ClassVar[str] = "Subtitle text from source one is required."
    """Error when source one field is missing from query."""

    src_2_missing_err: ClassVar[str] = "Subtitle text from source two is required."
    """Error when source two field is missing from query."""

    src_1_src_2_equal_err: ClassVar[str] = "Subtitle text from two sources must differ."
    """Error when source one and two fields are equal in query."""

    # Answer fields
    output: ClassVar[str] = "output"
    """Name of output field in answer."""

    output_desc: ClassVar[str] = "Output subtitle text"
    """Description of output field in answer."""

    note: ClassVar[str] = "note"
    """Name of note field in answer."""

    note_desc: ClassVar[str] = "Explanation of output"
    """Description of note field in answer."""
