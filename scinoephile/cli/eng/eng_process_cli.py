#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for English subtitle processing."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from scinoephile.common.exceptions import ArgumentConflictError
from scinoephile.core.cli import ScinoephileCliBase, read_series, write_series
from scinoephile.lang.eng.block_review import get_eng_block_reviewed
from scinoephile.lang.eng.cleaning import get_eng_cleaned
from scinoephile.lang.eng.flattening import get_eng_flattened

__all__ = ["EngProcessCli"]


class EngProcessCli(ScinoephileCliBase):
    """Modify English subtitles."""

    localizations = {
        "zh-hans": {
            'English subtitle infile path or "-" for stdin': (
                '英文字幕输入文件路径，或使用 "-" 表示标准输入'
            ),
            "English subtitle outfile path (default: stdout)": (
                "英文字幕输出文件路径（默认：标准输出）"
            ),
            "flatten multi-line subtitles into single lines": "将多行字幕合并为单行",
            "modify English subtitles": "修改英文字幕",
            "shift subtitle timings by this many milliseconds": (
                "按指定毫秒数平移字幕时间"
            ),
            "proofread subtitles using LLM": "使用大语言模型校对字幕",
        },
        "zh-hant": {
            'English subtitle infile path or "-" for stdin': (
                '英文字幕輸入檔路徑，或使用 "-" 代表標準輸入'
            ),
            "English subtitle outfile path (default: stdout)": (
                "英文字幕輸出檔路徑（預設：標準輸出）"
            ),
            "flatten multi-line subtitles into single lines": "將多行字幕合併為單行",
            "modify English subtitles": "修改英文字幕",
            "shift subtitle timings by this many milliseconds": (
                "依指定毫秒數平移字幕時間"
            ),
            "proofread subtitles using LLM": "使用大型語言模型校對字幕",
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
            "-i",
            "--infile",
            dest="infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='English subtitle infile path or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--clean",
            action="store_true",
            help="clean subtitles of closed-caption annotations and other anomalies",
        )
        arg_groups["operation arguments"].add_argument(
            "--flatten",
            action="store_true",
            help="flatten multi-line subtitles into single lines",
        )
        arg_groups["operation arguments"].add_argument(
            "--proofread",
            action="store_true",
            help="proofread subtitles using LLM",
        )
        arg_groups["operation arguments"].add_argument(
            "--offset",
            default=0,
            type=int_arg(),
            help="shift subtitle timings by this many milliseconds",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            default=None,
            dest="outfile_path",
            type=output_file_arg(),
            help="English subtitle outfile path (default: stdout)",
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
        return "process"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        infile_path: Path | str,
        outfile_path: Path | None,
        clean: bool,
        flatten: bool,
        proofread: bool,
        offset: int,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()

        if not (clean or flatten or proofread or offset):
            parser.error("At least one operation required")
        if overwrite and outfile_path is None:
            try:
                raise ArgumentConflictError(
                    "--overwrite may only be used with --outfile"
                )
            except ArgumentConflictError as exc:
                parser.error(str(exc))

        # Read input
        series = read_series(parser, infile_path, allow_stdin=True)

        # Perform operations
        if clean:
            series = get_eng_cleaned(series)
        if flatten:
            series = get_eng_flattened(series)
        if proofread:
            series = get_eng_block_reviewed(series)
        if offset:
            series.shift(ms=offset)

        # Write output
        write_series(
            parser, series, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    EngProcessCli.main()
