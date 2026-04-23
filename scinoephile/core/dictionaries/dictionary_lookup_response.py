#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Typed response payload for dictionary lookup tools."""

from __future__ import annotations

from typing import TypedDict

__all__ = ["DictionaryLookupResponse"]


class DictionaryLookupResponse(TypedDict, total=False):
    """Dictionary tool response payload."""

    query: str
    """Lookup query."""

    result_count: int
    """Number of matching entries returned."""

    entries: list[dict[str, str | float | list[dict[str, str]]]]
    """Serialized dictionary entries."""

    error: str
    """Error message when lookup fails."""
