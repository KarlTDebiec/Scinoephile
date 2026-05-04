#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for synchronizing subtitle series."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.common.argument_parsing import (
    float_arg,
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from scinoephile.common.exception import ArgumentConflictError
from scinoephile.core.cli import ScinoephileCliBase, read_series, write_series
from scinoephile.core.synchronization import get_synced_series

__all__ = ["SyncCli"]


class SyncCli(ScinoephileCliBase):
    """Combine two series into the top and bottom of a synchronized series."""

    localizations = {
        "zh-hans": {
            "combine two series into the top and bottom of a synchronized series": (
                "将两个序列合并为上下行同步字幕"
            ),
        },
        "zh-hant": {
            "combine two series into the top and bottom of a synchronized series": (
                "將兩個序列合併為上下行同步字幕"
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
            "--top-infile",
            dest="top_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='subtitle infile for top line or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--bottom-infile",
            dest="bottom_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='subtitle infile for bottom line or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--sync-cutoff",
            default=0.16,
            type=float_arg(min_value=0.0, max_value=1.0),
            help="initial overlap cutoff used to form sync groups (default: 0.16)",
        )
        arg_groups["operation arguments"].add_argument(
            "--pause-length",
            default=3000,
            type=int_arg(min_value=1),
            help=(
                "pause length in milliseconds used to split subtitle blocks "
                "(default: 3000)"
            ),
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            default=None,
            dest="outfile_path",
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
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        top_infile_path: Path | str,
        bottom_infile_path: Path | str,
        sync_cutoff: float,
        pause_length: int,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if top_infile_path == "-" and bottom_infile_path == "-":
            try:
                raise ArgumentConflictError(
                    "--top-infile and --bottom-infile may not both be '-'"
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
        top = read_series(parser, top_infile_path, allow_stdin=True)
        bottom = read_series(parser, bottom_infile_path, allow_stdin=True)

        # Perform operations
        synced = get_synced_series(
            top,
            bottom,
            sync_cutoff=sync_cutoff,
            pause_length=pause_length,
        )

        # Write outputs
        write_series(
            parser, synced, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    SyncCli.main()
