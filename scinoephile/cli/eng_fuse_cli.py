#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for fusing English OCR subtitle inputs."""

from __future__ import annotations

from argparse import ArgumentParser
from sys import stdout
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import get_arg_groups_by_name, input_file_arg
from scinoephile.common.validation import val_output_path
from scinoephile.core.subtitles import Series
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
            metavar="lens-infile",
            type=input_file_arg(),
            help="English subtitle infile OCRed using Google Lens",
        )
        arg_groups["input arguments"].add_argument(
            "tesseract_infile",
            metavar="tesseract-infile",
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
            metavar="FILE",
            default="-",
            type=str,
            help="English subtitle outfile (default: stdout)",
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

        lens = Series.load(lens_infile)
        tesseract = Series.load(tesseract_infile)
        if clean:
            lens = get_eng_cleaned(lens, remove_empty=False)
            tesseract = get_eng_cleaned(tesseract, remove_empty=False)
        fused = get_eng_ocr_fused(lens, tesseract)
        cls._write_series(parser, fused, outfile, overwrite)

    @classmethod
    def _write_series(
        cls,
        parser: ArgumentParser,
        series: Series,
        outfile: str,
        overwrite: bool,
    ):
        """Write a Series to a file path or stdout.

        Arguments:
            parser: argument parser for error reporting
            series: series to write
            outfile: output file path or "-" for stdout
            overwrite: whether to overwrite an existing file
        """
        if outfile == "-":
            stdout.write(series.to_string(format_="srt"))
            return
        output_path = val_output_path(outfile, exist_ok=True)
        if output_path.exists() and not overwrite:
            parser.error(f"{output_path} already exists")
        series.save(output_path)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "fuse"


if __name__ == "__main__":
    EngFuseCli.main()
