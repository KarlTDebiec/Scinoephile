#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Type definitions for persistent cache identities."""

from __future__ import annotations

from pydantic import JsonValue

__all__ = ["CacheIdentity"]

type CacheIdentity = dict[str, JsonValue]
"""JSON-serializable configuration identifying a reusable cache result."""
