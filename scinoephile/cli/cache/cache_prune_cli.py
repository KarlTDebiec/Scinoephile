#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for pruning cache entries."""

from __future__ import annotations

from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path

from scinoephile.common.argument_parsing import get_arg_groups_by_name
from scinoephile.core import ScinoephileError
from scinoephile.core.cache.operations import get_cache_entries, prune_cache
from scinoephile.core.cli import ScinoephileCliBase

from .argument_types import cache_dir_path_arg, duration_arg
from .output import print_entries

__all__ = ["CachePruneCli"]


class CachePruneCli(ScinoephileCliBase):
    """Prune old cache entries."""

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
            default=cache_dir_path_arg(None),
            dest="cache_dir_path",
            type=cache_dir_path_arg,
            help="cache root directory to inspect (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--older-than",
            required=True,
            type=duration_arg,
            help="delete entries older than a duration such as 7d, 30d, or 12h",
        )
        arg_groups["operation arguments"].add_argument(
            "--namespace",
            default=None,
            help="cache namespace to inspect",
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
        yes: bool,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        if not dry_run and not yes:
            parser.error("--yes is required unless --dry-run is specified")

        try:
            if dry_run:
                cutoff = datetime.now().astimezone() - older_than
                cutoff_entries = [
                    entry
                    for entry in get_cache_entries(cache_dir_path, namespace=namespace)
                    if entry.modified_at < cutoff
                ]
                print_entries(cutoff_entries, "text")
            else:
                deleted_entries = prune_cache(
                    cache_dir_path, older_than=older_than, namespace=namespace
                )
                print_entries(deleted_entries, "text")
        except (NotADirectoryError, ScinoephileError) as exc:
            parser.error(str(exc))
