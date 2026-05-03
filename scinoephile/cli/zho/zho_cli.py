#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for standard Chinese subtitle operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import TypedDict, Unpack

from scinoephile.common import CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .zho_fuse_cli import ZhoFuseCli
from .zho_process_cli import ZhoProcessCli
from .zho_validate_ocr_cli import ZhoValidateOcrCli

__all__ = ["ZhoCli"]


class _ZhoCliKwargs(TypedDict, total=False):
    """Keyword arguments for ZhoCli."""

    zho_subcommand: str
    """Selected standard Chinese subtitle subcommand."""


class ZhoCli(ScinoephileCliBase):
    """Modify standard Chinese subtitles."""

    localizations = {
        "zh-hans": {
            "command-line interface for standard Chinese subtitle operations": (
                "标准中文字幕操作命令行界面"
            ),
            "modify standard Chinese subtitles": "修改标准中文字幕",
        },
        "zh-hant": {
            "command-line interface for standard Chinese subtitle operations": (
                "標準中文字幕操作命令列介面"
            ),
            "modify standard Chinese subtitles": "修改標準中文字幕",
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

        # Subcommands
        subparsers = parser.add_subparsers(
            dest="zho_subcommand",
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
            ZhoFuseCli.name(): ZhoFuseCli,
            ZhoProcessCli.name(): ZhoProcessCli,
            ZhoValidateOcrCli.name(): ZhoValidateOcrCli,
        }

    @classmethod
    def _main(cls, **kwargs: Unpack[_ZhoCliKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        subcommand_name = kwargs.pop("zho_subcommand")
        subcommand_cli_class = cls.subcommands()[subcommand_name]
        subcommand_cli_class._main(**kwargs)


if __name__ == "__main__":
    ZhoCli.main()
