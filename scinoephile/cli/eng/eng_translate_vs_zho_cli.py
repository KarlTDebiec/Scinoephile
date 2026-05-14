#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for English guided translation from Chinese.

This command translates standard Chinese subtitles into English using aligned
English subtitles as guidance.
"""

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
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase, read_series, write_series
from scinoephile.multilang.eng_zho.guided_translation import (
    get_eng_translated_from_zho_with_eng_guidance,
    get_eng_zho_guided_translator,
)

__all__ = ["EngTranslateVsZhoCli"]


class EngTranslateVsZhoCli(ScinoephileCliBase):
    """Translate English subtitles using Chinese subtitles and English reference."""

    localizations = {
        "zh-hans": {
            'aligned English subtitle infile to use as guidance, or "-" for stdin': (
                '用作参考的已对齐英文字幕输入文件，或使用 "-" 表示标准输入'
            ),
            'aligned standard Chinese subtitle infile or "-" for stdin': (
                '已对齐的标准中文字幕输入文件，或使用 "-" 表示标准输入'
            ),
            "command-line interface for English guided translation from Chinese": (
                "由中文引导的英文翻译命令行界面"
            ),
            "English guided translation outfile path (default: stdout)": (
                "英文引导翻译输出文件路径（默认：标准输出）"
            ),
            "stop translation after this subtitle index": ("翻译到此字幕索引后停止"),
            "This command translates standard Chinese subtitles into English using "
            "aligned English subtitles as guidance.": (
                "此命令使用已对齐的英文字幕作为参考，将标准中文字幕翻译为英文。"
            ),
            "translate English subtitles using Chinese subtitles and English "
            "reference": ("使用中文字幕和英文参考翻译英文字幕"),
        },
        "zh-hant": {
            'aligned English subtitle infile to use as guidance, or "-" for stdin': (
                '用作參考的已對齊英文字幕輸入檔，或使用 "-" 代表標準輸入'
            ),
            'aligned standard Chinese subtitle infile or "-" for stdin': (
                '已對齊的標準中文字幕輸入檔，或使用 "-" 代表標準輸入'
            ),
            "command-line interface for English guided translation from Chinese": (
                "由中文引導的英文翻譯命令列介面"
            ),
            "English guided translation outfile path (default: stdout)": (
                "英文引導翻譯輸出檔路徑（預設：標準輸出）"
            ),
            "stop translation after this subtitle index": ("翻譯到此字幕索引後停止"),
            "This command translates standard Chinese subtitles into English using "
            "aligned English subtitles as guidance.": (
                "此命令使用已對齊的英文字幕作為參考，將標準中文字幕翻譯為英文。"
            ),
            "translate English subtitles using Chinese subtitles and English "
            "reference": ("使用中文字幕與英文參考翻譯英文字幕"),
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
            "--eng-infile",
            dest="eng_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='aligned English subtitle infile to use as guidance, or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--zho-infile",
            dest="zho_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='aligned standard Chinese subtitle infile or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--stop-at-idx",
            type=int_arg(min_value=0),
            help="stop translation after this subtitle index",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            default=None,
            dest="outfile_path",
            type=output_file_arg(),
            help="English guided translation outfile path (default: stdout)",
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
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        eng_infile_path: Path | str,
        zho_infile_path: Path | str,
        stop_at_idx: int | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if eng_infile_path == "-" and zho_infile_path == "-":
            try:
                raise ArgumentConflictError(
                    "--eng-infile and --zho-infile may not both be '-'"
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
        try:
            eng = read_series(parser, eng_infile_path, allow_stdin=True)
            zho = read_series(parser, zho_infile_path, allow_stdin=True)
        except (
            FileNotFoundError,
            NotADirectoryError,
            ScinoephileError,
            ValueError,
        ) as exc:
            parser.error(str(exc))

        # Perform operations
        translator = get_eng_zho_guided_translator()
        eng_translated = get_eng_translated_from_zho_with_eng_guidance(
            zho=zho,
            eng=eng,
            translator=translator,
            stop_at_idx=stop_at_idx,
        )

        # Write outputs
        write_series(
            parser,
            eng_translated,
            outfile_path if outfile_path is not None else "-",
            overwrite,
        )


if __name__ == "__main__":
    EngTranslateVsZhoCli.main()
