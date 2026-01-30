#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for English subtitle operations."""

from __future__ import annotations

from argparse import ArgumentParser
from sys import stdin, stdout
from typing import Unpack

from scinoephile.common import CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
)
from scinoephile.common.command_line_interface import CLIKwargs
from scinoephile.common.validation import val_input_path, val_output_path
from scinoephile.core.subtitles import Series
from scinoephile.lang.eng import get_eng_cleaned, get_eng_flattened, get_eng_proofread


class EngCli(CommandLineInterface):
    """Command-line interface for English subtitle operations."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
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
            "-i",
            "--infile",
            metavar="FILE",
            default="-",
            type=str,
            help="English subtitle infile (default: stdin)",
        )
        arg_groups["operation arguments"].add_argument(
            "--clean",
            action="store_true",
            help="clean subtitles of closed-caption annotations and other anomalies",
        )
        arg_groups["operation arguments"].add_argument(
            "--flatten",
            action="store_true",
            help="flatten multi-line subtitles into single lines",
        )
        arg_groups["operation arguments"].add_argument(
            "--proofread",
            action="store_true",
            help="proofread subtitles using configured LLM workflow",
        )
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
            **kwargs: Keyword arguments
        """
        parser = kwargs.pop("_parser", cls.argparser())
        infile = kwargs.pop("infile")
        outfile = kwargs.pop("outfile")
        clean = kwargs.pop("clean")
        flatten = kwargs.pop("flatten")
        proofread = kwargs.pop("proofread")
        overwrite = kwargs.pop("overwrite")

        if not (clean or flatten or proofread):
            parser.error("At least one operation required")
        series = cls._load_series(infile)
        if clean:
            series = get_eng_cleaned(series)
        if proofread:
            series = get_eng_proofread(series)
        if flatten:
            series = get_eng_flattened(series)
        cls._write_series(parser, series, outfile, overwrite)

    @classmethod
    def _load_series(cls, infile: str) -> Series:
        """Load a Series from a file path or stdin.

        Arguments:
            infile: Input file path or "-" for stdin
        Returns:
            loaded Series
        """
        if infile == "-":
            return Series.from_string(stdin.read(), format_="srt")
        input_path = val_input_path(infile)
        return Series.load(input_path)

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
            parser: Argument parser for error reporting
            series: Series to write
            outfile: Output file path or "-" for stdout
            overwrite: Whether to overwrite an existing file
        """
        if outfile == "-":
            stdout.write(series.to_string(format_="srt"))
            return
        output_path = val_output_path(outfile, exist_ok=True)
        if output_path.exists() and not overwrite:
            parser.error(f"{output_path} already exists")
        series.save(output_path)


if __name__ == "__main__":
    EngCli.main()
