#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for pruning cache entries."""

from __future__ import annotations

from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path

from scinoephile.cli.helpers.cache import CACHE_LOCALIZATIONS, add_cache_dir_arg
from scinoephile.common.argument_parsing import (
    duration_arg,
    get_arg_groups_by_name,
    int_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cache.operations import get_cache_entries, prune_cache
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations

from .output import print_entries

__all__ = ["CachePruneCli"]

CACHE_PRUNE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "cache namespace to inspect": "要检查的缓存命名空间",
        "cache root directory to inspect (default: %(default)s)": (
            "要检查的缓存根目录（默认：%(default)s）"
        ),
        "confirm destructive deletion": "确认破坏性删除",
        "delete entries older than a duration such as 7d, 30d, or 12h": (
            "删除早于指定时长的条目，例如 7d、30d 或 12h"
        ),
        "maximum entries to print; use 0 to show all (default: %(default)s)": (
            "最多输出的条目数；使用 0 显示全部（默认：%(default)s）"
        ),
        "prune old cache entries": "清理旧缓存条目",
        "show what would be deleted without deleting files": (
            "显示将删除的内容但不删除文件"
        ),
    },
    "zh-hant": {
        "cache namespace to inspect": "要檢查的快取命名空間",
        "cache root directory to inspect (default: %(default)s)": (
            "要檢查的快取根目錄（預設：%(default)s）"
        ),
        "confirm destructive deletion": "確認破壞性刪除",
        "delete entries older than a duration such as 7d, 30d, or 12h": (
            "刪除早於指定時長的條目，例如 7d、30d 或 12h"
        ),
        "maximum entries to print; use 0 to show all (default: %(default)s)": (
            "最多輸出的條目數；使用 0 顯示全部（預設：%(default)s）"
        ),
        "prune old cache entries": "清理舊快取條目",
        "show what would be deleted without deleting files": (
            "顯示將刪除的內容但不刪除檔案"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class CachePruneCli(ScinoephileCliBase):
    """Prune old cache entries."""

    localizations = merge_localizations(CACHE_LOCALIZATIONS, CACHE_PRUNE_LOCALIZATIONS)
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)
        arg_groups = get_arg_groups_by_name(
            parser,
            "input arguments",
            "operation arguments",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        add_cache_dir_arg(
            arg_groups["input arguments"],
            help_text="cache root directory to inspect (default: %(default)s)",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--older-than",
            required=True,
            type=duration_arg,
            help="delete entries older than a duration such as 7d, 30d, or 12h",
        )
        arg_groups["operation arguments"].add_argument(
            "--namespace",
            help="cache namespace to inspect",
        )
        arg_groups["operation arguments"].add_argument(
            "--dry-run",
            action="store_true",
            help="show what would be deleted without deleting files",
        )
        arg_groups["operation arguments"].add_argument(
            "--limit",
            default=100,
            type=int_arg(min_value=0),
            help="maximum entries to print; use 0 to show all (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--yes",
            action="store_true",
            help="confirm destructive deletion",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "prune"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        cache_dir_path: Path,
        older_than: timedelta,
        namespace: str | None,
        dry_run: bool,
        limit: int,
        yes: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if not dry_run and not yes:
            parser.error("--yes is required unless --dry-run is specified")

        # Perform operations
        try:
            if dry_run:
                cutoff = datetime.now().astimezone() - older_than
                entries = [
                    entry
                    for entry in get_cache_entries(cache_dir_path, namespace=namespace)
                    if entry.modified_at < cutoff
                ]
            else:
                entries = prune_cache(
                    cache_dir_path, older_than=older_than, namespace=namespace
                )
        except (NotADirectoryError, ScinoephileError) as exc:
            parser.error(str(exc))

        # Write outputs
        print_entries(entries, "text", limit=limit)
