#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Individual subtitle."""

from __future__ import annotations

from dataclasses import fields
from typing import TypedDict, Unpack, override

from pysubs2 import SSAEvent
from pysubs2.time import ms_to_str

__all__ = ["Subtitle", "SubtitleKwargs"]


class SubtitleKwargs(TypedDict, total=False):
    """Keyword arguments for Subtitle initialization.

    These correspond to the fields of pysubs2.SSAEvent.
    """

    start: int
    end: int
    text: str
    style: str
    name: str
    marked: bool
    effect: str
    layer: int
    margin_l: int
    margin_r: int
    margin_v: int


class Subtitle(SSAEvent):
    """Individual subtitle.

    Extension of pysubs2's SSAEvent with additional features.
    """

    __hash__ = None

    @override
    def __init__(self, **kwargs: Unpack[SubtitleKwargs]):
        """Initialize.

        Arguments:
            **kwargs: additional keyword arguments
        """
        super_field_names = {f.name for f in fields(SSAEvent)}
        super_kwargs = {k: v for k, v in kwargs.items() if k in super_field_names}
        super().__init__(**super_kwargs)

    @override
    def __eq__(self, other: object) -> bool:
        """Whether this subtitle is equal to another.

        Arguments:
            other: Subtitle to which to compare
        Returns:
            whether this subtitle is equal to another
        """
        if not isinstance(other, SSAEvent):
            return NotImplemented

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
    def __ne__(self, other: object) -> bool:
        """Whether this subtitle is not equal to another.

        Arguments:
            other: Subtitle to which to compare
        Returns:
            whether this subtitle is not equal to another
        """
        eq_result = self == other
        if eq_result is NotImplemented:
            return NotImplemented
        return not eq_result

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
    def text_with_newline(self) -> str:
        """Text with newline escapes replaced."""
        return self.text.replace("\\N", "\n")
