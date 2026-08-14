#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""LLM cache namespace declarations."""

from __future__ import annotations

from scinoephile.core.cache.cache_namespace import CacheNamespace

__all__ = ["LlmCacheNamespace"]


class LlmCacheNamespace(CacheNamespace):
    """Cache namespaces owned by the llms package."""

    OPERATION = "llms/<operation>"
    """Operation-specific LLM responses."""
