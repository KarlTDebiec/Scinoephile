#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for utility operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common import CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .cache import CacheCli
from .optimization import OptimizationCli

__all__ = ["UtilityCli"]

UTILITY_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for utility operations": "实用工具命令行界面",
        "run utility commands": "运行实用工具命令",
    },
    "zh-hant": {
        "command-line interface for utility operations": "實用工具命令列介面",
        "run utility commands": "執行實用工具命令",
    },
}
"""Localized help text keyed by locale and English source text."""


class UtilityCli(ScinoephileCliBase):
    """Run utility commands."""

    localizations = UTILITY_LOCALIZATIONS
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="utility_subcommand_name",
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
            CacheCli.name(): CacheCli,
            OptimizationCli.name(): OptimizationCli,
        }

    @classmethod
    def _main(
        cls,
        *,
        utility_subcommand_name: str,
        **kwargs: Any,
    ):
        """Execute with provided keyword arguments."""
        cls.subcommands()[utility_subcommand_name]._main(**kwargs)


if __name__ == "__main__":
    UtilityCli.main()
