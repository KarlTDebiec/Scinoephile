#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for multi-series subtitle operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common import CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .multi_cer_cli import MultiCerCli
from .multi_diff_cli import MultiDiffCli
from .multi_stack_cli import MultiStackCli
from .multi_sync_cli import MultiSyncCli
from .multi_timewarp_cli import MultiTimewarpCli

__all__ = ["MultiCli"]

MULTI_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "A subtitle series is one timed subtitle timeline loaded from one file.": (
            "字幕序列是从一个文件载入的一条带时间轴的字幕时间线。"
        ),
        "operate on multiple subtitle series": "处理多个字幕序列",
    },
    "zh-hant": {
        "A subtitle series is one timed subtitle timeline loaded from one file.": (
            "字幕序列是從一個檔案載入的一條帶時間軸的字幕時間線。"
        ),
        "operate on multiple subtitle series": "處理多個字幕序列",
    },
}
"""Localized help text keyed by locale and English source text."""


class MultiCli(ScinoephileCliBase):
    """Operate on multiple subtitle series.

    A subtitle series is one timed subtitle timeline loaded from one file.
    """

    localizations = MULTI_LOCALIZATIONS
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="multi_subcommand_name",
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
            MultiCerCli.name(): MultiCerCli,
            MultiDiffCli.name(): MultiDiffCli,
            MultiStackCli.name(): MultiStackCli,
            MultiSyncCli.name(): MultiSyncCli,
            MultiTimewarpCli.name(): MultiTimewarpCli,
        }

    @classmethod
    def _main(
        cls,
        *,
        multi_subcommand_name: str,
        **kwargs: Any,
    ):
        """Execute with provided keyword arguments."""
        cls.subcommands()[multi_subcommand_name]._main(**kwargs)


if __name__ == "__main__":
    MultiCli.main()
