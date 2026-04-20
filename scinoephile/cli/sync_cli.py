#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for synchronizing subtitle series."""

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
from scinoephile.core.synchronization import get_synced_series


class SyncCli(CommandLineInterface):
    """Command-line interface for synchronizing subtitle series."""

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
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--top-infile",
            metavar="TOP_INFILE",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='subtitle infile for top line or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--bottom-infile",
            metavar="BOTTOM_INFILE",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='subtitle infile for bottom line or "-" for stdin',
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            metavar="OUTFILE",
            default=None,
            type=output_file_arg(),
            help="synchronized subtitle outfile path (default: stdout)",
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
        # Validate arguments
        parser = kwargs.pop("_parser", cls.argparser())
        top_infile = kwargs.pop("top_infile")
        bottom_infile = kwargs.pop("bottom_infile")
        outfile: Path | None = kwargs.pop("outfile")
        overwrite = kwargs.pop("overwrite")
        if top_infile == "-" and bottom_infile == "-":
            try:
                raise ArgumentConflictError(
                    "--top-infile and --bottom-infile may not both be '-'"
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
        top = read_series(parser, top_infile, allow_stdin=True)
        bottom = read_series(parser, bottom_infile, allow_stdin=True)

        # Perform operations
        synced = get_synced_series(top, bottom)

        # Write outputs
        write_series(parser, synced, outfile if outfile is not None else "-", overwrite)


if __name__ == "__main__":
    SyncCli.main()
