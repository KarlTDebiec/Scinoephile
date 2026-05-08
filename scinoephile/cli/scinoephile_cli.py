#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for Scinoephile."""

from __future__ import annotations

from argparse import SUPPRESS, ArgumentParser
from typing import Any

from scinoephile.common import CommandLineInterface
from scinoephile.common.argument_parsing import get_arg_groups_by_name
from scinoephile.common.cli import ListAllCommandsAction
from scinoephile.core.cli import ScinoephileCliBase

from .analysis import AnalysisCli
from .cache import CacheCli
from .dictionary import DictionaryCli
from .eng import EngCli
from .media import MediaCli
from .ocr import OcrCli
from .optimization import OptimizationCli
from .sync_cli import SyncCli
from .timewarp_cli import TimewarpCli
from .yue import YueCli
from .zho import ZhoCli

__all__ = ["ScinoephileCli"]


class ScinoephileCli(ScinoephileCliBase):
    """Command-line interface for Scinoephile.

    Scinoephile is an application for working with Chinese, English, and bilingual
    subtitles.
    """

    localizations = {
        "zh-hans": {
            "additional help": "附加帮助",
            "analyze subtitles": "分析字幕",
            "Available subcommands:": "可用子命令：",
            "build or search Chinese dictionaries": "构建或查询中文词典",
            "command-line interface for Scinoephile": "Scinoephile 命令行界面",
            "combine two series into the top and bottom of a synchronized series": (
                "将两个序列合并为上下行同步字幕"
            ),
            "inspect and invalidate local caches": "检查并清除本地缓存",
            "inspect and extract media streams": "检查并提取媒体流",
            "list all subcommands and exit": "列出所有子命令并退出",
            "modify English subtitles": "修改英文字幕",
            "modify standard Chinese subtitles": "修改标准中文字幕",
            "modify written Cantonese subtitles": "修改书面粤语字幕",
            "prompt optimization utilities and persistence": "提示词优化工具与持久化",
            (
                "Scinoephile is an application for working with Chinese, English, "
                "and bilingual subtitles."
            ): "Scinoephile 是一个用于处理中英及双语字幕的应用。",
            "shift and stretch the timings of one subtitle series to match another": (
                "平移并拉伸一个字幕序列的时间轴以匹配另一个序列"
            ),
        },
        "zh-hant": {
            "additional help": "附加說明",
            "analyze subtitles": "分析字幕",
            "Available subcommands:": "可用子命令：",
            "build or search Chinese dictionaries": "建置或查詢中文詞典",
            "command-line interface for Scinoephile": "Scinoephile 命令列介面",
            "combine two series into the top and bottom of a synchronized series": (
                "將兩個序列合併為上下行同步字幕"
            ),
            "inspect and invalidate local caches": "檢查並清除本機快取",
            "inspect and extract media streams": "檢查並提取媒體流",
            "list all subcommands and exit": "列出所有子命令並結束",
            "modify English subtitles": "修改英文字幕",
            "modify standard Chinese subtitles": "修改標準中文字幕",
            "modify written Cantonese subtitles": "修改書面粵語字幕",
            "prompt optimization utilities and persistence": "提示詞最佳化工具與持久化",
            (
                "Scinoephile is an application for working with Chinese, English, "
                "and bilingual subtitles."
            ): "Scinoephile 是用於處理中文、英文與雙語字幕的應用程式。",
            "shift and stretch the timings of one subtitle series to match another": (
                "平移並拉伸一個字幕序列的時間軸以匹配另一個序列"
            ),
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

        arg_groups = get_arg_groups_by_name(
            parser,
            "additional help",
            optional_arguments_name="additional arguments",
        )
        arg_groups["additional help"].add_argument(
            "--all-commands",
            action=ListAllCommandsAction,
            default=SUPPRESS,
            help="list all subcommands and exit",
            root_cli_class=cls,
        )

        subparsers = parser.add_subparsers(
            dest="subcommand_name",
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
            AnalysisCli.name(): AnalysisCli,
            CacheCli.name(): CacheCli,
            DictionaryCli.name(): DictionaryCli,
            EngCli.name(): EngCli,
            MediaCli.name(): MediaCli,
            OcrCli.name(): OcrCli,
            OptimizationCli.name(): OptimizationCli,
            SyncCli.name(): SyncCli,
            TimewarpCli.name(): TimewarpCli,
            YueCli.name(): YueCli,
            ZhoCli.name(): ZhoCli,
        }

    @classmethod
    def _main(
        cls,
        *,
        subcommand_name: str,
        **kwargs: Any,
    ):
        """Execute with provided keyword arguments."""
        cls.subcommands()[subcommand_name]._main(**kwargs)


if __name__ == "__main__":
    ScinoephileCli.main()
