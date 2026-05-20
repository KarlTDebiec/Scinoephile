#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for English subtitle operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common import CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .eng_process_cli import EngProcessCli
from .eng_translate_vs_yue_cli import EngTranslateVsYueCli
from .eng_translate_vs_zho_cli import EngTranslateVsZhoCli

__all__ = ["EngCli"]

ENG_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for English subtitle operations": (
            "英文字幕操作命令行界面"
        ),
        "modify English subtitles": "修改英文字幕",
        "translate English subtitles from written Cantonese subtitles": (
            "根据书面粤语字幕翻译英文字幕"
        ),
        "translate English subtitles from Chinese subtitles": (
            "根据中文字幕翻译英文字幕"
        ),
    },
    "zh-hant": {
        "command-line interface for English subtitle operations": (
            "英文字幕操作命令列介面"
        ),
        "modify English subtitles": "修改英文字幕",
        "translate English subtitles from written Cantonese subtitles": (
            "根據書面粵語字幕翻譯英文字幕"
        ),
        "translate English subtitles from Chinese subtitles": (
            "根據中文字幕翻譯英文字幕"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class EngCli(ScinoephileCliBase):
    """Modify English subtitles."""

    localizations = ENG_LOCALIZATIONS
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="eng_subcommand_name",
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
            EngProcessCli.name(): EngProcessCli,
            EngTranslateVsYueCli.name(): EngTranslateVsYueCli,
            EngTranslateVsZhoCli.name(): EngTranslateVsZhoCli,
        }

    @classmethod
    def _main(
        cls,
        *,
        eng_subcommand_name: str,
        **kwargs: Any,
    ):
        """Execute with provided keyword arguments."""
        cls.subcommands()[eng_subcommand_name]._main(**kwargs)


if __name__ == "__main__":
    EngCli.main()
