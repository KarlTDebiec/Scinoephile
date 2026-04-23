#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for English subtitle operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .eng_fuse_cli import EngFuseCli
from .eng_process_cli import EngProcessCli
from .eng_validate_ocr_cli import EngValidateOcrCli

__all__ = ["EngCli"]


class EngCli(ScinoephileCliBase):
    """Modify English subtitles."""

    localizations = {
        "zh-hans": {
            "command-line interface for English subtitle operations": (
                "英文字幕操作命令行界面"
            ),
            "modify English subtitles": "修改英文字幕",
        },
        "zh-hant": {
            "command-line interface for English subtitle operations": (
                "英文字幕操作命令列介面"
            ),
            "modify English subtitles": "修改英文字幕",
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
            dest="eng_subcommand",
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
            EngFuseCli.name(): EngFuseCli,
            EngProcessCli.name(): EngProcessCli,
            EngValidateOcrCli.name(): EngValidateOcrCli,
        }

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        subcommand_name = kwargs.pop("eng_subcommand")
        subcommand_cli_class = cls.subcommands()[subcommand_name]
        subcommand_cli_class._main(**kwargs)


if __name__ == "__main__":
    EngCli.main()
