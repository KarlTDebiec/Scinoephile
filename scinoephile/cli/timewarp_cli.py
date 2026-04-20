#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for timewarping subtitle series."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from scinoephile.common.exception import ArgumentConflictError
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import read_series, write_series
from scinoephile.core.timing import get_series_timewarped

__all__ = ["TimewarpCli"]


class TimewarpCli(CommandLineInterface):
    """Shift and stretch the timings of one subtitle series to match another."""

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
            "--anchor-infile",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='subtitle infile used as anchor timing reference or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--mobile-infile",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='mobile subtitle infile to be timewarped or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--one-start-idx",
            type=int_arg(min_value=1),
            default=None,
            help="1-based start index in anchor series (default: 1)",
        )
        arg_groups["operation arguments"].add_argument(
            "--one-end-idx",
            type=int_arg(min_value=1),
            default=None,
            help="1-based end index in anchor series (default: final subtitle)",
        )
        arg_groups["operation arguments"].add_argument(
            "--two-start-idx",
            type=int_arg(min_value=1),
            default=None,
            help="1-based start index in moving series (default: 1)",
        )
        arg_groups["operation arguments"].add_argument(
            "--two-end-idx",
            type=int_arg(min_value=1),
            default=None,
            help="1-based end index in moving series (default: final subtitle)",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            default=None,
            type=output_file_arg(),
            help="timewarped subtitle outfile path (default: stdout)",
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
        anchor_infile_path = kwargs.pop("anchor_infile")
        mobile_infile_path = kwargs.pop("mobile_infile")
        one_start_idx = kwargs.pop("one_start_idx")
        one_end_idx = kwargs.pop("one_end_idx")
        two_start_idx = kwargs.pop("two_start_idx")
        two_end_idx = kwargs.pop("two_end_idx")
        outfile_path: Path | None = kwargs.pop("outfile")
        overwrite = kwargs.pop("overwrite")
        if anchor_infile_path == "-" and mobile_infile_path == "-":
            try:
                raise ArgumentConflictError(
                    "--anchor-infile and --mobile-infile may not both be '-'"
                )
            except ArgumentConflictError as exc:
                parser.error(str(exc))
        if overwrite and outfile_path is None:
            try:
                raise ArgumentConflictError(
                    "--overwrite may only be used with --outfile"
                )
            except ArgumentConflictError as exc:
                parser.error(str(exc))

        # Read inputs
        anchor = read_series(parser, anchor_infile_path, allow_stdin=True)
        mobile = read_series(parser, mobile_infile_path, allow_stdin=True)

        # Perform operations
        try:
            timewarped = get_series_timewarped(
                source_one=anchor,
                source_two=mobile,
                one_start_idx=one_start_idx,
                one_end_idx=one_end_idx,
                two_start_idx=two_start_idx,
                two_end_idx=two_end_idx,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write outputs
        write_series(
            parser,
            timewarped,
            outfile_path if outfile_path is not None else "-",
            overwrite,
        )


if __name__ == "__main__":
    TimewarpCli.main()
