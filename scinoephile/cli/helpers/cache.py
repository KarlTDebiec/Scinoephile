#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CLI helpers for cache directory arguments."""

from __future__ import annotations

from argparse import _ArgumentGroup  # noqa: PLC2701
from pathlib import Path

from scinoephile.core.paths import get_runtime_cache_dir_path

__all__ = [
    "CACHE_DIR_HELP",
    "CACHE_LOCALIZATIONS",
    "add_cache_dir_arg",
]

CACHE_DIR_HELP = "cache directory path (default: %(default)s)"
"""Generic help text for cache directory path arguments."""

CACHE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        CACHE_DIR_HELP: "缓存目录路径（默认：%(default)s）",
        "cache arguments": "缓存参数",
    },
    "zh-hant": {
        CACHE_DIR_HELP: "快取目錄路徑（預設：%(default)s）",
        "cache arguments": "快取參數",
    },
}
"""Localized text shared by CLIs that expose cache directory arguments."""


def add_cache_dir_arg(
    cache_arg_group: _ArgumentGroup,
    *default_parts: str | None,
    help_text: str = CACHE_DIR_HELP,
):
    """Add a standard cache directory argument to an argument group.

    Arguments:
        cache_arg_group: group to which the cache directory argument is added
        *default_parts: runtime cache subpath parts used for the default path
        help_text: help text for the cache directory argument
    """
    cache_arg_group.add_argument(
        "--cache-dir",
        default=_cache_dir_path_arg(*default_parts),
        dest="cache_dir_path",
        type=_cache_dir_path_arg,
        help=help_text,
    )


def _cache_dir_path_arg(*values: str | None) -> Path:
    """Resolve a cache directory CLI argument.

    Arguments:
        *values: path value or runtime cache subpath parts
    Returns:
        resolved cache directory path
    """
    if len(values) == 0 or values == (None,):
        return get_runtime_cache_dir_path(create=False)
    if len(values) > 1:
        parts = [value for value in values if value is not None]
        return get_runtime_cache_dir_path(*parts, create=False)
    value = values[0]
    if value is None:
        return get_runtime_cache_dir_path(create=False)
    return Path(value).expanduser().resolve()
