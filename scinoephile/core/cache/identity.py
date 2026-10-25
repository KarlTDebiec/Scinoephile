#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Type definitions for persistent cache identities."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

__all__ = ["CacheIdentity", "CacheIdentityValue"]

type CacheIdentityValue = (
    str
    | int
    | float
    | bool
    | None
    | Mapping[str, CacheIdentityValue]
    | Sequence[CacheIdentityValue]
)
"""JSON-compatible value in a cache identity."""

type CacheIdentity = dict[str, CacheIdentityValue]
"""JSON-serializable configuration identifying a reusable cache result."""
