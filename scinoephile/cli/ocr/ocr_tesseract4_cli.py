#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for Tesseract 4 OCR."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_or_dir_arg,
    output_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.image.subtitles import ImageSeries

__all__ = ["OcrTesseract4Cli"]

ocr_image_series_with_tesseract4: Any | None = None


class OcrTesseract4Cli(ScinoephileCliBase):
    """Recognize image subtitles with Tesseract 4 OCR."""

    localizations = {
        "zh-hans": {
            "Recognize image subtitles with Tesseract 4 OCR.": (
                "使用 Tesseract 4 OCR 识别图像字幕。"
            ),
            "Tesseract language code (default: %(default)s)": (
                "Tesseract 语言代码（默认：%(default)s）"
            ),
            (
                "image subtitle infile path (directory containing index.html and "
                "png files, or a .sup file)"
            ): (
                "图像字幕输入文件路径（包含 index.html 和 png 文件的目录，"
                "或 .sup 文件）"
            ),
            "recognized subtitle outfile path": "识别后字幕输出文件路径",
        },
        "zh-hant": {
            "Recognize image subtitles with Tesseract 4 OCR.": (
                "使用 Tesseract 4 OCR 識別影像字幕。"
            ),
            "Tesseract language code (default: %(default)s)": (
                "Tesseract 語言代碼（預設：%(default)s）"
            ),
            (
                "image subtitle infile path (directory containing index.html and "
                "png files, or a .sup file)"
            ): (
                "影像字幕輸入檔案路徑（包含 index.html 和 png 檔案的目錄，"
                "或 .sup 檔案）"
            ),
            "recognized subtitle outfile path": "識別後字幕輸出檔案路徑",
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
            "--infile",
            dest="infile_path",
            required=True,
            type=input_file_or_dir_arg(),
            help=(
                "image subtitle infile path "
                "(directory containing index.html and png files, or a .sup file)"
            ),
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--language",
            default="eng",
            help="Tesseract language code (default: %(default)s)",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "--outfile",
            dest="outfile_path",
            required=True,
            type=output_file_arg(exist_ok=True),
            help="recognized subtitle outfile path",
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
        return "tesseract4"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        infile_path: Path,
        outfile_path: Path,
        language: str,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if outfile_path.exists() and not overwrite:
            parser.error(f"{outfile_path} already exists")

        # Perform operations
        try:
            global ocr_image_series_with_tesseract4  # noqa: PLW0603
            if ocr_image_series_with_tesseract4 is None:
                from scinoephile.image.ocr.tesseract import (  # noqa: PLC0415
                    ocr_image_series_with_tesseract4 as imported_ocr,
                )

                ocr_image_series_with_tesseract4 = imported_ocr

            image_series = ImageSeries.load(infile_path)
            text_series = ocr_image_series_with_tesseract4(
                image_series,
                language=language,
            )
        except (
            FileNotFoundError,
            NotADirectoryError,
            ImportError,
            ScinoephileError,
            ValueError,
        ) as exc:
            parser.error(str(exc))

        # Write outputs
        text_series.save(outfile_path, format_="srt")


if __name__ == "__main__":
    OcrTesseract4Cli.main()
