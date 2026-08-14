#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Media cache namespace declarations."""

from __future__ import annotations

from scinoephile.core.cache.cache_namespace import CacheNamespace

__all__ = ["MediaCacheNamespace"]


class MediaCacheNamespace(CacheNamespace):
    """Cache namespaces owned by the media package."""

    SUBTITLES = "media/subtitles"
    """Extracted subtitle streams and image series."""
