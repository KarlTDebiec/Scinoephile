#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Runtime path helpers for LLM workflows."""

from __future__ import annotations

from os import getenv
from pathlib import Path
from platform import system

from scinoephile.common.validation import val_output_dir_path

__all__ = ["get_runtime_cache_dir"]


def get_runtime_cache_dir(*parts: str) -> Path:
    """Get runtime cache directory for Scinoephile.

    Arguments:
        *parts: optional path components beneath the cache root
    Returns:
        cache directory path
    """
    if configured_root := getenv("SCINOEPHILE_CACHE_DIR"):
        cache_root = Path(configured_root)
    elif system() == "Darwin":
        cache_root = Path.home() / "Library" / "Caches"
    elif system() == "Windows":
        cache_root = Path(getenv("LOCALAPPDATA") or Path.home() / "AppData" / "Local")
    else:
        cache_root = Path(getenv("XDG_CACHE_HOME") or Path.home() / ".cache")

    return val_output_dir_path(cache_root / "scinoephile" / Path(*parts))
