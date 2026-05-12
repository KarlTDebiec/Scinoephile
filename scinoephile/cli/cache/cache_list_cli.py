#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for listing cache entries."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Literal

from scinoephile.common.argument_parsing import get_arg_groups_by_name, int_arg
from scinoephile.core import ScinoephileError
from scinoephile.core.cache.operations import get_cache_entries
from scinoephile.core.cli import ScinoephileCliBase

from .argument_types import cache_dir_path_arg
from .output import print_entries, sort_entries

__all__ = ["CacheListCli"]


class CacheListCli(ScinoephileCliBase):
    """List cache entries."""

    localizations = {
        "zh-hans": {
            "cache namespace to inspect": "要检查的缓存命名空间",
            "cache root directory to inspect (default: %(default)s)": (
                "要检查的缓存根目录（默认：%(default)s）"
            ),
            "list cache entries": "列出缓存条目",
            "maximum number of entries to show": "要显示的最大条目数",
            "output format": "输出格式",
            "reverse sort order": "反转排序顺序",
            "sort field": "排序字段",
        },
        "zh-hant": {
            "cache namespace to inspect": "要檢查的快取命名空間",
            "cache root directory to inspect (default: %(default)s)": (
                "要檢查的快取根目錄（預設：%(default)s）"
            ),
            "list cache entries": "列出快取條目",
            "maximum number of entries to show": "要顯示的最大條目數",
            "output format": "輸出格式",
            "reverse sort order": "反轉排序順序",
            "sort field": "排序欄位",
        },
    }
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
        arg_groups["input arguments"].add_argument(
            "--cache-dir",
            default=cache_dir_path_arg(None),
            dest="cache_dir_path",
            type=cache_dir_path_arg,
            help="cache root directory to inspect (default: %(default)s)",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--namespace",
            default=None,
            help="cache namespace to inspect",
        )
        arg_groups["operation arguments"].add_argument(
            "--format",
            choices=["text", "json", "jsonl"],
            default="text",
            dest="output_format",
            help="output format",
        )
        arg_groups["operation arguments"].add_argument(
            "--limit",
            type=int_arg(min_value=1),
            default=None,
            help="maximum number of entries to show",
        )
        arg_groups["operation arguments"].add_argument(
            "--sort",
            choices=["name", "size", "mtime", "atime"],
            default="name",
            help="sort field",
        )
        arg_groups["operation arguments"].add_argument(
            "--reverse",
            action="store_true",
            help="reverse sort order",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "list"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        cache_dir_path: Path,
        namespace: str | None,
        output_format: Literal["text", "json", "jsonl"],
        limit: int | None,
        sort: Literal["name", "size", "mtime", "atime"],
        reverse: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()

        # Perform operations
        try:
            entries = get_cache_entries(cache_dir_path, namespace=namespace)
        except (NotADirectoryError, ScinoephileError) as exc:
            parser.error(str(exc))
        entries = sort_entries(entries, sort=sort, reverse=reverse)
        if limit is not None:
            entries = entries[:limit]

        # Write outputs
        print_entries(entries, output_format)
