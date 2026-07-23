#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared file helpers for tests."""

from __future__ import annotations

from os import utime
from pathlib import Path

__all__ = [
    "set_mtime",
    "write_cache_file",
]


def set_mtime(path: Path, timestamp: float) -> None:
    """Set a path modification and access time.

    Arguments:
        path: path to modify
        timestamp: timestamp to set
    """
    utime(path, (timestamp, timestamp))


def write_cache_file(path: Path, text: str = "{}") -> Path:
    """Write a cache file.

    Arguments:
        path: path to write
        text: text to write
    Returns:
        written path
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path
