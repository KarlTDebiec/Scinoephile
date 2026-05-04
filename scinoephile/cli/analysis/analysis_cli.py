#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for analysis operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common import CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .analysis_cer_cli import AnalysisCerCli
from .analysis_diff_cli import AnalysisDiffCli

__all__ = ["AnalysisCli"]


class AnalysisCli(ScinoephileCliBase):
    """Analyze subtitles."""

    localizations = {
        "zh-hans": {"analyze subtitles": "分析字幕"},
        "zh-hant": {"analyze subtitles": "分析字幕"},
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
            dest="analysis_subcommand_name",
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
            AnalysisCerCli.name(): AnalysisCerCli,
            AnalysisDiffCli.name(): AnalysisDiffCli,
        }

    @classmethod
    def _main(
        cls,
        *,
        analysis_subcommand_name: str,
        **kwargs: Any,
    ):
        """Execute with provided keyword arguments."""
        cls.subcommands()[analysis_subcommand_name]._main(**kwargs)


if __name__ == "__main__":
    AnalysisCli.main()
