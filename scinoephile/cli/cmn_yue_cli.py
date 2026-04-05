#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for 中文/粤文 shared operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Unpack

from scinoephile.cli.cmn_yue_dictionary_cli import CmnYueDictionaryCli
from scinoephile.common import CLIKwargs, CommandLineInterface

if TYPE_CHECKING:
    from argparse import ArgumentParser


class CmnYueCli(CommandLineInterface):
    """Command-line interface for 中文/粤文 shared operations."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="cmn_yue_subcommand",
            help="subcommand",
            required=True,
        )
        subcommands = cls.subcommands()
        for name in sorted(subcommands):
            subcommands[name].argparser(subparsers=subparsers)

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments."""
        subcommand_name = kwargs.pop("cmn_yue_subcommand")
        subcommand_cli_class = cls.subcommands()[subcommand_name]
        subcommand_cli_class._main(**kwargs)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return "cmn_yue"

    @classmethod
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Names and types of tools wrapped by command-line interface."""
        return {
            CmnYueDictionaryCli.name(): CmnYueDictionaryCli,
        }


if __name__ == "__main__":
    CmnYueCli.main()
