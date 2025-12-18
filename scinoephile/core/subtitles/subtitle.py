#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Individual subtitle."""

from __future__ import annotations

from dataclasses import fields
from typing import Any, override

from pysubs2 import SSAEvent
from pysubs2.time import ms_to_str

from ..text import full_punc_chars, half_punc_chars, whitespace_chars

__all__ = ["Subtitle"]


class Subtitle(SSAEvent):
    """Individual subtitle.

    Extension of pysubs2's SSAEvent with additional features.
    """

    __hash__ = None

    @override
    def __init__(self, **kwargs: Any):
        """Initialize.

        Arguments:
            **kwargs: Additional keyword arguments
        """
        super_field_names = {f.name for f in fields(SSAEvent)}
        super_kwargs = {k: v for k, v in kwargs.items() if k in super_field_names}
        super().__init__(**super_kwargs)

    comment: str = ""
    """Comment associated with subtitle."""

    @override
    def __eq__(self, other: SSAEvent) -> bool:
        """Whether this subtitle is equal to another.

        Arguments:
            other: Subtitle to which to compare
        Returns:
            Whether this subtitle is equal to another
        """
        if self.start != other.start:
            return False

        if self.end != other.end:
            return False

        if self.text == other.text:
            return True
        if self.text.replace("\n", "\\N") == other.text.replace("\n", "\\N"):
            return True
        return False

    @override
    def __ne__(self, other: SSAEvent) -> bool:
        """Whether this subtitle is not equal to another.

        Arguments:
            other: Subtitle to which to compare
        Returns:
            Whether this subtitle is not equal to another
        """
        return not self == other

    @override
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"<{self.__class__.__name__} "
            f"start={ms_to_str(self.start, True)} "
            f"end={ms_to_str(self.end, True)} "
            f"text={self.text!r}"
            f">"
        )

    @property
    def text_without_punc_and_whitespace(self) -> str:
        """Text without punctuation."""
        chars_to_remove = half_punc_chars | full_punc_chars | whitespace_chars
        return "".join([c for c in self.text if c not in chars_to_remove])

    @property
    def text_without_whitspace(self) -> str:
        """Text excluding whitespace."""
        return "".join([c for c in self.text if c not in whitespace_chars])
