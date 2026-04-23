#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for written Cantonese subtitle operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .yue_process_cli import YueProcessCli
from .yue_review_vs_zho_cli import YueReviewVsZhoCli
from .yue_transcribe_vs_zho_cli import YueTranscribeVsZhoCli
from .yue_translate_vs_zho_cli import YueTranslateVsZhoCli

__all__ = ["YueCli"]


class YueCli(ScinoephileCliBase):
    """Modify written Cantonese subtitles."""

    localizations = {
        "zh-hans": {
            "command-line interface for written Cantonese subtitle operations": (
                "书面粤语字幕操作命令行界面"
            ),
            "modify written Cantonese subtitles": "修改书面粤语字幕",
        },
        "zh-hant": {
            "command-line interface for written Cantonese subtitle operations": (
                "書面粵語字幕操作命令列介面"
            ),
            "modify written Cantonese subtitles": "修改書面粵語字幕",
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
            YueReviewVsZhoCli.name(): YueReviewVsZhoCli,
            YueTranscribeVsZhoCli.name(): YueTranscribeVsZhoCli,
            YueTranslateVsZhoCli.name(): YueTranslateVsZhoCli,
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
