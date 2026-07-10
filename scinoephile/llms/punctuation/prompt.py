#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Text for LLM correspondence for punctuation."""

from __future__ import annotations

from abc import ABC
from typing import ClassVar

from scinoephile.core.llms import Prompt

__all__ = ["PunctuationPrompt"]


class PunctuationPrompt(Prompt, ABC):
    """Text for LLM correspondence for punctuation."""

    # Query fields
    src_1: ClassVar[str] = "one"
    """Name of source one field in query."""

    src_1_desc: ClassVar[str] = "Subtitle texts from source one"
    """Description of source one field in query."""

    src_2: ClassVar[str] = "two"
    """Name of source two field in query."""

    src_2_desc: ClassVar[str] = "Subtitle text from source two"
    """Description of source two field in query."""

    # Query validation errors
    src_1_missing_err: ClassVar[str] = "Subtitle texts from source one are required."
    """Error when source one field is missing from query."""

    src_2_missing_err: ClassVar[str] = "Subtitle text from source two is required."
    """Error when source two field is missing from query."""

    # Answer fields
    output: ClassVar[str] = "output"
    """Name of output field in answer."""

    output_desc: ClassVar[str] = "Output subtitle text"
    """Description of output field in answer."""

    # Answer validation errors
    output_missing_err: ClassVar[str] = "Output subtitle text is required."
    """Error when output field is missing from answer."""

    # Test case validation errors
    src_1_chars_changed_err_tpl: ClassVar[str] = (
        "Answer output stripped of punctuation and whitespace does not match query "
        "source one concatenated:\n"
        "Expected: {expected}\n"
        "Received: {received}"
    )
    """Error when output characters do not match source one."""

    @classmethod
    def src_1_chars_changed_err(cls, expected: str, received: str) -> str:
        """Error when output characters do not match source one.

        Arguments:
            expected: expected source one characters
            received: received output characters
        Returns:
            error message
        """
        return cls.src_1_chars_changed_err_tpl.format(
            expected=expected,
            received=received,
        )
