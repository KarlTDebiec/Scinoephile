#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for character error rate analysis."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.analysis import get_series_cer
from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import get_arg_groups_by_name, input_file_arg
from scinoephile.common.exception import ArgumentConflictError
from scinoephile.core.cli import read_series


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

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--reference-infile",
            metavar="REFERENCE_INFILE",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='subtitle infile for reference series or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--candidate-infile",
            metavar="CANDIDATE_INFILE",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='subtitle infile for candidate series or "-" for stdin',
        )

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "cer"

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        # Validate arguments
        parser = kwargs.pop("_parser", cls.argparser())
        reference_infile_path = kwargs.pop("reference_infile")
        candidate_infile_path = kwargs.pop("candidate_infile")
        if reference_infile_path == "-" and candidate_infile_path == "-":
            try:
                raise ArgumentConflictError(
                    "--reference-infile and --candidate-infile may not both be '-'"
                )
            except ArgumentConflictError as exc:
                parser.error(str(exc))

        # Read inputs
        reference_series = read_series(parser, reference_infile_path, allow_stdin=True)
        candidate_series = read_series(parser, candidate_infile_path, allow_stdin=True)

        # Perform operations
        result = get_series_cer(reference_series, candidate_series)

        # Write outputs
        print(f"CER: {result.cer}")
        print(f"Correct: {result.correct}")
        print(f"Substitutions: {result.substitutions}")
        print(f"Insertions: {result.insertions}")
        print(f"Deletions: {result.deletions}")
        print(f"Reference length: {result.reference_length}")


if __name__ == "__main__":
    AnalysisCerCli.main()
