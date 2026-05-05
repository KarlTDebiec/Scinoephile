#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for PaddleOCR."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    output_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.image.ocr.paddle import ocr_image_series_with_paddle
from scinoephile.image.subtitles import ImageSeries

__all__ = ["OcrPaddleCli"]


class OcrPaddleCli(ScinoephileCliBase):
    """Recognize image subtitles with PaddleOCR."""

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

        arg_groups["input arguments"].add_argument(
            "--infile",
            dest="infile_path",
            required=True,
            type=Path,
            help=(
                "image subtitle infile path "
                "(directory containing index.html and png files, or a .sup file)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--language",
            default="en",
            help=(
                "PaddleOCR language code: en (English), ch (simplified Chinese "
                "and English), chinese_cht (traditional Chinese)"
            ),
        )
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
        language: str,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()

        if outfile_path.exists() and not overwrite:
            parser.error(f"{outfile_path} already exists")

        try:
            image_series = ImageSeries.load(infile_path)
            text_series = ocr_image_series_with_paddle(
                image_series,
                language=language,
            )
        except (
            FileNotFoundError,
            NotADirectoryError,
            ScinoephileError,
            ValueError,
        ) as exc:
            parser.error(str(exc))
        text_series.save(outfile_path, format_="srt")


if __name__ == "__main__":
    OcrPaddleCli.main()
