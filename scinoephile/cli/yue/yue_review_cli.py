#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for 粤文 review against 中文."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
    str_arg,
)
from scinoephile.common.exception import ArgumentConflictError
from scinoephile.core.cli import read_series, write_series
from scinoephile.multilang.yue_zho import (
    get_yue_proofread_vs_zho,
    get_yue_reviewed_vs_zho,
)

__all__ = ["YueReviewCli"]


class YueReviewCli(CommandLineInterface):
    """Review 粤文 subtitles against 中文 subtitles."""

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
            "--yue-infile",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='target 粤文 subtitle infile path or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--zho-infile",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help=('reference 中文 subtitle infile path or "-" for stdin'),
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--mode",
            default="block",
            type=str_arg(options=("block", "line")),
            help=(
                "review mode (default: block): "
                "block=block-by-block review, line=line-by-line proofreading"
            ),
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            default=None,
            type=output_file_arg(),
            help="reviewed 粤文 subtitle outfile path (default: stdout)",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "review"

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        # Validate arguments
        parser = kwargs.pop("_parser", cls.argparser())
        yue_infile_path = kwargs.pop("yue_infile")
        zho_infile_path = kwargs.pop("zho_infile")
        mode = kwargs.pop("mode")
        outfile_path: Path | None = kwargs.pop("outfile")
        overwrite = kwargs.pop("overwrite")
        if yue_infile_path == "-" and zho_infile_path == "-":
            try:
                raise ArgumentConflictError(
                    "--yue-infile and --zho-infile may not both be '-'"
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
        yuewen = read_series(parser, yue_infile_path, allow_stdin=True)
        zhongwen = read_series(parser, zho_infile_path, allow_stdin=True)

        # Perform operations
        if mode == "line":
            reviewed = get_yue_proofread_vs_zho(yuewen=yuewen, zhongwen=zhongwen)
        else:
            reviewed = get_yue_reviewed_vs_zho(yuewen=yuewen, zhongwen=zhongwen)

        # Write output
        write_series(
            parser,
            reviewed,
            outfile_path if outfile_path is not None else "-",
            overwrite,
        )


if __name__ == "__main__":
    YueReviewCli.main()
