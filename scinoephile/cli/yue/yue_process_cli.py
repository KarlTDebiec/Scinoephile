#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for written Cantonese subtitle processing."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.helpers.conversion import (
    CONVERSION_LOCALIZATIONS,
    add_opencc_convert_argument,
)
from scinoephile.cli.helpers.io import read_series, write_series
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.lang.yue.romanization import get_yue_romanized
from scinoephile.lang.zho.cleaning import get_zho_cleaned
from scinoephile.lang.zho.flattening import get_zho_flattened
from scinoephile.lang.zho.script.conversion import (
    OpenCCConfig,
    get_zho_converted,
)

__all__ = ["YueProcessCli"]

YUE_PROCESS_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "append Cantonese romanization to subtitles": "为字幕追加粤语罗马字",
        "clean subtitles of closed-caption annotations and other anomalies": (
            "清理字幕中的隐藏字幕标注及其他异常"
        ),
        "command-line interface for written Cantonese subtitle processing": (
            "书面粤语字幕处理命令行界面"
        ),
        "flatten multi-line subtitles into single lines": ("将多行字幕合并为单行"),
        "modify written Cantonese subtitles": "修改书面粤语字幕",
        "shift subtitle timings by this many milliseconds": (
            "按指定毫秒数平移字幕时间"
        ),
        'Written Cantonese subtitle infile path or "-" for stdin': (
            '书面粤语字幕输入文件路径，或使用 "-" 表示标准输入'
        ),
        "Written Cantonese subtitle outfile path (default: stdout)": (
            "书面粤语字幕输出文件路径（默认：标准输出）"
        ),
    },
    "zh-hant": {
        "append Cantonese romanization to subtitles": "為字幕附加粵語羅馬字",
        "clean subtitles of closed-caption annotations and other anomalies": (
            "清理字幕中的隱藏字幕標註及其他異常"
        ),
        "command-line interface for written Cantonese subtitle processing": (
            "書面粵語字幕處理命令列介面"
        ),
        "flatten multi-line subtitles into single lines": ("將多行字幕合併為單行"),
        "modify written Cantonese subtitles": "修改書面粵語字幕",
        "shift subtitle timings by this many milliseconds": (
            "依指定毫秒數平移字幕時間"
        ),
        'Written Cantonese subtitle infile path or "-" for stdin': (
            '書面粵語字幕輸入檔路徑，或使用 "-" 代表標準輸入'
        ),
        "Written Cantonese subtitle outfile path (default: stdout)": (
            "書面粵語字幕輸出檔路徑（預設：標準輸出）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class YueProcessCli(ScinoephileCliBase):
    """Modify written Cantonese subtitles."""

    localizations = merge_localizations(
        CONVERSION_LOCALIZATIONS,
        YUE_PROCESS_LOCALIZATIONS,
    )
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
            "additional help",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "-i",
            "--infile",
            dest="infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='Written Cantonese subtitle infile path or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--clean",
            action="store_true",
            help="clean subtitles of closed-caption annotations and other anomalies",
        )
        add_opencc_convert_argument(
            arg_groups["operation arguments"], arg_groups["additional help"]
        )
        arg_groups["operation arguments"].add_argument(
            "--flatten",
            action="store_true",
            help="flatten multi-line subtitles into single lines",
        )
        arg_groups["operation arguments"].add_argument(
            "--romanize",
            action="store_true",
            help="append Cantonese romanization to subtitles",
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
            type=output_file_arg(exist_ok=True),
            help="Written Cantonese subtitle outfile path (default: stdout)",
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
        convert: OpenCCConfig | None,
        romanize: bool,
        offset: int,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()

        if not (clean or flatten or convert or romanize or offset):
            parser.error("At least one operation required")
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")

        # Read inputs
        series = read_series(parser, infile_path, allow_stdin=True)

        # Perform operations
        if clean:
            series = get_zho_cleaned(series)
        if convert is not None:
            series = get_zho_converted(series, convert)
        if flatten:
            series = get_zho_flattened(series)
        if romanize:
            series = get_yue_romanized(series, append=True)
        if offset:
            series.shift(ms=offset)

        # Write outputs
        write_series(
            parser, series, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    YueProcessCli.main()
