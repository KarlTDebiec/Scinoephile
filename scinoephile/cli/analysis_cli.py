#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for analysis operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.cli.analysis_cer_cli import AnalysisCerCli
from scinoephile.cli.analysis_diff_cli import AnalysisDiffCli
from scinoephile.common import CLIKwargs, CommandLineInterface


class AnalysisCli(CommandLineInterface):
    """Command-line interface wrapper for analysis subcommands."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="analysis_subcommand",
            help="subcommand",
            required=True,
        )
        subcommands = cls.subcommands()
        for name in sorted(subcommands):
            subcommands[name].argparser(subparsers=subparsers)

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        subcommand_name = kwargs.pop("analysis_subcommand")
        subcommand_cli_class = cls.subcommands()[subcommand_name]
        subcommand_cli_class._main(**kwargs)

    @classmethod
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Names and types of tools wrapped by command-line interface.

        Returns:
            mapping of subcommand names to CLI classes
        """
        return {
            AnalysisCerCli.name(): AnalysisCerCli,
            AnalysisDiffCli.name(): AnalysisDiffCli,
        }


if __name__ == "__main__":
    AnalysisCli.main()
