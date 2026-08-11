#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Language cache namespace declarations."""

from __future__ import annotations

from scinoephile.core.cache.cache_namespace import CacheNamespace

__all__ = ["LangCacheNamespace"]


class LangCacheNamespace(CacheNamespace):
    """Cache namespaces owned by the lang package."""

    ZHO_SUBTITLES_ANALYSIS = "lang/zho/subtitles/analysis"
    """Chinese subtitle script analysis results."""
