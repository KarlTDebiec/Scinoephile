#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for subtitle processing.

Process subtitles.
"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.common.argument_parsing import (
    enum_arg,
    enum_metavar,
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.lang.zho.script.conversion import (
    OpenCCConfig,
    get_zho_converted,
)
from scinoephile.workflows.clean import clean_series
from scinoephile.workflows.flatten import flatten_series
from scinoephile.workflows.helpers import resolve_language
from scinoephile.workflows.romanize import romanize_series

from .helpers.conversion import (
    CONVERSION_LOCALIZATIONS,
    add_opencc_convert_auto_argument,
)
from .helpers.io import read_series, write_series

__all__ = ["ProcessCli"]


PROCESS_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "append language-specific romanization to Chinese subtitles": (
            "为中文字幕追加对应语言的罗马字"
        ),
        "clean subtitles of closed-caption annotations and other anomalies": (
            "清理字幕中的隐藏字幕标注及其他异常"
        ),
        "command-line interface for subtitle processing": "字幕处理命令行界面",
        "flatten multi-line subtitles into single lines": "将多行字幕合并为单行",
        "process subtitles": "处理字幕",
        "Process subtitles.": "处理字幕。",
        "shift subtitle timings by this many milliseconds": (
            "按指定毫秒数平移字幕时间"
        ),
        'subtitle infile path or "-" for stdin': (
            '字幕输入文件路径，或使用 "-" 表示标准输入'
        ),
        "subtitle language tag (detected from infile if omitted)": (
            "字幕语言标签（省略时从输入文件检测）"
        ),
        "subtitle outfile path (default: stdout)": (
            "字幕输出文件路径（默认：标准输出）"
        ),
    },
    "zh-hant": {
        "append language-specific romanization to Chinese subtitles": (
            "為中文字幕附加對應語言的羅馬字"
        ),
        "clean subtitles of closed-caption annotations and other anomalies": (
            "清理字幕中的隱藏字幕標註及其他異常"
        ),
        "command-line interface for subtitle processing": "字幕處理命令列介面",
        "flatten multi-line subtitles into single lines": "將多行字幕合併為單行",
        "process subtitles": "處理字幕",
        "Process subtitles.": "處理字幕。",
        "shift subtitle timings by this many milliseconds": (
            "依指定毫秒數平移字幕時間"
        ),
        'subtitle infile path or "-" for stdin': (
            '字幕輸入檔路徑，或使用 "-" 代表標準輸入'
        ),
        "subtitle language tag (detected from infile if omitted)": (
            "字幕語言標籤（省略時從輸入檔偵測）"
        ),
        "subtitle outfile path (default: stdout)": "字幕輸出檔路徑（預設：標準輸出）",
    },
}
"""Localized help text keyed by locale and English source text."""


class ProcessCli(ScinoephileCliBase):
    """Process subtitles."""

    localizations = merge_localizations(
        CONVERSION_LOCALIZATIONS,
        PROCESS_LOCALIZATIONS,
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
            help='subtitle infile path or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--language",
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help="subtitle language tag (detected from infile if omitted)",
        )
        arg_groups["operation arguments"].add_argument(
            "--clean",
            action="store_true",
            help="clean subtitles of closed-caption annotations and other anomalies",
        )
        add_opencc_convert_auto_argument(
            arg_groups["operation arguments"],
            arg_groups["additional help"],
        )
        arg_groups["operation arguments"].add_argument(
            "--flatten",
            action="store_true",
            help="flatten multi-line subtitles into single lines",
        )
        arg_groups["operation arguments"].add_argument(
            "--romanize",
            action="store_true",
            help="append language-specific romanization to Chinese subtitles",
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
            dest="outfile_path",
            type=output_file_arg(exist_ok=True),
            help="subtitle outfile path (default: stdout)",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def _main(  # noqa: PLR0912
        cls,
        *,
        _parser: ArgumentParser | None = None,
        infile_path: Path | str,
        outfile_path: Path | None,
        language: Language | None,
        clean: bool,
        flatten: bool,
        convert: OpenCCConfig | bool | None,
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

        # Read input and resolve language
        series = read_series(parser, infile_path, allow_stdin=True)
        try:
            resolved_language = resolve_language(series, language)
        except ScinoephileError as exc:
            parser.error(str(exc))
        if resolved_language is Language.eng and convert is not None:
            parser.error("--convert may only be used with Chinese subtitles")
        resolved_convert: OpenCCConfig | None = None
        if isinstance(convert, OpenCCConfig):
            resolved_convert = convert
        elif convert:
            if resolved_language.script == "Hans":
                resolved_convert = OpenCCConfig.s2t
            else:
                resolved_convert = OpenCCConfig.t2s
        if resolved_language is Language.eng and romanize:
            parser.error("--romanize may only be used with Chinese subtitles")

        # Perform operations
        if clean:
            series = clean_series(series, language=resolved_language)
        if resolved_convert is not None:
            series = get_zho_converted(series, resolved_convert)
        if flatten:
            series = flatten_series(series, language=resolved_language)
        if romanize:
            series = romanize_series(
                series,
                language=resolved_language,
                append=True,
            )
        if offset:
            series.shift(ms=offset)

        # Write output
        write_series(
            parser, series, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    ProcessCli.main()
