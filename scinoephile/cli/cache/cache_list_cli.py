#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for listing cache entries."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Literal, TypedDict, Unpack

from scinoephile.common.argument_parsing import get_arg_groups_by_name, int_arg
from scinoephile.core import ScinoephileError
from scinoephile.core.cache.operations import get_cache_entries
from scinoephile.core.cli import ScinoephileCliBase

from .argument_types import cache_dir_path_arg
from .output import print_entries, sort_entries

__all__ = ["CacheListCli"]


class _CacheListCliKwargs(TypedDict, total=False):
    """Keyword arguments for CacheListCli."""

    _parser: ArgumentParser
    """Argument parser."""
    cache_dir_path: str | None
    """Cache root directory path."""
    namespace: str | None
    """Cache namespace filter."""
    output_format: Literal["text", "json", "jsonl"]
    """Output format."""
    limit: int | None
    """Maximum number of entries to show."""
    sort: Literal["name", "size", "mtime", "atime"]
    """Sort field."""
    reverse: bool
    """Whether to reverse sort order."""


class CacheListCli(ScinoephileCliBase):
    """List cache entries."""

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
    def _main(cls, **kwargs: Unpack[_CacheListCliKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        parser = kwargs.pop("_parser", cls.argparser())
        cache_dir_path = cache_dir_path_arg(kwargs.pop("cache_dir_path"))
        namespace = kwargs.pop("namespace")
        output_format = kwargs.pop("output_format")
        limit = kwargs.pop("limit")
        sort = kwargs.pop("sort")
        reverse = kwargs.pop("reverse")

        try:
            entries = get_cache_entries(cache_dir_path, namespace=namespace)
        except (NotADirectoryError, ScinoephileError) as exc:
            parser.error(str(exc))
        entries = sort_entries(entries, sort=sort, reverse=reverse)
        if limit is not None:
            entries = entries[:limit]
        print_entries(entries, output_format)
