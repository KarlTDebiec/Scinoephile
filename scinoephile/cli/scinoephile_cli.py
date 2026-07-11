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

from .audit import AuditCli
from .dictionary import DictionaryCli
from .media import MediaCli
from .multi import MultiCli
from .ocr import OcrCli
from .process_cli import ProcessCli
from .proofread_cli import ProofreadCli
from .translate_cli import TranslateCli
from .utility import UtilityCli
from .yue import YueCli

__all__ = ["ScinoephileCli"]

SCINOEPHILE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "additional help": "附加帮助",
        "Available subcommands:": "可用子命令：",
        "audit subtitle review workflows": "审核字幕校对工作流",
        "build or search Chinese dictionaries": "构建或查询中文词典",
        "calculate the Character Error Rate (CER) of one series relative to "
        "another": "计算一个序列相对于另一个序列的字符错误率（CER）",
        "calculate the diff between two series": "计算两个序列之间的差异",
        "command-line interface for Scinoephile": "Scinoephile 命令行界面",
        "fuse OCR output for a selected language": "融合所选语言的 OCR 输出",
        "inspect and extract media streams": "检查并提取媒体流",
        "list all subcommands and exit": "列出所有子命令并退出",
        "operate on multiple subtitle series": "处理多个字幕序列",
        "process subtitles": "处理字幕",
        "proofread subtitles using an LLM": "使用大语言模型校对字幕",
        "recognize text from image-based subtitles": "识别图像字幕中的文本",
        "run written Cantonese subtitle workflows": "运行书面粤语字幕工作流",
        "run utility commands": "运行实用工具命令",
        (
            "Scinoephile is an application for working with Chinese, English, "
            "and bilingual subtitles."
        ): "Scinoephile 是一个用于处理中英及双语字幕的应用。",
        "shift and stretch the timings of one subtitle series to match another": (
            "平移并拉伸一个字幕序列的时间轴以匹配另一个序列"
        ),
        "stack two series into top and bottom subtitle lines": (
            "将两个序列堆叠为上下行字幕"
        ),
        "translate subtitles between supported languages": (
            "在受支持的语言之间翻译字幕"
        ),
        "validate OCR text against subtitle images": "对照字幕图像校验 OCR 文本",
    },
    "zh-hant": {
        "additional help": "附加說明",
        "Available subcommands:": "可用子命令：",
        "audit subtitle review workflows": "稽核字幕校對工作流程",
        "build or search Chinese dictionaries": "建置或查詢中文詞典",
        "calculate the Character Error Rate (CER) of one series relative to "
        "another": "計算一個序列相對於另一個序列的字元錯誤率（CER）",
        "calculate the diff between two series": "計算兩個序列之間的差異",
        "command-line interface for Scinoephile": "Scinoephile 命令列介面",
        "fuse OCR output for a selected language": "融合所選語言的 OCR 輸出",
        "inspect and extract media streams": "檢查並提取媒體流",
        "list all subcommands and exit": "列出所有子命令並結束",
        "operate on multiple subtitle series": "處理多個字幕序列",
        "process subtitles": "處理字幕",
        "proofread subtitles using an LLM": "使用大型語言模型校對字幕",
        "recognize text from image-based subtitles": "識別影像字幕中的文字",
        "run written Cantonese subtitle workflows": "執行書面粵語字幕工作流程",
        "run utility commands": "執行實用工具命令",
        (
            "Scinoephile is an application for working with Chinese, English, "
            "and bilingual subtitles."
        ): "Scinoephile 是用於處理中文、英文與雙語字幕的應用程式。",
        "shift and stretch the timings of one subtitle series to match another": (
            "平移並拉伸一個字幕序列的時間軸以匹配另一個序列"
        ),
        "stack two series into top and bottom subtitle lines": (
            "將兩個序列堆疊為上下行字幕"
        ),
        "translate subtitles between supported languages": ("在支援的語言之間翻譯字幕"),
        "validate OCR text against subtitle images": "對照字幕影像驗證 OCR 文字",
    },
}
"""Localized help text keyed by locale and English source text."""


class ScinoephileCli(ScinoephileCliBase):
    """Command-line interface for Scinoephile.

    Scinoephile is an application for working with Chinese, English, and bilingual
    subtitles.
    """

    localizations = SCINOEPHILE_LOCALIZATIONS
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        additional_help_arg_group = parser.add_argument_group("additional help")
        additional_help_arg_group.add_argument(
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
        get_arg_groups_by_name(
            parser,
            "additional help",
            optional_arguments_name="additional arguments",
        )

    @classmethod
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Names and types of tools wrapped by command-line interface.

        Returns:
            mapping of subcommand names to CLI classes
        """
        return {
            AuditCli.name(): AuditCli,
            DictionaryCli.name(): DictionaryCli,
            MediaCli.name(): MediaCli,
            MultiCli.name(): MultiCli,
            OcrCli.name(): OcrCli,
            ProcessCli.name(): ProcessCli,
            ProofreadCli.name(): ProofreadCli,
            TranslateCli.name(): TranslateCli,
            UtilityCli.name(): UtilityCli,
            YueCli.name(): YueCli,
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
