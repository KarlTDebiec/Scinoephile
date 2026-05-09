#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for standard Chinese OCR subtitle validation."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.common import DirectoryNotFoundError
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    int_arg,
    output_dir_arg,
)
from scinoephile.common.exceptions import NotAFileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.zho.ocr_validation import validate_zho_ocr

__all__ = ["ZhoValidateOcrCli"]


class ZhoValidateOcrCli(ScinoephileCliBase):
    """Validate OCR text against subtitle images."""

    localizations = {
        "zh-hans": {
            "command-line interface for standard Chinese OCR subtitle validation": (
                "标准中文 OCR 字幕校验命令行界面"
            ),
            "directory in which to save validation image outputs": (
                "保存校验图像输出的目录"
            ),
            "overwrite outfile directory if it exists": "若输出目录已存在则覆盖",
            "prompt for interactive validation decisions": "提示进行交互式校验决策",
            "Standard Chinese OCR image subtitle infile path (directory containing "
            "index.html and png files, or a .sup file)": (
                "标准中文 OCR 图像字幕输入路径（包含 index.html 和 png 文件的目录，或 "
                ".sup 文件）"
            ),
            "stop validation after this subtitle index": "校验到此字幕索引后停止",
            "validate OCR text against subtitle images": "对照字幕图像校验 OCR 文本",
            "write validation data updates to repo data": (
                "将校验数据更新写入仓库数据"
            ),
        },
        "zh-hant": {
            "command-line interface for standard Chinese OCR subtitle validation": (
                "標準中文 OCR 字幕驗證命令列介面"
            ),
            "directory in which to save validation image outputs": (
                "儲存驗證影像輸出的目錄"
            ),
            "overwrite outfile directory if it exists": "若輸出目錄已存在則覆寫",
            "prompt for interactive validation decisions": "提示進行互動式驗證決策",
            "Standard Chinese OCR image subtitle infile path (directory containing "
            "index.html and png files, or a .sup file)": (
                "標準中文 OCR 影像字幕輸入路徑（包含 index.html 和 png 檔案的目錄，或 "
                ".sup 檔）"
            ),
            "stop validation after this subtitle index": "驗證到此字幕索引後停止",
            "validate OCR text against subtitle images": "對照字幕影像驗證 OCR 文字",
            "write validation data updates to repo data": (
                "將驗證資料更新寫入儲存庫資料"
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
            "-i",
            "--infile",
            dest="infile_path",
            required=True,
            type=Path,
            help=(
                "Standard Chinese OCR image subtitle infile path "
                "(directory containing index.html and png files, or a .sup file)"
            ),
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--stop-at-idx",
            type=int_arg(min_value=0),
            help="stop validation after this subtitle index",
        )
        arg_groups["operation arguments"].add_argument(
            "--interactive",
            action="store_true",
            help="prompt for interactive validation decisions",
        )
        arg_groups["operation arguments"].add_argument(
            "--dev",
            action="store_true",
            help="write validation data updates to repo data",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            required=True,
            type=output_dir_arg(create=False),
            help="directory in which to save validation image outputs",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile directory if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "validate-ocr"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        infile_path: Path,
        stop_at_idx: int | None,
        interactive: bool,
        dev: bool,
        outfile_path: Path,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if outfile_path.exists() and not overwrite:
            parser.error(f"{outfile_path} already exists")

        # Read input
        try:
            series = ImageSeries.load(infile_path)
        except (
            DirectoryNotFoundError,
            FileNotFoundError,
            NotADirectoryError,
            NotAFileError,
            ValueError,
        ) as exc:
            parser.error(str(exc))

        # Perform operations
        validated = validate_zho_ocr(
            series,
            stop_at_idx=stop_at_idx,
            interactive=interactive,
            dev=dev,
        )

        # Write output
        validated.save(outfile_path)


if __name__ == "__main__":
    ZhoValidateOcrCli.main()
