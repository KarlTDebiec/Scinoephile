#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for showing cache statistics."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Literal, TypedDict, Unpack

from scinoephile.common.argument_parsing import get_arg_groups_by_name
from scinoephile.core import ScinoephileError
from scinoephile.core.cache.operations import get_cache_stats
from scinoephile.core.cli import ScinoephileCliBase

from .argument_types import cache_dir_path_arg
from .output import print_stats

__all__ = ["CacheStatsCli"]


class _CacheStatsCliKwargs(TypedDict, total=False):
    """Keyword arguments for CacheStatsCli."""

    _parser: ArgumentParser
    """Argument parser."""
    cache_dir_path: str | None
    """Cache root directory path."""
    namespace: str | None
    """Cache namespace filter."""
    output_format: Literal["text", "json"]
    """Output format."""


class CacheStatsCli(ScinoephileCliBase):
    """Show cache statistics."""

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

        arg_groups["input arguments"].add_argument(
            "--cache-dir",
            default=None,
            dest="cache_dir_path",
            help="cache root directory to inspect",
        )
        arg_groups["operation arguments"].add_argument(
            "--namespace",
            default=None,
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
    def _main(cls, **kwargs: Unpack[_CacheStatsCliKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        parser = kwargs.pop("_parser", cls.argparser())
        cache_dir_path = cache_dir_path_arg(kwargs.pop("cache_dir_path"))
        namespace = kwargs.pop("namespace")
        output_format = kwargs.pop("output_format")

        try:
            stats = get_cache_stats(cache_dir_path, namespace=namespace)
        except (NotADirectoryError, ScinoephileError) as exc:
            parser.error(str(exc))
        print_stats(stats, output_format)
