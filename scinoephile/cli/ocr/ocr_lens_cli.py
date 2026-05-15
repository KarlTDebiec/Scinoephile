#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for Google Lens OCR."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_or_dir_arg,
    output_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.image.ocr.lens import ocr_image_series_with_lens
from scinoephile.image.subtitles import ImageSeries

__all__ = ["OcrLensCli"]

OCR_LENS_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "Google Lens language code": "Google Lens 语言代码",
        "Recognize image subtitles with Google Lens.": (
            "使用 Google Lens 识别图像字幕。"
        ),
        (
            "image subtitle infile path (directory containing index.html and "
            "png files, or a .sup file)"
        ): "图像字幕输入文件路径（包含 index.html 和 png 文件，或 .sup 文件）",
        "recognized subtitle outfile path": "识别后字幕输出文件路径",
    },
    "zh-hant": {
        "Google Lens language code": "Google Lens 語言代碼",
        "Recognize image subtitles with Google Lens.": (
            "使用 Google Lens 識別影像字幕。"
        ),
        (
            "image subtitle infile path (directory containing index.html and "
            "png files, or a .sup file)"
        ): "影像字幕輸入檔案路徑（包含 index.html 和 png 檔案，或 .sup 檔案）",
        "recognized subtitle outfile path": "識別後字幕輸出檔案路徑",
    },
}
"""Localized help text keyed by locale and English source text."""


class OcrLensCli(ScinoephileCliBase):
    """Recognize image subtitles with Google Lens."""

    localizations = OCR_LENS_LOCALIZATIONS
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
            default="en",
            help="Google Lens language code",
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
        return "lens"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        infile_path: Path,
        language: str,
        outfile_path: Path,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if outfile_path.exists() and not overwrite:
            parser.error(f"{outfile_path} already exists")

        # Read inputs
        try:
            image_series = ImageSeries.load(infile_path)
        except (
            FileNotFoundError,
            NotADirectoryError,
            ScinoephileError,
            ValueError,
        ) as exc:
            parser.error(str(exc))

        # Perform operations
        try:
            text_series = ocr_image_series_with_lens(
                image_series,
                language=language,
            )
        except (
            ImportError,
            NotADirectoryError,
            OSError,
            RuntimeError,
            ScinoephileError,
            ValueError,
        ) as exc:
            parser.error(str(exc))

        # Write outputs
        text_series.save(outfile_path, format_="srt")


if __name__ == "__main__":
    OcrLensCli.main()
