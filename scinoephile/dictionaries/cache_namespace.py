#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Dictionary cache namespace declarations."""

from __future__ import annotations

from scinoephile.core.cache.cache_namespace import CacheNamespace

__all__ = ["DictionariesCacheNamespace"]


class DictionariesCacheNamespace(CacheNamespace):
    """Cache namespaces owned by the dictionaries package."""

    CUHK_DISCOVERY = "dictionaries/cuhk/discovery"
    """CUHK dictionary discovery responses."""
    CUHK_PAGES = "dictionaries/cuhk/pages"
    """CUHK dictionary entry pages."""
