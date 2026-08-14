#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared file helpers for tests."""

from __future__ import annotations

from os import utime
from pathlib import Path

__all__ = ["get_python_files", "set_mtime", "write_cache_file"]

_EXCLUDED_DIR_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "local",
}
"""Directory names excluded from recursive source scans."""


def get_python_files(target_dir_path: Path) -> list[Path]:
    """Get Python files under a target directory.

    Arguments:
        target_dir_path: directory path to scan
    Returns:
        sorted Python file paths
    """
    return sorted(
        file_path
        for file_path in target_dir_path.rglob("*.py")
        if not _is_excluded_path(file_path, target_dir_path)
    )


def _is_excluded_path(file_path: Path, target_dir_path: Path) -> bool:
    """Check whether a discovered file falls under an excluded directory.

    Arguments:
        file_path: discovered file path
        target_dir_path: recursive scan root
    Returns:
        whether the file should be omitted from the scan
    """
    relative_file_path = file_path.relative_to(target_dir_path)
    return any(part in _EXCLUDED_DIR_NAMES for part in relative_file_path.parts)


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
