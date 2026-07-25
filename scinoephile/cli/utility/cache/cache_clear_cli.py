#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for clearing cache entries."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.helpers.cache import CACHE_LOCALIZATIONS, add_cache_dir_arg
from scinoephile.common.argument_parsing import get_arg_groups_by_name, int_arg
from scinoephile.core import ScinoephileError
from scinoephile.core.cache.operations import clear_cache, get_cache_entries
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations

from .output import print_entries

__all__ = ["CacheClearCli"]

CACHE_CLEAR_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "cache namespace to clear": "要清除的缓存命名空间",
        "cache root directory to inspect (default: %(default)s)": (
            "要检查的缓存根目录（默认：%(default)s）"
        ),
        "clear cache entries": "清除缓存条目",
        "clear every discovered namespace": "清除所有发现的命名空间",
        "confirm destructive deletion": "确认破坏性删除",
        "maximum entries to print; use 0 to show all (default: %(default)s)": (
            "最多输出的条目数；使用 0 显示全部（默认：%(default)s）"
        ),
        "show what would be deleted without deleting files": (
            "显示将删除的内容但不删除文件"
        ),
    },
    "zh-hant": {
        "cache namespace to clear": "要清除的快取命名空間",
        "cache root directory to inspect (default: %(default)s)": (
            "要檢查的快取根目錄（預設：%(default)s）"
        ),
        "clear cache entries": "清除快取條目",
        "clear every discovered namespace": "清除所有發現的命名空間",
        "confirm destructive deletion": "確認破壞性刪除",
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
    """Clear cache entries."""

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
        add_cache_dir_arg(
            arg_groups["input arguments"],
            help_text="cache root directory to inspect (default: %(default)s)",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--namespace",
            help="cache namespace to clear",
        )
        arg_groups["operation arguments"].add_argument(
            "--all",
            action="store_true",
            dest="all_namespaces",
            help="clear every discovered namespace",
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
        return "clear"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        cache_dir_path: Path,
        namespace: str | None,
        all_namespaces: bool,
        dry_run: bool,
        limit: int,
        yes: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if not dry_run and not yes:
            parser.error("--yes is required unless --dry-run is specified")
        if namespace is not None and all_namespaces:
            parser.error("--namespace and --all may not be used together")

        # Perform operations
        try:
            if dry_run:
                if all_namespaces:
                    entries = get_cache_entries(cache_dir_path)
                elif namespace is None:
                    raise ScinoephileError(
                        "--namespace is required unless --all is specified"
                    )
                else:
                    entries = get_cache_entries(cache_dir_path, namespace=namespace)
            else:
                entries = clear_cache(
                    cache_dir_path,
                    namespace=namespace,
                    all_namespaces=all_namespaces,
                )
        except (NotADirectoryError, ScinoephileError) as exc:
            parser.error(str(exc))

        # Write outputs
        print_entries(entries, "text", limit=limit)
