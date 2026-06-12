#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runtime path helpers."""

from __future__ import annotations

from os import getenv
from pathlib import Path
from platform import system
from tempfile import gettempdir

from scinoephile.common.validation import val_output_dir_path

__all__ = ["get_runtime_cache_dir_path"]


def get_runtime_cache_dir_path(*parts: str, create: bool = True) -> Path:
    """Get runtime cache directory path for Scinoephile.

    Arguments:
        *parts: optional path components beneath the cache root
        create: whether to create the directory if it does not exist
    Returns:
        cache directory path
    """
    if configured_cache_dir_path := getenv("SCINOEPHILE_CACHE_DIR"):
        cache_root_path = Path(configured_cache_dir_path)
    elif system() == "Darwin":
        cache_root_path = _get_home_cache_root_path("Library", "Caches")
    elif system() == "Windows":
        if local_appdata := getenv("LOCALAPPDATA"):
            cache_root_path = Path(local_appdata)
        else:
            cache_root_path = _get_home_cache_root_path("AppData", "Local")
    elif xdg_cache_home := getenv("XDG_CACHE_HOME"):
        cache_root_path = Path(xdg_cache_home)
    else:
        cache_root_path = _get_home_cache_root_path(".cache")

    return val_output_dir_path(
        cache_root_path / "scinoephile" / Path(*parts),
        create=create,
    )


def _get_home_cache_root_path(*parts: str) -> Path:
    """Get a home-relative cache root path, falling back to temp if home is absent.

    Arguments:
        *parts: cache root components beneath the user home directory
    Returns:
        cache root path
    """
    try:
        return Path.home() / Path(*parts)
    except RuntimeError:
        return Path(gettempdir())
