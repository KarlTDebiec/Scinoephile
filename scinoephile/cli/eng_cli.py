#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for English subtitle operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common import CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
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
            required=True,
            type=input_file_arg(),
            help="English subtitle infile",
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
            required=True,
            type=output_file_arg(exist_ok=True),
            help="English subtitle outfile",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )

    @classmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: Keyword arguments
        """
        infile = kwargs.pop("infile")
        outfile = kwargs.pop("outfile")
        clean = kwargs.pop("clean")
        flatten = kwargs.pop("flatten")
        proofread = kwargs.pop("proofread")
        overwrite = kwargs.pop("overwrite")

        if not (clean or flatten or proofread):
            cls.argparser().error("At least one operation required")
        if outfile.exists() and not overwrite:
            cls.argparser().error(f"{outfile} already exists")

        series = Series.load(infile)
        if clean:
            series = get_eng_cleaned(series)
        if proofread:
            series = get_eng_proofread(series)
        if flatten:
            series = get_eng_flattened(series)
        series.save(outfile)


if __name__ == "__main__":
    EngCli.main()
