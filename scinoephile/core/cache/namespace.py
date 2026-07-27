#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cache namespace directory helpers."""

from __future__ import annotations

from pathlib import Path

from scinoephile.common.validation import val_output_dir_path

__all__ = [
    "CACHE_NAMESPACE_MARKER_FILENAME",
    "get_cache_namespace_dir_path",
]

CACHE_NAMESPACE_MARKER_FILENAME = ".scinoephile-cache-namespace"
"""Filename identifying a directory as a cache namespace."""


def get_cache_namespace_dir_path(
    cache_root_path: Path,
    *namespace_parts: str,
) -> Path:
    """Get and identify a cache namespace directory.

    Arguments:
        cache_root_path: cache root directory path
        *namespace_parts: cache namespace path components
    Returns:
        cache namespace directory path
    Raises:
        ValueError: if a namespace component is empty or contains a path separator
    """
    if not namespace_parts:
        raise ValueError("At least one cache namespace component is required")
    if any(
        not part or part in {".", ".."} or Path(part).name != part
        for part in namespace_parts
    ):
        raise ValueError("Cache namespace components must be simple directory names")

    cache_dir_path = val_output_dir_path(cache_root_path.joinpath(*namespace_parts))
    marker_path = cache_dir_path / CACHE_NAMESPACE_MARKER_FILENAME
    if not marker_path.exists():
        marker_path.touch()
    return cache_dir_path
