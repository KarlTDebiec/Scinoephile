#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for Google Lens OCR."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.helpers.cache import (
    CACHE_LOCALIZATIONS,
    CacheArguments,
    add_cache_args,
)
from scinoephile.cli.helpers.io import read_image_series, write_series
from scinoephile.common.argument_parsing import (
    enum_arg,
    enum_metavar,
    get_arg_groups_by_name,
    input_file_or_dir_arg,
    int_arg,
    output_file_arg,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.image.ocr.lens import ocr_image_series_with_lens

__all__ = ["OcrLensCli"]

OCR_LENS_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "language of the OCR text to recognize (default: %(default)s)": (
            "要识别的 OCR 文本语言（默认：%(default)s）"
        ),
        "Google Lens request attempts per uncached image (default: %(default)s)": (
            "每张未缓存图像的 Google Lens 请求尝试次数（默认：%(default)s）"
        ),
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
        "language of the OCR text to recognize (default: %(default)s)": (
            "要識別的 OCR 文字語言（預設：%(default)s）"
        ),
        "Google Lens request attempts per uncached image (default: %(default)s)": (
            "每張未快取影像的 Google Lens 請求嘗試次數（預設：%(default)s）"
        ),
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

    localizations = merge_localizations(CACHE_LOCALIZATIONS, OCR_LENS_LOCALIZATIONS)
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
            "cache arguments",
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
            "--retries",
            default=3,
            type=int_arg(min_value=1),
            help=(
                "Google Lens request attempts per uncached image (default: %(default)s)"
            ),
        )

        # Cache arguments
        add_cache_args(arg_groups["cache arguments"])

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
        language: Language,
        outfile_path: Path,
        overwrite: bool,
        cache_args: CacheArguments,
        retries: int,
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
            text_series = ocr_image_series_with_lens(
                image_series,
                cache_dir_path=cache_args.dir_path / "google-lens",
                language=language,
                overwrite_cache=cache_args.overwrite,
                retries=retries,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write outputs
        write_series(parser, text_series, outfile_path, overwrite)


if __name__ == "__main__":
    OcrLensCli.main()
