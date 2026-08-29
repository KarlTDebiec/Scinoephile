#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for inspecting cache usage."""

from __future__ import annotations

from argparse import ArgumentParser
from datetime import timedelta
from pathlib import Path
from typing import Literal

from scinoephile.cli.helpers.cache import CACHE_LOCALIZATIONS, add_cache_root_arg
from scinoephile.common.argument_parsing import duration_arg, get_arg_groups_by_name
from scinoephile.core import ScinoephileError
from scinoephile.core.cache.operations import get_cache_entries, get_cache_stats
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.workflows.cache_registry import CACHE_REGISTRY

from .output import print_entries, print_stats

__all__ = ["CacheInspectCli"]

CACHE_INSPECT_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "cache namespace to inspect": "要检查的缓存命名空间",
        "cache root directory to inspect (default: %(default)s)": (
            "要检查的缓存根目录（默认：%(default)s）"
        ),
        "inspect local cache usage": "检查本地缓存使用情况",
        "only include entries older than a duration such as 7d, 30d, or 12h": (
            "仅包括早于指定时长的条目，例如 7d、30d 或 12h"
        ),
        "output format": "输出格式",
        "show individual entries instead of summary statistics": (
            "显示单个条目而不是汇总统计信息"
        ),
    },
    "zh-hant": {
        "cache namespace to inspect": "要檢查的快取命名空間",
        "cache root directory to inspect (default: %(default)s)": (
            "要檢查的快取根目錄（預設：%(default)s）"
        ),
        "inspect local cache usage": "檢查本機快取使用情況",
        "only include entries older than a duration such as 7d, 30d, or 12h": (
            "僅包括早於指定時長的條目，例如 7d、30d 或 12h"
        ),
        "output format": "輸出格式",
        "show individual entries instead of summary statistics": (
            "顯示個別條目而不是彙總統計資訊"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class CacheInspectCli(ScinoephileCliBase):
    """Inspect local cache usage."""

    localizations = merge_localizations(
        CACHE_LOCALIZATIONS, CACHE_INSPECT_LOCALIZATIONS
    )
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
            help_text="cache root directory to inspect (default: %(default)s)",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--namespace", help="cache namespace to inspect"
        )
        arg_groups["operation arguments"].add_argument(
            "--older-than",
            type=duration_arg,
            help=("only include entries older than a duration such as 7d, 30d, or 12h"),
        )
        arg_groups["operation arguments"].add_argument(
            "--entries",
            action="store_true",
            help="show individual entries instead of summary statistics",
        )
        arg_groups["operation arguments"].add_argument(
            "--format",
            choices=["text", "json"],
            default="text",
            dest="output_format",
            help="output format",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "inspect"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        cache_root_path: Path,
        namespace: str | None,
        older_than: timedelta | None,
        entries: bool,
        output_format: Literal["text", "json"],
    ):
        """Inspect selected cache entries and print a report.

        Arguments:
            _parser: optional preconfigured argument parser
            cache_root_path: cache root directory
            namespace: optional cache namespace
            older_than: optional minimum entry age
            entries: whether to include individual cache entries
            output_format: report output format
        """
        parser = _parser or cls.argparser()

        try:
            if entries:
                cache_entries = get_cache_entries(
                    cache_root_path,
                    CACHE_REGISTRY,
                    namespace=namespace,
                    older_than=older_than,
                )
            else:
                stats = get_cache_stats(
                    cache_root_path,
                    CACHE_REGISTRY,
                    namespace=namespace,
                    older_than=older_than,
                )
        except (NotADirectoryError, ScinoephileError) as exc:
            parser.error(str(exc))

        if entries:
            print_entries(cache_entries, output_format)
        else:
            print_stats(stats, output_format)
