#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for Written Cantonese review against Standard Chinese."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Unpack

from scinoephile.common import CLIKwargs
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
    str_arg,
)
from scinoephile.common.exception import ArgumentConflictError
from scinoephile.core.cli import ScinoephileCliBase, read_series, write_series
from scinoephile.multilang.yue_zho import (
    get_yue_block_reviewed_vs_zho,
    get_yue_line_reviewed_vs_zho,
)
from scinoephile.multilang.yue_zho.block_review import (
    YueHansBlockReviewPrompt,
    YueHantBlockReviewPrompt,
    get_yue_vs_zho_block_reviewer,
)
from scinoephile.multilang.yue_zho.line_review import (
    YueZhoHansLineReviewPrompt,
    YueZhoHantLineReviewPrompt,
    get_yue_vs_zho_line_reviewer,
)

__all__ = ["YueReviewVsZhoCli"]


class YueReviewVsZhoCli(ScinoephileCliBase):
    """Review Written Cantonese subtitles against Standard Chinese subtitles."""

    localizations = {
        "zh-hans": {
            (
                "command-line interface for Written Cantonese review against "
                "Standard Chinese"
            ): "书面粤语对照标准中文校对命令行界面",
            (
                "review mode (default: block): block=block-by-block review, "
                "line=line-by-line review"
            ): "校对模式（默认：block）：block=按区块校对，line=按行校对",
            "reviewed Written Cantonese subtitle outfile path (default: stdout)": (
                "校对后的书面粤语字幕输出文件路径（默认：标准输出）"
            ),
            "review Written Cantonese subtitles against Standard Chinese subtitles": (
                "校对书面粤语字幕与标准中文字幕"
            ),
            "script for prompts and output conversion (default: simplified)": (
                "提示词和输出转换使用的字形（默认：简体）"
            ),
            'target Written Cantonese subtitle infile path or "-" for stdin': (
                '目标书面粤语字幕输入文件路径，或使用 "-" 表示标准输入'
            ),
            'reference Standard Chinese subtitle infile path or "-" for stdin': (
                '参考标准中文字幕输入文件路径，或使用 "-" 表示标准输入'
            ),
        },
        "zh-hant": {
            (
                "command-line interface for Written Cantonese review against "
                "Standard Chinese"
            ): "書面粵語對照標準中文校對命令列介面",
            (
                "review mode (default: block): block=block-by-block review, "
                "line=line-by-line review"
            ): "校對模式（預設：block）：block=按區塊校對，line=按行校對",
            "reviewed Written Cantonese subtitle outfile path (default: stdout)": (
                "校對後的書面粵語字幕輸出檔路徑（預設：標準輸出）"
            ),
            "review Written Cantonese subtitles against Standard Chinese subtitles": (
                "校對書面粵語字幕與標準中文字幕"
            ),
            "script for prompts and output conversion (default: simplified)": (
                "提示詞與輸出轉換使用的字形（預設：簡體）"
            ),
            'target Written Cantonese subtitle infile path or "-" for stdin': (
                '目標書面粵語字幕輸入檔路徑，或使用 "-" 代表標準輸入'
            ),
            'reference Standard Chinese subtitle infile path or "-" for stdin': (
                '參考標準中文字幕輸入檔路徑，或使用 "-" 代表標準輸入'
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
            help='target Written Cantonese subtitle infile path or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--zho-infile",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='reference Standard Chinese subtitle infile path or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--mode",
            default="block",
            type=str_arg(options=("block", "line")),
            help=(
                "review mode (default: block): "
                "block=block-by-block review, line=line-by-line review"
            ),
        )
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
            help="reviewed Written Cantonese subtitle outfile path (default: stdout)",
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
        return "review"

    @classmethod
    def _get_line_review_prompt_cls(
        cls, script: str
    ) -> type[YueZhoHansLineReviewPrompt] | type[YueZhoHantLineReviewPrompt]:
        """Get the line-review prompt class for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            line-review prompt class
        """
        if script == "traditional":
            return YueZhoHantLineReviewPrompt
        return YueZhoHansLineReviewPrompt

    @classmethod
    def _get_block_review_prompt_cls(
        cls, script: str
    ) -> type[YueHansBlockReviewPrompt] | type[YueHantBlockReviewPrompt]:
        """Get the block review prompt class for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            block review prompt class
        """
        if script == "traditional":
            return YueHantBlockReviewPrompt
        return YueHansBlockReviewPrompt

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        # Validate arguments
        parser = kwargs.pop("_parser", cls.argparser())
        yue_infile_path = kwargs.pop("yue_infile")
        zho_infile_path = kwargs.pop("zho_infile")
        mode = kwargs.pop("mode")
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
        if mode == "line":
            prompt_cls = cls._get_line_review_prompt_cls(script)
            processor = get_yue_vs_zho_line_reviewer(prompt_cls=prompt_cls)
            reviewed = get_yue_line_reviewed_vs_zho(
                yuewen=yuewen,
                zhongwen=zhongwen,
                processor=processor,
            )
        else:
            prompt_cls = cls._get_block_review_prompt_cls(script)
            reviewer = get_yue_vs_zho_block_reviewer(prompt_cls=prompt_cls)
            reviewed = get_yue_block_reviewed_vs_zho(
                yuewen=yuewen,
                zhongwen=zhongwen,
                reviewer=reviewer,
            )

        # Write output
        write_series(
            parser,
            reviewed,
            outfile_path if outfile_path is not None else "-",
            overwrite,
        )


if __name__ == "__main__":
    YueReviewVsZhoCli.main()
