#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for English OCR subtitle validation."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Unpack

from scinoephile.common import (
    CLIKwargs,
    CommandLineInterface,
    DirectoryNotFoundError,
)
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    int_arg,
    output_dir_arg,
    output_file_arg,
)
from scinoephile.common.exception import ArgumentConflictError, NotAFileError
from scinoephile.core.cli import write_series
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng import validate_eng_ocr

__all__ = ["EngValidateOcrCli"]


class EngValidateOcrCli(CommandLineInterface):
    """Validate English OCR text against subtitle images."""

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
                "English OCR image subtitle infile path "
                "(directory with index.html/pngs or .sup file; stdin is not supported)"
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
            "--output-dir",
            default=None,
            type=output_dir_arg(),
            help="directory in which to save validation image outputs",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            default=None,
            type=output_file_arg(),
            help="English subtitle outfile path (default: stdout)",
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
        output_dir_path: Path | None = kwargs.pop("output_dir")
        outfile_path: Path | None = kwargs.pop("outfile")
        overwrite = kwargs.pop("overwrite")
        if overwrite and outfile_path is None:
            try:
                raise ArgumentConflictError(
                    "--overwrite may only be used with --outfile"
                )
            except ArgumentConflictError as exc:
                parser.error(str(exc))

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
        validated = validate_eng_ocr(
            series,
            stop_at_idx=stop_at_idx,
            interactive=interactive,
            output_dir_path=output_dir_path,
        )

        # Write output
        write_series(
            parser,
            validated,
            outfile_path if outfile_path is not None else "-",
            overwrite,
        )


if __name__ == "__main__":
    EngValidateOcrCli.main()
