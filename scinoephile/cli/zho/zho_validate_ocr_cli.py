#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for standard Chinese OCR subtitle validation."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Unpack

from scinoephile.common import (
    CLIKwargs,
    DirectoryNotFoundError,
)
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    int_arg,
    output_dir_arg,
)
from scinoephile.common.exception import NotAFileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.zho import validate_zho_ocr

__all__ = ["ZhoValidateOcrCli"]


class ZhoValidateOcrCli(ScinoephileCliBase):
    """Validate OCR text against subtitle images."""

    localizations = {
        "zh-hans": {
            "command-line interface for standard Chinese OCR subtitle validation": (
                "标准中文 OCR 字幕校验命令行界面"
            ),
        },
        "zh-hant": {
            "command-line interface for standard Chinese OCR subtitle validation": (
                "標準中文 OCR 字幕驗證命令列介面"
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

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
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
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        # Validate arguments
        parser = kwargs.pop("_parser", cls.argparser())
        infile_path = kwargs.pop("infile")
        stop_at_idx = kwargs.pop("stop_at_idx")
        interactive = kwargs.pop("interactive")
        outfile_path: Path = kwargs.pop("outfile")
        overwrite = kwargs.pop("overwrite")
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
        )

        # Write output
        validated.save(outfile_path)


if __name__ == "__main__":
    ZhoValidateOcrCli.main()
