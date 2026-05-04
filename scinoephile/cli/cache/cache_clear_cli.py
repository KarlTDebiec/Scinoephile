#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for clearing cache entries."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import TypedDict, Unpack

from scinoephile.common.argument_parsing import get_arg_groups_by_name
from scinoephile.core import ScinoephileError
from scinoephile.core.cache import clear_cache, get_cache_entries
from scinoephile.core.cli import ScinoephileCliBase

from .argument_types import cache_dir_path_arg
from .output import print_entries

__all__ = ["CacheClearCli"]


class _CacheClearCliKwargs(TypedDict, total=False):
    """Keyword arguments for CacheClearCli."""

    _parser: ArgumentParser
    """Argument parser."""
    cache_dir_path: str | None
    """Cache root directory path."""
    namespace: str | None
    """Cache namespace filter."""
    all_namespaces: bool
    """Whether to clear every namespace."""
    dry_run: bool
    """Whether to preview deletion."""
    yes: bool
    """Whether deletion is confirmed."""


class CacheClearCli(ScinoephileCliBase):
    """Clear cache entries."""

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
    def _main(cls, **kwargs: Unpack[_CacheClearCliKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        parser = kwargs.pop("_parser", cls.argparser())
        cache_dir_path = cache_dir_path_arg(kwargs.pop("cache_dir_path"))
        namespace = kwargs.pop("namespace")
        all_namespaces = kwargs.pop("all_namespaces")
        dry_run = kwargs.pop("dry_run")
        yes = kwargs.pop("yes")
        if not dry_run and not yes:
            parser.error("--yes is required unless --dry-run is specified")
        if namespace is not None and all_namespaces:
            parser.error("--namespace and --all may not be used together")

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
                print_entries(entries, "text")
            else:
                deleted_entries = clear_cache(
                    cache_dir_path,
                    namespace=namespace,
                    all_namespaces=all_namespaces,
                )
                print_entries(deleted_entries, "text")
        except (NotADirectoryError, ScinoephileError) as exc:
            parser.error(str(exc))
