#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for English/中文 synchronization."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common import CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
from scinoephile.core.subtitles import Series
from scinoephile.core.synchronization import get_synced_series
from scinoephile.lang.eng import get_eng_cleaned, get_eng_flattened
from scinoephile.lang.zho import get_zho_cleaned, get_zho_converted, get_zho_flattened
from scinoephile.lang.zho.conversion import OpenCCConfig


class EngZhoSyncCli(CommandLineInterface):
    """Command-line interface for synchronizing English and 中文 subtitles."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: Nascent argument parser
        """
        super().add_arguments_to_argparser(parser)
        arg_groups = get_arg_groups_by_name(
            parser,
            "input arguments",
            "operation arguments",
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        arg_groups["input arguments"].add_argument(
            "--eng-infile",
            metavar="FILE",
            required=True,
            type=input_file_arg(),
            help="English subtitle infile",
        )
        arg_groups["input arguments"].add_argument(
            "--zho-infile",
            metavar="FILE",
            required=True,
            type=input_file_arg(),
            help="中文 subtitle infile",
        )
        arg_groups["operation arguments"].add_argument(
            "--clean",
            action="store_true",
            help="clean subtitles of closed-caption annotations and other anomalies",
        )
        arg_groups["operation arguments"].add_argument(
            "--convert",
            metavar="CONFIG",
            nargs="?",
            const=OpenCCConfig.t2s,
            default=None,
            type=OpenCCConfig,
            help=(
                "convert Chinese characters using specified OpenCC configuration"
                " (default: t2s)"
            ),
        )
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            metavar="FILE",
            required=True,
            type=output_file_arg(exist_ok=True),
            help="bilingual subtitle outfile",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )

    @classmethod
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: Keyword arguments
        """
        eng_infile = kwargs.pop("eng_infile")
        zho_infile = kwargs.pop("zho_infile")
        outfile = kwargs.pop("outfile")
        clean = kwargs.pop("clean")
        convert = kwargs.pop("convert")
        overwrite = kwargs.pop("overwrite")

        if outfile.exists() and not overwrite:
            cls.argparser().error(f"{outfile} already exists")

        eng = Series.load(eng_infile)
        zho = Series.load(zho_infile)

        if clean:
            eng = get_eng_cleaned(eng)
            zho = get_zho_cleaned(zho)
        if convert is not None:
            zho = get_zho_converted(zho, convert)

        eng = get_eng_flattened(eng)
        zho = get_zho_flattened(zho)

        bilingual = get_synced_series(zho, eng)
        bilingual.save(outfile)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser."""
        return "sync"


if __name__ == "__main__":
    EngZhoSyncCli.main()
