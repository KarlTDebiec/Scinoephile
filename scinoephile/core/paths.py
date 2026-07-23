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
        cache_root_path = Path.home() / "Library/Caches"
    elif system() == "Windows":
        cache_root_path = _get_windows_cache_root_path()
    elif xdg_cache_home := getenv("XDG_CACHE_HOME"):
        cache_root_path = Path(xdg_cache_home)
    else:
        cache_root_path = Path.home() / ".cache"

    return val_output_dir_path(
        cache_root_path / "scinoephile" / Path(*parts),
        create=create,
    )


def _get_windows_cache_root_path() -> Path:
    """Get the Windows cache root path, falling back to temp if home is absent.

    Returns:
        cache root path
    """
    if local_appdata := getenv("LOCALAPPDATA"):
        return Path(local_appdata)
    try:
        return Path.home() / "AppData/Local"
    except RuntimeError:
        return Path(gettempdir())
