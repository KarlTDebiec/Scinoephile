#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for Scinoephile."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.cli.eng_cli import EngCli
from scinoephile.cli.eng_zho_cli import EngZhoCli
from scinoephile.cli.zho_cli import ZhoCli
from scinoephile.common import CommandLineInterface
from scinoephile.common.command_line_interface import CLIKwargs


class ScinoephileCli(CommandLineInterface):
    """Command-line interface for Scinoephile."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="subcommand",
            help="subcommand",
            required=True,
        )
        subcommands = cls.subcommands()
        for name in sorted(subcommands):
            subcommands[name].argparser(subparsers=subparsers)

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments."""
        subcommand_name = kwargs.pop("subcommand")
        subcommand_cli_class = cls.subcommands()[subcommand_name]
        subcommand_cli_class._main(**kwargs)

    @classmethod
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Names and types of tools wrapped by command-line interface."""
        return {
            EngCli.name(): EngCli,
            ZhoCli.name(): ZhoCli,
            EngZhoCli.name(): EngZhoCli,
        }


if __name__ == "__main__":
    ScinoephileCli.main()
