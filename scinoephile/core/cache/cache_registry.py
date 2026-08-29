#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Generic registry of cache namespace declarations."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

from .cache_namespace import CacheNamespace

__all__ = ["CacheRegistry"]


@dataclass(frozen=True, slots=True, init=False)
class CacheRegistry:
    """Immutable collection of cache namespaces available to maintenance tools."""

    namespaces: tuple[CacheNamespace, ...]
    """Registered cache namespace declarations."""

    def __init__(self, namespaces: Iterable[CacheNamespace]):
        """Initialize.

        Arguments:
            namespaces: cache namespace declarations to register
        Raises:
            ValueError: if multiple declarations have the same namespace template
        """
        namespace_tuple = tuple(namespaces)
        namespace_value_counts = Counter(
            namespace.value for namespace in namespace_tuple
        )
        duplicate_values = sorted(
            namespace_value
            for namespace_value, count in namespace_value_counts.items()
            if count > 1
        )
        if duplicate_values:
            raise ValueError(
                f"Duplicate cache namespace templates: {', '.join(duplicate_values)}"
            )
        object.__setattr__(self, "namespaces", namespace_tuple)

    def __iter__(self) -> Iterator[CacheNamespace]:
        """Iterate over registered cache namespace declarations.

        Returns:
            iterator over namespace declarations
        """
        return iter(self.namespaces)

    def discover_names(self, cache_root_path: Path) -> list[str]:
        """Discover registered namespaces under a cache root.

        Arguments:
            cache_root_path: cache root directory path
        Returns:
            sorted portable namespace names
        Raises:
            NotADirectoryError: if a required path is not a directory
        """
        if not cache_root_path.exists():
            return []
        if not cache_root_path.is_dir():
            raise NotADirectoryError(f"{cache_root_path} is not a directory")
        return sorted(
            namespace_name
            for namespace in self.namespaces
            for namespace_name in namespace.discover_names(cache_root_path)
        )
