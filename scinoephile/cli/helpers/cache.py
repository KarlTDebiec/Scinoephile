#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CLI helpers for cache arguments."""

from __future__ import annotations

from argparse import _ArgumentGroup  # noqa: PLC2701
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path

from scinoephile.common.argument_parsing import output_dir_arg
from scinoephile.core.paths import get_runtime_cache_root_path

from .argument_bundle_field_action import ArgumentBundleFieldAction

__all__ = [
    "CACHE_LOCALIZATIONS",
    "CacheArguments",
    "add_cache_args",
    "add_cache_root_arg",
]

CACHE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "cache root directory path (default: %(field_default)s)": (
            "缓存根目录路径（默认：%(field_default)s）"
        ),
        "overwrite matching cache files": "覆盖匹配的缓存文件",
        "cache arguments": "缓存参数",
    },
    "zh-hant": {
        "cache root directory path (default: %(field_default)s)": (
            "快取根目錄路徑（預設：%(field_default)s）"
        ),
        "overwrite matching cache files": "覆寫匹配的快取檔案",
        "cache arguments": "快取參數",
    },
}
"""Localized text shared by CLIs that expose cache arguments."""


@dataclass(frozen=True)
class CacheArguments:
    """Parsed cache CLI arguments."""

    root_path: Path = field(
        default_factory=partial(get_runtime_cache_root_path, create=False)
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
        field_name="root_path",
        metavar="CACHE_DIR",
        type=output_dir_arg(create=False),
        help="cache root directory path (default: %(field_default)s)",
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
        help="overwrite matching cache files",
    )


def add_cache_root_arg(
    cache_arg_group: _ArgumentGroup,
    help_text: str = "cache root directory path (default: %(default)s)",
):
    """Add a standard cache root argument to an argument group.

    Arguments:
        cache_arg_group: group to which the cache directory argument is added
        help_text: help text for the cache directory argument
    """
    cache_arg_group.add_argument(
        "--cache-dir",
        default=get_runtime_cache_root_path(create=False),
        dest="cache_root_path",
        type=output_dir_arg(create=False),
        help=help_text,
    )
