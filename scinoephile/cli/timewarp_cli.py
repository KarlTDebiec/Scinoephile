#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for timewarping subtitle series."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli.io import (
    load_subtitle_series,
    parser_error_from_exception,
    write_subtitle_series,
)
from scinoephile.core.timing import get_series_timewarped


class TimewarpCli(CommandLineInterface):
    """Command-line interface for timewarping subtitle series."""

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
            "anchor_infile",
            metavar="ANCHOR_INFILE",
            type=input_file_arg(),
            help="subtitle infile used as anchor timing reference",
        )
        arg_groups["input arguments"].add_argument(
            "mobile_infile",
            metavar="MOBILE_INFILE",
            type=input_file_arg(),
            help="mobile subtitle infile to be timewarped",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--one-start-idx",
            metavar="N",
            type=int_arg(min_value=1),
            default=None,
            help="1-based start index in anchor series (default: 1)",
        )
        arg_groups["operation arguments"].add_argument(
            "--one-end-idx",
            metavar="N",
            type=int_arg(min_value=1),
            default=None,
            help="1-based end index in anchor series (default: final subtitle)",
        )
        arg_groups["operation arguments"].add_argument(
            "--two-start-idx",
            metavar="N",
            type=int_arg(min_value=1),
            default=None,
            help="1-based start index in moving series (default: 1)",
        )
        arg_groups["operation arguments"].add_argument(
            "--two-end-idx",
            metavar="N",
            type=int_arg(min_value=1),
            default=None,
            help="1-based end index in moving series (default: final subtitle)",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            metavar="OUTFILE",
            default="-",
            type=str,
            help='timewarped subtitle outfile path or "-" for stdout',
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
        anchor_infile = kwargs.pop("anchor_infile")
        mobile_infile = kwargs.pop("mobile_infile")
        one_start_idx = kwargs.pop("one_start_idx")
        one_end_idx = kwargs.pop("one_end_idx")
        two_start_idx = kwargs.pop("two_start_idx")
        two_end_idx = kwargs.pop("two_end_idx")
        outfile = kwargs.pop("outfile")
        overwrite = kwargs.pop("overwrite")

        anchor = load_subtitle_series(parser, anchor_infile)
        mobile = load_subtitle_series(parser, mobile_infile)
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
            parser_error_from_exception(parser, exc)
        write_subtitle_series(parser, timewarped, outfile, overwrite)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "timewarp"


if __name__ == "__main__":
    TimewarpCli.main()
