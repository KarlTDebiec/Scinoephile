#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CLI helpers for cache arguments."""

from __future__ import annotations

from argparse import _ArgumentGroup  # noqa: PLC2701
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path

from scinoephile.common.argument_parsing import output_dir_arg
from scinoephile.core.paths import get_runtime_cache_dir_path

from .argument_bundle_field_action import ArgumentBundleFieldAction

__all__ = [
    "CACHE_DIR_HELP",
    "CACHE_LOCALIZATIONS",
    "CACHE_OVERWRITE_HELP",
    "CacheArguments",
    "add_cache_args",
    "add_cache_dir_arg",
]

CACHE_DIR_HELP = "cache directory path (default: %(default)s)"
"""Generic help text for cache directory path arguments."""

CACHE_OVERWRITE_HELP = "overwrite matching cache files"
"""Generic help text for cache overwrite arguments."""

CACHE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        CACHE_DIR_HELP: "缓存目录路径（默认：%(default)s）",
        CACHE_OVERWRITE_HELP: "覆盖匹配的缓存文件",
        "cache arguments": "缓存参数",
    },
    "zh-hant": {
        CACHE_DIR_HELP: "快取目錄路徑（預設：%(default)s）",
        CACHE_OVERWRITE_HELP: "覆寫匹配的快取檔案",
        "cache arguments": "快取參數",
    },
}
"""Localized text shared by CLIs that expose cache arguments."""


@dataclass(frozen=True)
class CacheArguments:
    """Parsed cache CLI arguments."""

    dir_path: Path = field(
        default_factory=partial(get_runtime_cache_dir_path, create=False)
    )
    """Cache root directory path."""
    overwrite: bool = False
    """Whether matching cache files should be overwritten."""


def add_cache_args(cache_arg_group: _ArgumentGroup):
    """Add standard cache arguments to an argument group.

    Arguments:
        cache_arg_group: group to which cache arguments are added
    """
    default = CacheArguments()
    cache_arg_group.add_argument(
        "--cache-dir",
        action=ArgumentBundleFieldAction,
        bundle_type=CacheArguments,
        default=default,
        dest="cache_args",
        field_name="dir_path",
        metavar="CACHE_DIR",
        type=output_dir_arg(create=False),
        help=CACHE_DIR_HELP,
    )
    cache_arg_group.add_argument(
        "--cache-overwrite",
        action=ArgumentBundleFieldAction,
        bundle_type=CacheArguments,
        const=True,
        default=default,
        dest="cache_args",
        field_name="overwrite",
        nargs=0,
        help=CACHE_OVERWRITE_HELP,
    )


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
        default=_cache_dir_default_path(*default_parts),
        dest="cache_dir_path",
        type=output_dir_arg(create=False),
        help=help_text,
    )


def _cache_dir_default_path(*default_parts: str | None) -> Path:
    """Resolve a default cache directory path.

    Arguments:
        *default_parts: runtime cache subpath parts
    Returns:
        resolved default cache directory path
    """
    if len(default_parts) == 0 or default_parts == (None,):
        return get_runtime_cache_dir_path(create=False)
    parts = [default_part for default_part in default_parts if default_part is not None]
    if not parts:
        return get_runtime_cache_dir_path(create=False)
    return get_runtime_cache_dir_path(*parts, create=False)
