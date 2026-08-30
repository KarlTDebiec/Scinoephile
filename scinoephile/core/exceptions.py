#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Core Scinoephile exceptions."""

from __future__ import annotations

__all__ = ["DependencyError", "ScinoephileError", "UnsupportedCharacterError"]


class ScinoephileError(Exception):
    """Scinoephile error."""


class DependencyError(ScinoephileError):
    """Raised when an optional dependency required by an operation is unavailable."""


class UnsupportedCharacterError(ScinoephileError):
    """Text contains unsupported character(s)."""
