#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for written Cantonese subtitle operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common import CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .yue_transcribe_vs_zho_cli import YueTranscribeVsZhoCli

__all__ = ["YueCli"]

YUE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for written Cantonese subtitle operations": (
            "书面粤语字幕操作命令行界面"
        ),
        "run written Cantonese subtitle workflows": "运行书面粤语字幕工作流",
    },
    "zh-hant": {
        "command-line interface for written Cantonese subtitle operations": (
            "書面粵語字幕操作命令列介面"
        ),
        "run written Cantonese subtitle workflows": "執行書面粵語字幕工作流程",
    },
}
"""Localized help text keyed by locale and English source text."""


class YueCli(ScinoephileCliBase):
    """Run written Cantonese subtitle workflows."""

    localizations = YUE_LOCALIZATIONS
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
            dest="yue_subcommand_name",
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
        return {YueTranscribeVsZhoCli.name(): YueTranscribeVsZhoCli}

    @classmethod
    def _main(cls, *, yue_subcommand_name: str, **kwargs: Any):
        """Execute with provided keyword arguments."""
        cls.subcommands()[yue_subcommand_name]._main(**kwargs)


if __name__ == "__main__":
    YueCli.main()
