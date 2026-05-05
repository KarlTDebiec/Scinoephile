#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for timewarping subtitle series."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from scinoephile.common.exceptions import ArgumentConflictError
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase, read_series, write_series
from scinoephile.core.timing import get_series_timewarped

__all__ = ["TimewarpCli"]


class TimewarpCli(ScinoephileCliBase):
    """Shift and stretch the timings of one subtitle series to match another."""

    localizations = {
        "zh-hans": {
            "shift and stretch the timings of one subtitle series to match another": (
                "平移并拉伸一个字幕序列的时间轴以匹配另一个序列"
            ),
        },
        "zh-hant": {
            "shift and stretch the timings of one subtitle series to match another": (
                "平移並拉伸一個字幕序列的時間軸以匹配另一個序列"
            ),
        },
    }
    """Localized help text keyed by locale and English source text."""

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
            dest="anchor_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='subtitle infile used as anchor timing reference or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--mobile-infile",
            dest="mobile_infile_path",
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
            dest="outfile_path",
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
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        anchor_infile_path: Path | str,
        mobile_infile_path: Path | str,
        one_start_idx: int | None,
        one_end_idx: int | None,
        two_start_idx: int | None,
        two_end_idx: int | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
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
