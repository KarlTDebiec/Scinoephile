#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runtime path helpers."""

from __future__ import annotations

from os import getenv
from pathlib import Path
from platform import system
from tempfile import gettempdir

from scinoephile.common.validation import val_output_dir_path

__all__ = [
    "get_runtime_cache_root_path",
    "get_runtime_data_root_path",
]


def get_runtime_cache_root_path(*, create: bool = True) -> Path:
    """Get the Scinoephile runtime cache root path.

    Arguments:
        create: whether to create the directory if it does not exist
    Returns:
        cache root path
    """
    if configured_cache_root_path := getenv("SCINOEPHILE_CACHE_DIR"):
        cache_root_path = Path(configured_cache_root_path)
    elif system() == "Darwin":
        cache_root_path = Path.home() / "Library/Caches" / "scinoephile"
    elif system() == "Windows":
        cache_root_path = _get_windows_cache_parent_path() / "scinoephile"
    elif xdg_cache_home := getenv("XDG_CACHE_HOME"):
        cache_root_path = Path(xdg_cache_home) / "scinoephile"
    else:
        cache_root_path = Path.home() / ".cache" / "scinoephile"

    return val_output_dir_path(cache_root_path, create=create)


def get_runtime_data_root_path(*, create: bool = True) -> Path:
    """Get the Scinoephile runtime data root path.

    Arguments:
        create: whether to create the directory if it does not exist
    Returns:
        data root path
    """
    if configured_data_root_path := getenv("SCINOEPHILE_DATA_DIR"):
        data_root_path = Path(configured_data_root_path)
    elif system() == "Darwin":
        data_root_path = Path.home() / "Library/Application Support" / "scinoephile"
    elif system() == "Windows":
        data_root_path = _get_windows_data_parent_path() / "scinoephile"
    elif xdg_data_home := getenv("XDG_DATA_HOME"):
        data_root_path = Path(xdg_data_home) / "scinoephile"
    else:
        data_root_path = Path.home() / ".local/share" / "scinoephile"

    return val_output_dir_path(data_root_path, create=create)


def _get_windows_cache_parent_path() -> Path:
    """Get the Windows cache parent path, falling back to temp if home is absent.

    Returns:
        cache parent path
    """
    if local_appdata := getenv("LOCALAPPDATA"):
        return Path(local_appdata)
    try:
        return Path.home() / "AppData/Local"
    except RuntimeError:
        return Path(gettempdir())


def _get_windows_data_parent_path() -> Path:
    """Get the Windows data parent path, falling back to temp if home is absent.

    Returns:
        data parent path
    """
    if appdata := getenv("APPDATA"):
        return Path(appdata)
    try:
        return Path.home() / "AppData/Roaming"
    except RuntimeError:
        return Path(gettempdir())
