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
from scinoephile.core.cli import write_series
from scinoephile.core.subtitles import Series
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
            "top_infile",
            metavar="TOP_INFILE",
            type=input_file_arg(),
            help="subtitle infile for top line",
        )
        arg_groups["input arguments"].add_argument(
            "bottom_infile",
            metavar="BOTTOM_INFILE",
            type=input_file_arg(),
            help="subtitle infile for bottom line",
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
        if overwrite and outfile is None:
            try:
                raise ArgumentConflictError(
                    "--overwrite may only be used with --outfile"
                )
            except ArgumentConflictError as exc:
                parser.error(str(exc))

        # Read inputs
        top = Series.load(top_infile)
        bottom = Series.load(bottom_infile)

        # Perform operations
        synced = get_synced_series(top, bottom)

        # Write outputs
        write_series(parser, synced, outfile if outfile is not None else "-", overwrite)


if __name__ == "__main__":
    SyncCli.main()
