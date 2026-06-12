#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for multi-series subtitle diffs."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.analysis.diff import SeriesDiff
from scinoephile.cli.helpers.io import read_series
from scinoephile.common.argument_parsing import (
    float_arg,
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core.cli import ScinoephileCliBase

__all__ = ["MultiDiffCli"]

MULTI_DIFF_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "calculate the diff between two series": "计算两个序列之间的差异",
        "command-line interface for multi-series subtitle diffs": (
            "多序列字幕差异命令行界面"
        ),
        "series label for candidate output in diff messages (default: candidate)": (
            "差异消息中候选输出的序列标签（默认：candidate）"
        ),
        "series label for reference input in diff messages (default: reference)": (
            "差异消息中参考输入的序列标签（默认：reference）"
        ),
        "similarity threshold used to pair replacements (default: 0.6)": (
            "用于配对替换项的相似度阈值（默认：0.6）"
        ),
        'candidate subtitle infile to compare against the reference, or "-" '
        "for stdin": ('要与参考输入比较的候选字幕输入文件，或用 "-" 表示标准输入'),
        'reference subtitle infile or "-" for stdin': (
            '参考字幕输入文件，或用 "-" 表示标准输入'
        ),
    },
    "zh-hant": {
        "calculate the diff between two series": "計算兩個序列之間的差異",
        "command-line interface for multi-series subtitle diffs": (
            "多序列字幕差異命令列介面"
        ),
        "series label for candidate output in diff messages (default: candidate)": (
            "差異訊息中候選輸出的序列標籤（預設：candidate）"
        ),
        "series label for reference input in diff messages (default: reference)": (
            "差異訊息中參考輸入的序列標籤（預設：reference）"
        ),
        "similarity threshold used to pair replacements (default: 0.6)": (
            "用於配對替換項的相似度閾值（預設：0.6）"
        ),
        'candidate subtitle infile to compare against the reference, or "-" '
        "for stdin": ('要與參考輸入比較的候選字幕輸入檔，或用 "-" 表示標準輸入'),
        'reference subtitle infile or "-" for stdin': (
            '參考字幕輸入檔，或用 "-" 表示標準輸入'
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class MultiDiffCli(ScinoephileCliBase):
    """Calculate the diff between two series."""

    localizations = MULTI_DIFF_LOCALIZATIONS
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
            "--reference-infile",
            dest="reference_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='reference subtitle infile or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--candidate-infile",
            dest="candidate_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help=(
                'candidate subtitle infile to compare against the reference, or "-" '
                "for stdin"
            ),
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
            "--reference-label",
            default="reference",
            type=str,
            help=(
                "series label for reference input in diff messages (default: reference)"
            ),
        )
        arg_groups["output arguments"].add_argument(
            "--candidate-label",
            default="candidate",
            type=str,
            help=(
                "series label for candidate output in diff messages "
                "(default: candidate)"
            ),
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "diff"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        reference_infile_path: Path | str,
        candidate_infile_path: Path | str,
        similarity_cutoff: float,
        reference_label: str,
        candidate_label: str,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if reference_infile_path == "-" and candidate_infile_path == "-":
            parser.error(
                "--reference-infile and --candidate-infile may not both be '-'"
            )

        # Read inputs
        reference_subtitle_series = read_series(
            parser, reference_infile_path, allow_stdin=True
        )
        candidate_subtitle_series = read_series(
            parser, candidate_infile_path, allow_stdin=True
        )

        # Perform operations
        diff = SeriesDiff(
            reference_subtitle_series,
            candidate_subtitle_series,
            one_lbl=reference_label,
            two_lbl=candidate_label,
            similarity_cutoff=similarity_cutoff,
        )

        # Write outputs
        line_diffs = list(diff)
        if not line_diffs:
            print("No differences found.")
            return
        for line_diff in line_diffs:
            print(line_diff)


if __name__ == "__main__":
    MultiDiffCli.main()
