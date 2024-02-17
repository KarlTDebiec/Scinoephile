#  Copyright 2017-2024 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for Scinoephile."""
from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from scinoephile.common import (
    Cli,
    get_arg_groups_by_name,
    input_file_path_arg,
    output_file_path_arg,
)
from scinoephile.core import ScinoephileException, SubtitleSeries


class ScinoephileCli(Cli):
    """Command-line interface for Scinoephile."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser) -> None:
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

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "-bif",
            "--bilingual_infile",
            metavar="FILE",
            type=input_file_path_arg(),
            help="bilingual subtitle infile",
        )
        arg_groups["input arguments"].add_argument(
            "-cif",
            "--chinese_infile",
            dest="hanzi_infile",
            metavar="FILE",
            type=input_file_path_arg(),
            help="Chinese Hanzi subtitle infile",
        )
        arg_groups["input arguments"].add_argument(
            "-eif",
            "--english_infile",
            metavar="FILE",
            type=input_file_path_arg(),
            help="English subtitle infile",
        )

        # Operations
        arg_groups["operation arguments"].add_argument(
            "-m",
            "--merge",
            action="store_true",
            help="merge multi-line subtitles into single lines",
        )
        arg_groups["operation arguments"].add_argument(
            "-s",
            "--simplify",
            action="store_true",
            help="convert traditional Hanzi characters to simplified",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-bof",
            "--bilingual_outfile",
            metavar="FILE",
            type=output_file_path_arg(),
            help="bilingual subtitle outfile",
        )
        arg_groups["output arguments"].add_argument(
            "-cof",
            "--chinese_outfile",
            dest="hanzi_outfile",
            metavar="FILE",
            type=output_file_path_arg(),
            help="Chinese Hanzi subtitle outfile",
        )
        arg_groups["output arguments"].add_argument(
            "-eof",
            "--english_outfile",
            metavar="FILE",
            type=output_file_path_arg(),
            help="English subtitle outfile",
        )
        arg_groups["output arguments"].add_argument(
            "-o",
            "--overwrite",
            action="store_true",
            help="overwrite outfiles if they exist",
        )

    @classmethod
    def main_internal(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments."""

        operations = cls._determine_operations(**kwargs)

    @classmethod
    def run(cls, operations: dict[str, Any]) -> None:
        """Run operations."""
        bilingual = english = hanzi = None
        if "load_bilingual" in operations:
            bilingual = SubtitleSeries.load(operations["load_bilingual"])
        if "load_english" in operations:
            english = SubtitleSeries.load(operations["load_english"])
        if "load_hanzi" in operations:
            hanzi = SubtitleSeries.load(operations["load_hanzi"])

        if "save_bilingual" in operations:
            bilingual.save(operations["save_bilingual"])
        if "save_english" in operations:
            english.save(operations["save_english"])
        if "save_hanzi" in operations:
            hanzi.save(operations["save_hanzi"])

    @classmethod
    def _determine_operations(
        cls,
        bilingual_infile: Path | None = None,
        bilingual_outfile: Path | None = None,
        english_infile: Path | None = None,
        english_outfile: Path | None = None,
        hanzi_infile: Path | None = None,
        hanzi_outfile: Path | None = None,
        merge: bool = False,
        overwrite: bool = False,
        simplify: bool = False,
    ):
        operations = {}

        # Compile input operations
        if not (bilingual_infile or english_infile or hanzi_infile):
            raise ScinoephileException("At least one infile required")
        if bilingual_infile:
            operations["load_bilingual"] = bilingual_infile
        if english_infile:
            operations["load_english"] = english_infile
        if hanzi_infile:
            operations["load_hanzi"] = hanzi_infile

        # Compile output operations
        if not (bilingual_outfile or english_outfile or hanzi_outfile):
            raise ScinoephileException("At least one outfile required")
        if bilingual_outfile:
            if bilingual_outfile.exists() and not overwrite:
                raise ScinoephileException(f"{bilingual_outfile} already exists")
            operations["save_bilingual"] = bilingual_outfile
        if english_outfile:
            if english_outfile.exists() and not overwrite:
                raise ScinoephileException(f"{english_outfile} already exists")
            operations["save_english"] = english_outfile
        if hanzi_outfile:
            if hanzi_outfile.exists() and not overwrite:
                raise ScinoephileException(f"{hanzi_outfile} already exists")
            operations["save_hanzi"] = hanzi_outfile

        # Compile operations
        if merge:
            if not (english_infile and (bilingual_outfile or english_outfile)) and not (
                hanzi_infile and (bilingual_outfile or hanzi_outfile)
            ):
                raise ScinoephileException(
                    "At least one infile and one outfile including the same language "
                    "required for merge"
                )
            if english_infile and (bilingual_outfile or english_outfile):
                operations["merge_english"] = True
            if hanzi_infile and (bilingual_outfile or hanzi_outfile):
                operations["merge_hanzi"] = True
        if simplify:
            if not hanzi_infile:
                raise ScinoephileException("Hanzi infile required for simplify")
            operations["simplify_hanzi"] = True

        # Validate operations
        if "save_bilingual" in operations and "load_bilingual" not in operations:
            if "load_english" not in operations and "load_hanzi" not in operations:
                raise ScinoephileException(
                    "Bilingual outfile requires English and Hanzi infiles"
                )
            operations["sync_bilingual"] = True

        return operations


if __name__ == "__main__":
    ScinoephileCli.main()
