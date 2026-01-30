#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for English/中文 bilingual operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.cli.eng_zho_sync_cli import EngZhoSyncCli
from scinoephile.common import CommandLineInterface


class EngZhoCli(CommandLineInterface):
    """Command-line interface for English/中文 bilingual operations."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="eng_zho_subcommand",
            help="subcommand",
            required=True,
        )
        for name in sorted(cls.subcommands()):
            cls.subcommands()[name].argparser(subparsers=subparsers)

    @classmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments."""
        subcommand_name = kwargs.pop("eng_zho_subcommand")
        subcommand_cli_class = cls.subcommands()[subcommand_name]
        subcommand_cli_class._main(**kwargs)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return "eng_zho"

    @classmethod
    def subcommands(cls) -> dict[str, type[EngZhoSyncCli]]:
        """Names and types of tools wrapped by command-line interface."""
        return {
            EngZhoSyncCli.name(): EngZhoSyncCli,
        }


if __name__ == "__main__":
    EngZhoCli.main()
