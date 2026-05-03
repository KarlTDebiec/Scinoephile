#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for written Cantonese translation.

This command uses standard Chinese reference subtitles.
"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import TypedDict, Unpack

from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
    str_arg,
)
from scinoephile.common.exception import ArgumentConflictError
from scinoephile.core.cli import ScinoephileCliBase, read_series, write_series
from scinoephile.multilang.yue_zho.translation import (
    YueVsZhoYueHansTranslationPrompt,
    YueVsZhoYueHantTranslationPrompt,
    get_yue_translated_vs_zho,
    get_yue_vs_zho_translator,
)

__all__ = ["YueTranslateVsZhoCli"]


class _YueTranslateVsZhoCliKwargs(TypedDict, total=False):
    """Keyword arguments for YueTranslateVsZhoCli."""

    _parser: ArgumentParser
    """Argument parser."""
    yue_infile: Path | str
    """Target written Cantonese subtitle infile or stdin sentinel."""
    zho_infile: Path | str
    """Reference standard Chinese subtitle infile or stdin sentinel."""
    script: str
    """Selected prompt script."""
    outfile: Path | None
    """Translated written Cantonese subtitle outfile path."""
    overwrite: bool
    """Whether to overwrite an existing outfile."""


class YueTranslateVsZhoCli(ScinoephileCliBase):
    """Translate missing subtitles using a standard Chinese reference series."""

    localizations = {
        "zh-hans": {
            "command-line interface for written Cantonese translation": (
                "书面粤语翻译命令行界面"
            ),
            "This command uses standard Chinese reference subtitles.": (
                "此命令使用标准中文字幕作为参考。"
            ),
            'reference standard Chinese subtitle infile or "-" for stdin': (
                '参考标准中文字幕输入文件，或使用 "-" 表示标准输入'
            ),
            "script for prompts and output conversion (default: simplified)": (
                "提示词和输出转换使用的字形（默认：简体）"
            ),
            'target written Cantonese subtitle infile or "-" for stdin': (
                '目标书面粤语字幕输入文件，或使用 "-" 表示标准输入'
            ),
            "translated written Cantonese subtitle outfile path (default: stdout)": (
                "翻译后的书面粤语字幕输出文件路径（默认：标准输出）"
            ),
            "translate missing subtitles using a standard Chinese reference series": (
                "使用标准中文字幕参考补全缺失字幕"
            ),
        },
        "zh-hant": {
            "command-line interface for written Cantonese translation": (
                "書面粵語翻譯命令列介面"
            ),
            "This command uses standard Chinese reference subtitles.": (
                "此命令使用標準中文字幕作為參考。"
            ),
            'reference standard Chinese subtitle infile or "-" for stdin': (
                '參考標準中文字幕輸入檔，或使用 "-" 代表標準輸入'
            ),
            "script for prompts and output conversion (default: simplified)": (
                "提示詞與輸出轉換使用的字形（預設：簡體）"
            ),
            'target written Cantonese subtitle infile or "-" for stdin': (
                '目標書面粵語字幕輸入檔，或使用 "-" 代表標準輸入'
            ),
            "translated written Cantonese subtitle outfile path (default: stdout)": (
                "翻譯後的書面粵語字幕輸出檔路徑（預設：標準輸出）"
            ),
            "translate missing subtitles using a standard Chinese reference series": (
                "使用標準中文字幕參考補全缺失字幕"
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
            "input arguments",
            "operation arguments",
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--yue-infile",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='target written Cantonese subtitle infile or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--zho-infile",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='reference standard Chinese subtitle infile or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--script",
            default="simplified",
            type=str_arg(options=("simplified", "traditional")),
            help="script for prompts and output conversion (default: simplified)",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            default=None,
            type=output_file_arg(),
            help="translated written Cantonese subtitle outfile path (default: stdout)",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "translate-vs-zho"

    @classmethod
    def _get_translation_prompt_cls(
        cls, script: str
    ) -> type[YueVsZhoYueHansTranslationPrompt]:
        """Get the translation prompt class for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            translation prompt class
        """
        if script == "traditional":
            return YueVsZhoYueHantTranslationPrompt
        return YueVsZhoYueHansTranslationPrompt

    @classmethod
    def _main(cls, **kwargs: Unpack[_YueTranslateVsZhoCliKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        # Validate arguments
        parser = kwargs.pop("_parser", cls.argparser())
        yue_infile_path = kwargs.pop("yue_infile")
        zho_infile_path = kwargs.pop("zho_infile")
        script = kwargs.pop("script")
        outfile_path: Path | None = kwargs.pop("outfile")
        overwrite = kwargs.pop("overwrite")
        if yue_infile_path == "-" and zho_infile_path == "-":
            try:
                raise ArgumentConflictError(
                    "--yue-infile and --zho-infile may not both be '-'"
                )
            except ArgumentConflictError as exc:
                parser.error(str(exc))
        if overwrite and outfile_path is None:
            try:
                raise ArgumentConflictError(
                    "--overwrite may only be used with --outfile"
                )
            except ArgumentConflictError as exc:
                parser.error(str(exc))

        # Read inputs
        yuewen = read_series(parser, yue_infile_path, allow_stdin=True)
        zhongwen = read_series(parser, zho_infile_path, allow_stdin=True)

        # Perform operations
        prompt_cls = cls._get_translation_prompt_cls(script)
        translator = get_yue_vs_zho_translator(prompt_cls=prompt_cls)
        yuewen = get_yue_translated_vs_zho(
            yuewen=yuewen,
            zhongwen=zhongwen,
            translator=translator,
        )

        # Write outputs
        write_series(
            parser, yuewen, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    YueTranslateVsZhoCli.main()
