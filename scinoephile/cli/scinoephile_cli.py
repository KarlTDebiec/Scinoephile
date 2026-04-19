#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for Scinoephile."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface

from .analysis.analysis_cli import AnalysisCli
from .dictionary.dictionary_cli import DictionaryCli
from .eng.eng_cli import EngCli
from .sync_cli import SyncCli
from .timewarp_cli import TimewarpCli
from .yue_cli import YueCli
from .zho.zho_cli import ZhoCli


class ScinoephileCli(CommandLineInterface):
    """Command-line interface for Scinoephile."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
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
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "scinoephile"

    @classmethod
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Names and types of tools wrapped by command-line interface.

        Returns:
            mapping of subcommand names to CLI classes
        """
        return {
            AnalysisCli.name(): AnalysisCli,
            DictionaryCli.name(): DictionaryCli,
            EngCli.name(): EngCli,
            SyncCli.name(): SyncCli,
            TimewarpCli.name(): TimewarpCli,
            YueCli.name(): YueCli,
            ZhoCli.name(): ZhoCli,
        }

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        subcommand_name = kwargs.pop("subcommand")
        subcommand_cli_class = cls.subcommands()[subcommand_name]
        subcommand_cli_class._main(**kwargs)


if __name__ == "__main__":
    ScinoephileCli.main()
