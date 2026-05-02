#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for subtitle diff analysis."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import ClassVar, Unpack

from scinoephile.analysis.diff import SeriesDiff
from scinoephile.common import CLIKwargs
from scinoephile.common.argument_parsing import (
    float_arg,
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.common.exception import ArgumentConflictError
from scinoephile.core.cli import ScinoephileCliBase, read_series

__all__ = ["AnalysisDiffCli"]


class AnalysisDiffCli(ScinoephileCliBase):
    """Calculate the diff between two series."""

    localizations: ClassVar[dict[str, dict[str, str]]] = {
        "zh-hans": {
            "calculate the diff between two series": "计算两个序列之间的差异",
            "command-line interface for subtitle diff analysis": (
                "字幕差异分析命令行界面"
            ),
            "label for first series (default: one)": "第一个序列标签（默认：one）",
            "label for second series (default: two)": "第二个序列标签（默认：two）",
            "similarity threshold used to pair replacements (default: 0.6)": (
                "用于配对替换项的相似度阈值（默认：0.6）"
            ),
            'subtitle infile for first series or "-" for stdin': (
                '第一个序列的字幕输入文件，或用 "-" 表示标准输入'
            ),
            'subtitle infile for second series or "-" for stdin': (
                '第二个序列的字幕输入文件，或用 "-" 表示标准输入'
            ),
        },
        "zh-hant": {
            "calculate the diff between two series": "計算兩個序列之間的差異",
            "command-line interface for subtitle diff analysis": (
                "字幕差異分析命令列介面"
            ),
            "label for first series (default: one)": "第一個序列標籤（預設：one）",
            "label for second series (default: two)": "第二個序列標籤（預設：two）",
            "similarity threshold used to pair replacements (default: 0.6)": (
                "用於配對替換項的相似度閾值（預設：0.6）"
            ),
            'subtitle infile for first series or "-" for stdin': (
                '第一個序列的字幕輸入檔，或用 "-" 表示標準輸入'
            ),
            'subtitle infile for second series or "-" for stdin': (
                '第二個序列的字幕輸入檔，或用 "-" 表示標準輸入'
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
            "--one-infile",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='subtitle infile for first series or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--two-infile",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='subtitle infile for second series or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--similarity-cutoff",
            default=0.6,
            type=float_arg(min_value=0.0, max_value=1.0),
            help="similarity threshold used to pair replacements (default: 0.6)",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "--one-label",
            default="one",
            type=str,
            help="label for first series (default: one)",
        )
        arg_groups["output arguments"].add_argument(
            "--two-label",
            default="two",
            type=str,
            help="label for second series (default: two)",
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "diff"

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        # Validate arguments
        parser = kwargs.pop("_parser", cls.argparser())
        one_infile_path = kwargs.pop("one_infile")
        two_infile_path = kwargs.pop("two_infile")
        similarity_cutoff = kwargs.pop("similarity_cutoff")
        one_label = kwargs.pop("one_label")
        two_label = kwargs.pop("two_label")
        if one_infile_path == "-" and two_infile_path == "-":
            try:
                raise ArgumentConflictError(
                    "--one-infile and --two-infile may not both be '-'"
                )
            except ArgumentConflictError as exc:
                parser.error(str(exc))

        # Read inputs
        one_subtitle_series = read_series(parser, one_infile_path, allow_stdin=True)
        two_subtitle_series = read_series(parser, two_infile_path, allow_stdin=True)

        # Perform operations
        diff = SeriesDiff(
            one_subtitle_series,
            two_subtitle_series,
            one_lbl=one_label,
            two_lbl=two_label,
            similarity_cutoff=similarity_cutoff,
        )

        # Write outputs
        for line_diff in diff:
            print(line_diff)


if __name__ == "__main__":
    AnalysisDiffCli.main()
