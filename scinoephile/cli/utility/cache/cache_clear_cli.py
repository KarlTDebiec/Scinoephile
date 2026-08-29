#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for clearing cache entries."""

from __future__ import annotations

from argparse import ArgumentParser
from datetime import timedelta
from pathlib import Path

from scinoephile.cli.helpers.cache import CACHE_LOCALIZATIONS, add_cache_root_arg
from scinoephile.common.argument_parsing import (
    duration_arg,
    get_arg_groups_by_name,
    int_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cache.operations import clear_cache
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.workflows.cache_registry import CACHE_REGISTRY

from .output import print_entries

__all__ = ["CacheClearCli"]

CACHE_CLEAR_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "cache namespace to clear": "要清除的缓存命名空间",
        "cache root directory to clear (default: %(default)s)": (
            "要清除的缓存根目录（默认：%(default)s）"
        ),
        "clear matching cache entries": "清除匹配的缓存条目",
        "clear the cache root; with --older-than, clear registered entries only": (
            "清除缓存根目录中的所有内容；与 --older-than 一起使用时，仅清除已注册的条目"
        ),
        "confirm destructive deletion": "确认破坏性删除",
        "only clear registered entries older than a duration such as 7d, 30d, or 12h": (
            "仅清除早于指定时长的已注册条目，例如 7d、30d 或 12h"
        ),
        "maximum entries to print; use 0 to show all (default: %(default)s)": (
            "最多输出的条目数；使用 0 显示全部（默认：%(default)s）"
        ),
        "show what would be deleted without deleting files": (
            "显示将删除的内容但不删除文件"
        ),
    },
    "zh-hant": {
        "cache namespace to clear": "要清除的快取命名空間",
        "cache root directory to clear (default: %(default)s)": (
            "要清除的快取根目錄（預設：%(default)s）"
        ),
        "clear matching cache entries": "清除符合條件的快取條目",
        "clear the cache root; with --older-than, clear registered entries only": (
            "清除快取根目錄中的所有內容；與 --older-than 一起使用時，僅清除已註冊的條目"
        ),
        "confirm destructive deletion": "確認破壞性刪除",
        "only clear registered entries older than a duration such as 7d, 30d, or 12h": (
            "僅清除早於指定時長的已註冊條目，例如 7d、30d 或 12h"
        ),
        "maximum entries to print; use 0 to show all (default: %(default)s)": (
            "最多輸出的條目數；使用 0 顯示全部（預設：%(default)s）"
        ),
        "show what would be deleted without deleting files": (
            "顯示將刪除的內容但不刪除檔案"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class CacheClearCli(ScinoephileCliBase):
    """Clear matching cache entries."""

    localizations = merge_localizations(CACHE_LOCALIZATIONS, CACHE_CLEAR_LOCALIZATIONS)
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
        add_cache_root_arg(
            arg_groups["input arguments"],
            help_text="cache root directory to clear (default: %(default)s)",
        )

        # Operation arguments
        scope_group = arg_groups["operation arguments"].add_mutually_exclusive_group(
            required=True
        )
        scope_group.add_argument("--namespace", help="cache namespace to clear")
        scope_group.add_argument(
            "--all",
            action="store_true",
            dest="entire_cache",
            help=(
                "clear the cache root; with --older-than, clear registered entries only"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--older-than",
            type=duration_arg,
            help=(
                "only clear registered entries older than a duration such as 7d, "
                "30d, or 12h"
            ),
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
            "--yes", action="store_true", help="confirm destructive deletion"
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "clear"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        cache_root_path: Path,
        namespace: str | None,
        entire_cache: bool,
        older_than: timedelta | None,
        dry_run: bool,
        limit: int,
        yes: bool,
    ):
        """Remove selected cache entries and print a summary.

        Arguments:
            _parser: optional preconfigured argument parser
            cache_root_path: cache root directory
            namespace: optional cache namespace
            entire_cache: whether to select the entire cache
            older_than: optional minimum entry age
            dry_run: whether to report without deleting entries
            limit: maximum number of entries to remove
            yes: whether to skip interactive confirmation
        """
        # Validate arguments
        parser = _parser or cls.argparser()
        if not dry_run and not yes:
            parser.error("--yes is required unless --dry-run is specified")
        if namespace is None and not entire_cache:
            parser.error("--namespace is required unless --all is specified")
        if namespace is not None and entire_cache:
            parser.error("--namespace and --all may not be used together")

        # Perform operations
        try:
            entries = clear_cache(
                cache_root_path,
                CACHE_REGISTRY,
                namespace=namespace,
                entire_cache=entire_cache,
                older_than=older_than,
                dry_run=dry_run,
            )
        except (NotADirectoryError, ScinoephileError) as exc:
            parser.error(str(exc))

        # Write outputs
        print_entries(entries, "text", limit=limit)
