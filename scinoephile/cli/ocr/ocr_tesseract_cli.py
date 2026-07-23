#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for Tesseract OCR."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.helpers.io import read_image_series, write_series
from scinoephile.common.argument_parsing import (
    enum_arg,
    enum_metavar,
    get_arg_groups_by_name,
    input_file_or_dir_arg,
    output_file_arg,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.image.ocr.tesseract import ocr_image_series_with_tesseract

__all__ = ["OcrTesseractCli"]

OCR_TESSERACT_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "Recognize image subtitles with Tesseract OCR.": (
            "使用 Tesseract OCR 识别图像字幕。"
        ),
        "language of the OCR text to recognize (default: %(default)s)": (
            "要识别的 OCR 文本语言（默认：%(default)s）"
        ),
        "Tesseract requires the system tesseract executable and language data.": (
            "Tesseract 需要系统 tesseract 可执行文件和语言数据。"
        ),
        "run a second legacy-engine pass to detect italic text": (
            "运行第二次旧版引擎识别以检测斜体文本"
        ),
        (
            "image subtitle infile path (directory containing index.html and "
            "png files, or a .sup file)"
        ): ("图像字幕输入文件路径（包含 index.html 和 png 文件的目录，或 .sup 文件）"),
        "recognized subtitle outfile path": "识别后字幕输出文件路径",
    },
    "zh-hant": {
        "Recognize image subtitles with Tesseract OCR.": (
            "使用 Tesseract OCR 識別影像字幕。"
        ),
        "language of the OCR text to recognize (default: %(default)s)": (
            "要識別的 OCR 文字語言（預設：%(default)s）"
        ),
        "Tesseract requires the system tesseract executable and language data.": (
            "Tesseract 需要系統 tesseract 可執行檔和語言資料。"
        ),
        "run a second legacy-engine pass to detect italic text": (
            "執行第二次舊版引擎識別以偵測斜體文字"
        ),
        (
            "image subtitle infile path (directory containing index.html and "
            "png files, or a .sup file)"
        ): ("影像字幕輸入檔案路徑（包含 index.html 和 png 檔案的目錄，或 .sup 檔案）"),
        "recognized subtitle outfile path": "識別後字幕輸出檔案路徑",
    },
}
"""Localized help text keyed by locale and English source text."""


class OcrTesseractCli(ScinoephileCliBase):
    """Recognize image subtitles with Tesseract OCR.

    Tesseract requires the system tesseract executable and language data.
    """

    localizations = OCR_TESSERACT_LOCALIZATIONS
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
            default=Language.eng,
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help="language of the OCR text to recognize (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--detect-italics",
            action="store_true",
            help="run a second legacy-engine pass to detect italic text",
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
        return "tesseract"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        infile_path: Path,
        outfile_path: Path,
        detect_italics: bool,
        language: Language,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if outfile_path.exists() and not overwrite:
            parser.error(f"{outfile_path} already exists")
        if detect_italics and language is not Language.eng:
            parser.error("--detect-italics may only be used with --language eng")

        # Read inputs
        image_series = read_image_series(parser, infile_path)

        # Perform operations
        try:
            text_series = ocr_image_series_with_tesseract(
                image_series,
                detect_italics=detect_italics,
                language=language,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write outputs
        write_series(parser, text_series, outfile_path, overwrite)


if __name__ == "__main__":
    OcrTesseractCli.main()
