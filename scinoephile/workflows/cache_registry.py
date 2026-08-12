#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Application-wide registry of Scinoephile-owned cache namespaces."""

from __future__ import annotations

from scinoephile.audio.cache_namespace import AudioCacheNamespace
from scinoephile.core.cache.cache_registry import CacheRegistry
from scinoephile.core.llms import LlmCacheNamespace
from scinoephile.dictionaries.cache_namespace import DictionariesCacheNamespace
from scinoephile.image.cache_namespace import ImageCacheNamespace
from scinoephile.lang.cache_namespace import LangCacheNamespace
from scinoephile.media.cache_namespace import MediaCacheNamespace

__all__ = ["CACHE_REGISTRY"]

CACHE_REGISTRY = CacheRegistry(
    (
        *AudioCacheNamespace,
        *DictionariesCacheNamespace,
        *ImageCacheNamespace,
        *LangCacheNamespace,
        *LlmCacheNamespace,
        *MediaCacheNamespace,
    )
)
"""Scinoephile-owned cache namespaces available to maintenance operations."""
