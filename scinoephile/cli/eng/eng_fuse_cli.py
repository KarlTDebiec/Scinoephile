#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for fusing English OCR subtitle inputs."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import get_arg_groups_by_name, input_file_arg
from scinoephile.core.cli.io import load_subtitle_series, write_subtitle_series
from scinoephile.lang.eng import get_eng_cleaned, get_eng_ocr_fused


class EngFuseCli(CommandLineInterface):
    """Command-line interface for fusing English OCR subtitle inputs."""

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
            "lens_infile",
            metavar="LENS_INFILE",
            type=input_file_arg(),
            help="English subtitle infile OCRed using Google Lens",
        )
        arg_groups["input arguments"].add_argument(
            "tesseract_infile",
            metavar="TESSERACT_INFILE",
            type=input_file_arg(),
            help="English subtitle infile OCRed using Tesseract",
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
            default="-",
            type=str,
            help='English subtitle outfile path or "-" for stdout',
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        parser = kwargs.pop("_parser", cls.argparser())
        lens_infile = kwargs.pop("lens_infile")
        tesseract_infile = kwargs.pop("tesseract_infile")
        clean = kwargs.pop("clean")
        outfile = kwargs.pop("outfile")
        overwrite = kwargs.pop("overwrite")

        lens = load_subtitle_series(parser, lens_infile)
        tesseract = load_subtitle_series(parser, tesseract_infile)
        if clean:
            lens = get_eng_cleaned(lens, remove_empty=False)
            tesseract = get_eng_cleaned(tesseract, remove_empty=False)
        fused = get_eng_ocr_fused(lens, tesseract)
        write_subtitle_series(parser, fused, outfile, overwrite)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "fuse"


if __name__ == "__main__":
    EngFuseCli.main()
