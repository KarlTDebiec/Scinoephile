#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for written Cantonese subtitle processing."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.conversion import (
    add_opencc_convert_argument,
    merge_conversion_localizations,
)
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
    str_arg,
)
from scinoephile.common.exception import ArgumentConflictError
from scinoephile.core.cli import ScinoephileCliBase, read_series, write_series
from scinoephile.lang.yue.romanization import get_yue_romanized
from scinoephile.lang.zho.block_review import (
    ZhoHansBlockReviewPrompt,
    ZhoHantBlockReviewPrompt,
    get_zho_block_reviewed,
    get_zho_reviewer,
)
from scinoephile.lang.zho.cleaning import get_zho_cleaned
from scinoephile.lang.zho.conversion import (
    SIMPLIFIED_CONFIGS,
    TRADITIONAL_CONFIGS,
    OpenCCConfig,
    get_zho_converted,
)
from scinoephile.lang.zho.flattening import get_zho_flattened

__all__ = ["YueProcessCli"]


class YueProcessCli(ScinoephileCliBase):
    """Modify written Cantonese subtitles."""

    localizations = merge_conversion_localizations(
        {
            "zh-hans": {
                "append Cantonese romanization to subtitles": "为字幕追加粤语罗马字",
                "command-line interface for written Cantonese subtitle processing": (
                    "书面粤语字幕处理命令行界面"
                ),
                "flatten multi-line subtitles into single lines": (
                    "将多行字幕合并为单行"
                ),
                "modify written Cantonese subtitles": "修改书面粤语字幕",
                "proofread subtitles using LLM (default: traditional)": (
                    "使用大语言模型校对字幕（默认：繁体）"
                ),
                "script for prompts and output conversion (default: traditional)": (
                    "提示词和输出转换使用的字形（默认：繁体）"
                ),
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
                "command-line interface for written Cantonese subtitle processing": (
                    "書面粵語字幕處理命令列介面"
                ),
                "flatten multi-line subtitles into single lines": (
                    "將多行字幕合併為單行"
                ),
                "modify written Cantonese subtitles": "修改書面粵語字幕",
                "proofread subtitles using LLM (default: traditional)": (
                    "使用大型語言模型校對字幕（預設：繁體）"
                ),
                "script for prompts and output conversion (default: traditional)": (
                    "提示詞與輸出轉換使用的字形（預設：繁體）"
                ),
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
            "--proofread",
            dest="review_script",
            nargs="?",
            const="traditional",
            type=str_arg(options=("simplified", "traditional")),
            help="proofread subtitles using LLM (default: traditional)",
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
            type=output_file_arg(),
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
        review_script: str | None,
        romanize: bool,
        offset: int,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()

        if not (clean or flatten or convert or review_script or romanize or offset):
            parser.error("At least one operation required")
        if overwrite and outfile_path is None:
            try:
                raise ArgumentConflictError(
                    "--overwrite may only be used with --outfile"
                )
            except ArgumentConflictError as exc:
                parser.error(str(exc))
        cls._validate_review_script(parser, convert, review_script)

        # Read input
        series = read_series(parser, infile_path, allow_stdin=True)

        # Perform operations
        if clean:
            series = get_zho_cleaned(series)
        if convert is not None:
            series = get_zho_converted(series, convert)
        if flatten:
            series = get_zho_flattened(series)
        if review_script is not None:
            prompt_cls = cls._get_review_prompt_cls(review_script)
            proofreader = get_zho_reviewer(prompt_cls=prompt_cls)
            series = get_zho_block_reviewed(series, processor=proofreader)
        if romanize:
            series = get_yue_romanized(series, append=True)
        if offset:
            series.shift(ms=offset)

        # Write output
        write_series(
            parser, series, outfile_path if outfile_path is not None else "-", overwrite
        )

    @classmethod
    def _get_review_prompt_cls(
        cls, review_script: str
    ) -> type[ZhoHansBlockReviewPrompt]:
        """Get the block-review prompt class for the selected script.

        Arguments:
            review_script: script identifier
        Returns:
            block-review prompt class
        """
        if review_script == "traditional":
            return ZhoHantBlockReviewPrompt
        return ZhoHansBlockReviewPrompt

    @classmethod
    def _get_script_for_conversion(cls, convert: OpenCCConfig) -> str | None:
        """Get the script implied by a conversion configuration.

        Arguments:
            convert: OpenCC configuration
        Returns:
            "simplified", "traditional", or None if not implied
        """
        if convert in SIMPLIFIED_CONFIGS:
            return "simplified"
        if convert in TRADITIONAL_CONFIGS:
            return "traditional"
        return None

    @classmethod
    def _validate_review_script(
        cls,
        parser: ArgumentParser,
        convert: OpenCCConfig | None,
        review_script: str | None,
    ):
        """Validate that review script matches conversion output.

        Arguments:
            parser: argument parser for error reporting
            convert: OpenCC configuration
            review_script: script identifier for block review
        """
        if review_script is None or convert is None:
            return
        convert_script = cls._get_script_for_conversion(convert)
        if convert_script is None:
            return
        if convert_script != review_script:
            parser.error(
                "Review script must match post-conversion script: "
                f"{convert} yields {convert_script}"
            )


if __name__ == "__main__":
    YueProcessCli.main()
