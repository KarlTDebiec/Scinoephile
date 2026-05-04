#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for cache operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common import CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .cache_clear_cli import CacheClearCli
from .cache_list_cli import CacheListCli
from .cache_prune_cli import CachePruneCli
from .cache_stats_cli import CacheStatsCli

__all__ = ["CacheCli"]


class CacheCli(ScinoephileCliBase):
    """Inspect and invalidate local caches."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="cache_subcommand_name",
            help="subcommand",
            required=True,
        )
        subcommands = cls.subcommands()
        for name in sorted(subcommands):
            subcommands[name].argparser(subparsers=subparsers)

    @classmethod
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Names and types of tools wrapped by command-line interface.

        Returns:
            mapping of subcommand names to CLI classes
        """
        return {
            CacheClearCli.name(): CacheClearCli,
            CacheListCli.name(): CacheListCli,
            CachePruneCli.name(): CachePruneCli,
            CacheStatsCli.name(): CacheStatsCli,
        }

    @classmethod
    def _main(
        cls,
        *,
        cache_subcommand_name: str,
        **kwargs: Any,
    ):
        """Execute with provided keyword arguments."""
        cls.subcommands()[cache_subcommand_name]._main(**kwargs)


if __name__ == "__main__":
    CacheCli.main()
