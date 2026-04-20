#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for English OCR subtitle fusion."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
from scinoephile.common.exception import ArgumentConflictError
from scinoephile.core.cli import read_series, write_series
from scinoephile.lang.eng import get_eng_cleaned, get_eng_ocr_fused


class EngFuseCli(CommandLineInterface):
    """Command-line interface for English OCR subtitle fusion."""

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
            "--lens-infile",
            metavar="LENS_INFILE",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='English subtitles OCRed using Google Lens or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--tesseract-infile",
            metavar="TESSERACT_INFILE",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='English subtitles OCRed using Tesseract or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--clean",
            action="store_true",
            default=False,
            help="clean both OCR subtitle infiles before fusing",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            metavar="OUTFILE",
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
        return "fuse"

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        # Validate arguments
        parser = kwargs.pop("_parser", cls.argparser())
        lens_infile = kwargs.pop("lens_infile")
        tesseract_infile = kwargs.pop("tesseract_infile")
        clean = kwargs.pop("clean")
        outfile: Path | None = kwargs.pop("outfile")
        overwrite = kwargs.pop("overwrite")
        if lens_infile == "-" and tesseract_infile == "-":
            try:
                raise ArgumentConflictError(
                    "--lens-infile and --tesseract-infile may not both be '-'"
                )
            except ArgumentConflictError as exc:
                parser.error(str(exc))
        if overwrite and outfile is None:
            try:
                raise ArgumentConflictError(
                    "--overwrite may only be used with --outfile"
                )
            except ArgumentConflictError as exc:
                parser.error(str(exc))

        # Read inputs
        lens = read_series(parser, lens_infile, allow_stdin=True)
        tesseract = read_series(parser, tesseract_infile, allow_stdin=True)

        # Perform operations
        if clean:
            lens = get_eng_cleaned(lens, remove_empty=False)
            tesseract = get_eng_cleaned(tesseract, remove_empty=False)
        fused = get_eng_ocr_fused(lens, tesseract)

        # Write outputs
        write_series(parser, fused, outfile if outfile is not None else "-", overwrite)


if __name__ == "__main__":
    EngFuseCli.main()
