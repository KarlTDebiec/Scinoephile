#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for character error rate analysis."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.analysis import get_series_cer
from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import get_arg_groups_by_name, input_file_arg
from scinoephile.core.subtitles import Series


class AnalysisCerCli(CommandLineInterface):
    """Command-line interface for subtitle character error rate output."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)
        arg_groups = get_arg_groups_by_name(parser, "input arguments")

        arg_groups["input arguments"].add_argument(
            "reference_infile_path",
            metavar="reference-infile",
            type=input_file_arg(),
            help="subtitle infile for reference series",
        )
        arg_groups["input arguments"].add_argument(
            "candidate_infile_path",
            metavar="candidate-infile",
            type=input_file_arg(),
            help="subtitle infile for candidate series",
        )

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        reference_infile_path = kwargs.pop("reference_infile_path")
        candidate_infile_path = kwargs.pop("candidate_infile_path")

        reference_series = Series.load(reference_infile_path)
        candidate_series = Series.load(candidate_infile_path)
        result = get_series_cer(reference_series, candidate_series)
        print(f"CER: {result.cer}")
        print(f"Correct: {result.correct}")
        print(f"Substitutions: {result.substitutions}")
        print(f"Insertions: {result.insertions}")
        print(f"Deletions: {result.deletions}")
        print(f"Reference length: {result.reference_length}")

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "cer"


if __name__ == "__main__":
    AnalysisCerCli.main()
