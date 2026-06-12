#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Enum base class with code and description metadata."""

from __future__ import annotations

from enum import Enum
from typing import Self

__all__ = ["DescribedEnum"]


class DescribedEnum(Enum):
    """Enum with code and description metadata."""

    _description: str

    def __new__(cls, code: str, description: str) -> Self:
        """Create enum member with attached description metadata.

        Arguments:
            code: enum code
            description: human-readable description
        """
        member = object.__new__(cls)
        member._value_ = code
        member._description = description
        return member

    @property
    def code(self) -> str:
        """Enum code."""
        return self.value

    @property
    def description(self) -> str:
        """Human-readable description of this enum member."""
        return self._description

    def __str__(self) -> str:
        """String representation used in CLI/help contexts."""
        return self.value
