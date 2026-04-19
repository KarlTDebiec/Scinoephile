#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for English subtitle operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
)
from scinoephile.lang.eng import get_eng_cleaned, get_eng_flattened, get_eng_proofread

from ..subtitles_io import load_subtitle_series, write_subtitle_series
from .eng_fuse_cli import EngFuseCli


class EngCli(CommandLineInterface):
    """Command-line interface for English subtitle operations."""

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
            metavar="INFILE",
            default="-",
            type=str,
            help='English subtitle infile path or "-" for stdin',
        )

        # Operation arguments
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

        subparsers = parser.add_subparsers(
            dest="eng_subcommand",
            help="subcommand",
            required=False,
        )
        subcommands = cls.subcommands()
        for name in sorted(subcommands):
            subcommands[name].argparser(subparsers=subparsers)
        parser.set_defaults(_parser=parser)

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        parser = kwargs.pop("_parser", cls.argparser())
        subcommand_name = kwargs.pop("eng_subcommand", None)
        if subcommand_name is not None:
            subcommand_cli_class = cls.subcommands()[subcommand_name]
            subcommand_cli_class._main(**kwargs)
            return

        infile = kwargs.pop("infile")
        outfile = kwargs.pop("outfile")
        clean = kwargs.pop("clean")
        flatten = kwargs.pop("flatten")
        proofread = kwargs.pop("proofread")
        overwrite = kwargs.pop("overwrite")

        if not (clean or flatten or proofread):
            parser.error("At least one operation required")
        series = load_subtitle_series(parser, infile, allow_stdin=True)
        if clean:
            series = get_eng_cleaned(series)
        if proofread:
            series = get_eng_proofread(series)
        if flatten:
            series = get_eng_flattened(series)
        write_subtitle_series(parser, series, outfile, overwrite)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "eng"

    @classmethod
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Names and types of tools wrapped by command-line interface.

        Returns:
            mapping of subcommand names to CLI classes
        """
        return {
            EngFuseCli.name(): EngFuseCli,
        }


if __name__ == "__main__":
    EngCli.main()
