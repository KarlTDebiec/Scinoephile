#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for showing cache statistics."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Literal

from scinoephile.cli.helpers.cache import CACHE_LOCALIZATIONS, add_cache_dir_arg
from scinoephile.common.argument_parsing import get_arg_groups_by_name
from scinoephile.core import ScinoephileError
from scinoephile.core.cache.operations import get_cache_stats
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations

from .output import print_stats

__all__ = ["CacheStatsCli"]

CACHE_STATS_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "cache namespace to inspect": "要检查的缓存命名空间",
        "cache root directory to inspect (default: %(default)s)": (
            "要检查的缓存根目录（默认：%(default)s）"
        ),
        "output format": "输出格式",
        "show cache statistics": "显示缓存统计信息",
    },
    "zh-hant": {
        "cache namespace to inspect": "要檢查的快取命名空間",
        "cache root directory to inspect (default: %(default)s)": (
            "要檢查的快取根目錄（預設：%(default)s）"
        ),
        "output format": "輸出格式",
        "show cache statistics": "顯示快取統計資訊",
    },
}
"""Localized help text keyed by locale and English source text."""


class CacheStatsCli(ScinoephileCliBase):
    """Show cache statistics."""

    localizations = merge_localizations(CACHE_LOCALIZATIONS, CACHE_STATS_LOCALIZATIONS)
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
            "operation arguments",
            "cache arguments",
            optional_arguments_name="additional arguments",
        )

        # Cache arguments
        add_cache_dir_arg(
            arg_groups["cache arguments"],
            help_text="cache root directory to inspect (default: %(default)s)",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--namespace",
            help="cache namespace to inspect",
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
        return "stats"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        cache_dir_path: Path,
        namespace: str | None,
        output_format: Literal["text", "json"],
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()

        # Perform operations
        try:
            stats = get_cache_stats(cache_dir_path, namespace=namespace)
        except (NotADirectoryError, ScinoephileError) as exc:
            parser.error(str(exc))

        # Write outputs
        print_stats(stats, output_format)
