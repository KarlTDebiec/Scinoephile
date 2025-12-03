#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Data class for a pair of characters."""

from __future__ import annotations

from dataclasses import dataclass

from scinoephile.core.text import get_char_type

__all__ = ["CharPair"]


@dataclass(slots=True)
class CharPair:
    """Data class for a pair of characters."""

    char_1: str
    """First character."""
    char_2: str
    """Second character."""
    width_1: int
    """Width of the first character."""
    width_2: int
    """Width of the second character."""
    gap: int
    """Gap between the two characters."""
    whitespace: str
    """Whitespace between the two characters."""

    @property
    def type_1(self) -> str:
        """Type of the first character."""
        return get_char_type(self.char_1)

    @property
    def type_2(self) -> str:
        """Type of the second character."""
        return get_char_type(self.char_2)
