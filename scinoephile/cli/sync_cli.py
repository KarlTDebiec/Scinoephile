#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for synchronizing subtitle series."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
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
            metavar="top-infile",
            type=input_file_arg(),
            help="subtitle infile for top line",
        )
        arg_groups["input arguments"].add_argument(
            "bottom_infile",
            metavar="bottom-infile",
            type=input_file_arg(),
            help="subtitle infile for bottom line",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            metavar="FILE",
            required=True,
            type=output_file_arg(exist_ok=True),
            help="synchronized subtitle outfile",
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
        top_infile = kwargs.pop("top_infile")
        bottom_infile = kwargs.pop("bottom_infile")
        outfile = kwargs.pop("outfile")
        overwrite = kwargs.pop("overwrite")

        if outfile.exists() and not overwrite:
            parser.error(f"{outfile} already exists")

        top = Series.load(top_infile)
        bottom = Series.load(bottom_infile)

        synced = get_synced_series(top, bottom)
        synced.save(outfile)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "sync"


if __name__ == "__main__":
    SyncCli.main()
