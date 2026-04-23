#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for building dictionary caches."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface

from .dictionary_build_cuhk_cli import DictionaryBuildCuhkCli
from .dictionary_build_gzzj_cli import DictionaryBuildGzzjCli
from .dictionary_build_kaifangcidian_cli import DictionaryBuildKaifangcidianCli
from .dictionary_build_unihan_cli import DictionaryBuildUnihanCli
from .dictionary_build_wiktionary_cli import DictionaryBuildWiktionaryCli

__all__ = ["DictionaryBuildCli"]


class DictionaryBuildCli(CommandLineInterface):
    """Build dictionary caches."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="dictionary_build_subcommand",
            help="dictionary source",
            required=True,
        )
        for name, subcommand in sorted(cls.subcommands().items()):
            subcommand.argparser(subparsers=subparsers)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "build"

    @classmethod
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Names and types of build subcommands.

        Returns:
            mapping of subcommand names to CLI classes
        """
        return {
            DictionaryBuildCuhkCli.name(): DictionaryBuildCuhkCli,
            DictionaryBuildGzzjCli.name(): DictionaryBuildGzzjCli,
            DictionaryBuildKaifangcidianCli.name(): DictionaryBuildKaifangcidianCli,
            DictionaryBuildUnihanCli.name(): DictionaryBuildUnihanCli,
            DictionaryBuildWiktionaryCli.name(): DictionaryBuildWiktionaryCli,
        }

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        subcommand_name = kwargs.pop("dictionary_build_subcommand")
        cls.subcommands()[subcommand_name]._main(**kwargs)


if __name__ == "__main__":
    DictionaryBuildCli.main()
