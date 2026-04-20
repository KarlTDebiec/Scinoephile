#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for 粤文 subtitle operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface

from .yue_process_cli import YueProcessCli
from .yue_transcribe_cli import YueTranscribeCli

__all__ = ["YueCli"]


class YueCli(CommandLineInterface):
    """Modify Written Cantonese (粤文) subtitles."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        # Subcommands
        subparsers = parser.add_subparsers(
            dest="yue_subcommand",
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
            YueProcessCli.name(): YueProcessCli,
            YueTranscribeCli.name(): YueTranscribeCli,
        }

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        subcommand_name = kwargs.pop("yue_subcommand")
        subcommand_cli_class = cls.subcommands()[subcommand_name]
        subcommand_cli_class._main(**kwargs)


if __name__ == "__main__":
    YueCli.main()
