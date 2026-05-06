#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for dictionary operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common import CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .build.dictionary_build_cli import DictionaryBuildCli
from .dictionary_search_cli import DictionarySearchCli

__all__ = ["DictionaryCli"]


class DictionaryCli(ScinoephileCliBase):
    """Build or search Chinese dictionaries."""

    localizations = {
        "zh-hans": {
            "build or search Chinese dictionaries": "构建或查询中文词典",
            "command-line interface for dictionary operations": "词典操作命令行界面",
        },
        "zh-hant": {
            "build or search Chinese dictionaries": "建置或查詢中文詞典",
            "command-line interface for dictionary operations": "詞典操作命令列介面",
        },
    }
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="dictionary_subcommand_name",
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
            DictionaryBuildCli.name(): DictionaryBuildCli,
            DictionarySearchCli.name(): DictionarySearchCli,
        }

    @classmethod
    def _main(
        cls,
        *,
        dictionary_subcommand_name: str,
        **kwargs: Any,
    ):
        """Execute with provided keyword arguments."""
        cls.subcommands()[dictionary_subcommand_name]._main(**kwargs)


if __name__ == "__main__":
    DictionaryCli.main()
