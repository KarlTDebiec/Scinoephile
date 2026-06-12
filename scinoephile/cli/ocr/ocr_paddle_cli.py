#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PaddleOCR."""

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
from scinoephile.image.ocr.paddle import ocr_image_series_with_paddle

__all__ = ["OcrPaddleCli"]

OCR_PADDLE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "language of the OCR text to recognize (default: %(default)s)": (
            "要识别的 OCR 文本语言（默认：%(default)s）"
        ),
        "PaddleOCR requires the optional PaddleOCR runtime dependencies.": (
            "PaddleOCR 需要可选的 PaddleOCR 运行时依赖。"
        ),
        "Recognize image subtitles with PaddleOCR.": ("使用 PaddleOCR 识别图像字幕。"),
        (
            "image subtitle infile path (directory containing index.html and "
            "png files, or a .sup file)"
        ): ("图像字幕输入文件路径（包含 index.html 和 png 文件的目录，或 .sup 文件）"),
        "recognized subtitle outfile path": "识别后字幕输出文件路径",
    },
    "zh-hant": {
        "language of the OCR text to recognize (default: %(default)s)": (
            "要識別的 OCR 文字語言（預設：%(default)s）"
        ),
        "PaddleOCR requires the optional PaddleOCR runtime dependencies.": (
            "PaddleOCR 需要可選的 PaddleOCR 執行時依賴。"
        ),
        "Recognize image subtitles with PaddleOCR.": ("使用 PaddleOCR 識別影像字幕。"),
        (
            "image subtitle infile path (directory containing index.html and "
            "png files, or a .sup file)"
        ): ("影像字幕輸入檔案路徑（包含 index.html 和 png 檔案的目錄，或 .sup 檔案）"),
        "recognized subtitle outfile path": "識別後字幕輸出檔案路徑",
    },
}
"""Localized help text keyed by locale and English source text."""


class OcrPaddleCli(ScinoephileCliBase):
    """Recognize image subtitles with PaddleOCR.

    PaddleOCR requires the optional PaddleOCR runtime dependencies.
    """

    localizations = OCR_PADDLE_LOCALIZATIONS
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
        return "paddle"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        infile_path: Path,
        outfile_path: Path,
        language: Language,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if outfile_path.exists() and not overwrite:
            parser.error(f"{outfile_path} already exists")

        # Read inputs
        image_series = read_image_series(parser, infile_path)

        # Perform operations
        try:
            text_series = ocr_image_series_with_paddle(
                image_series,
                language=language,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write outputs
        write_series(parser, text_series, outfile_path, overwrite)


if __name__ == "__main__":
    OcrPaddleCli.main()
