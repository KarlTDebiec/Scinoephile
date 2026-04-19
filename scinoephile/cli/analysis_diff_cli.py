#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for subtitle diff analysis."""

from __future__ import annotations

from argparse import ArgumentParser
from sys import stdout
from typing import Unpack

from scinoephile.analysis import get_series_diff
from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import (
    float_arg,
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core.subtitles import Series


class AnalysisDiffCli(CommandLineInterface):
    """Command-line interface for subtitle diff analysis."""

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
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "one_infile",
            metavar="one-infile",
            type=input_file_arg(),
            help="subtitle infile for first series",
        )
        arg_groups["input arguments"].add_argument(
            "two_infile",
            metavar="two-infile",
            type=input_file_arg(),
            help="subtitle infile for second series",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--one-label",
            metavar="LABEL",
            default="one",
            type=str,
            help="label for first series (default: one)",
        )
        arg_groups["operation arguments"].add_argument(
            "--two-label",
            metavar="LABEL",
            default="two",
            type=str,
            help="label for second series (default: two)",
        )
        arg_groups["operation arguments"].add_argument(
            "--similarity-cutoff",
            metavar="N",
            default=0.6,
            type=float_arg(min_value=0.0, max_value=1.0),
            help="similarity threshold used to pair replacements (default: 0.6)",
        )

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        one_infile = kwargs.pop("one_infile")
        two_infile = kwargs.pop("two_infile")
        one_label = kwargs.pop("one_label")
        two_label = kwargs.pop("two_label")
        similarity_cutoff = kwargs.pop("similarity_cutoff")

        one_series = Series.load(one_infile)
        two_series = Series.load(two_infile)
        diff = get_series_diff(
            one_series,
            two_series,
            one_lbl=one_label,
            two_lbl=two_label,
            similarity_cutoff=similarity_cutoff,
        )
        for line_diff in diff:
            stdout.write(f"{line_diff}\n")

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "diff"


if __name__ == "__main__":
    AnalysisDiffCli.main()
