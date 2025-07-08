#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for Scinoephile."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Any

from scinoephile.common import CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
from scinoephile.core import ScinoephileError, Series
from scinoephile.core.english import get_english_cleaned, get_english_flattened
from scinoephile.core.hanzi import (
    get_hanzi_cleaned,
    get_hanzi_flattened,
    get_hanzi_simplified,
)
from scinoephile.core.synchronization import get_synced_series


class ScinoephileCli(CommandLineInterface):
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
            "--bilingual-infile",
            metavar="FILE",
            type=input_file_arg(),
            help="bilingual subtitle infile",
        )
        arg_groups["input arguments"].add_argument(
            "-cif",
            "--chinese-infile",
            dest="hanzi_infile",
            metavar="FILE",
            type=input_file_arg(),
            help="Chinese Hanzi subtitle infile",
        )
        arg_groups["input arguments"].add_argument(
            "-eif",
            "--english-infile",
            metavar="FILE",
            type=input_file_arg(),
            help="English subtitle infile",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "-c",
            "--clean",
            action="store_true",
            help="clean subtitles of closed-caption annotations and other anomalies",
        )
        arg_groups["operation arguments"].add_argument(
            "-f",
            "--flatten",
            action="store_true",
            help="flatten multi-line subtitles into single lines",
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
            "--bilingual-outfile",
            metavar="FILE",
            type=output_file_arg(),
            help="bilingual subtitle outfile",
        )
        arg_groups["output arguments"].add_argument(
            "-cof",
            "--chinese-outfile",
            dest="hanzi_outfile",
            metavar="FILE",
            type=output_file_arg(),
            help="Chinese Hanzi subtitle outfile",
        )
        arg_groups["output arguments"].add_argument(
            "-eof",
            "--english-outfile",
            metavar="FILE",
            type=output_file_arg(),
            help="English subtitle outfile",
        )
        arg_groups["output arguments"].add_argument(
            "-o",
            "--overwrite",
            action="store_true",
            help="overwrite outfiles if they exist",
        )

    @classmethod
    def run(cls, operations: dict[str, Any]) -> None:
        """Run operations.

        Arguments:
            operations: Operations to be performed, keys are operations and values are
              the arguments to be passed to the corresponding functions, if applicable
        """
        bilingual = english = hanzi = None

        # Input operations
        if "load_bilingual" in operations:
            bilingual = Series.load(operations["load_bilingual"])
        if "load_english" in operations:
            english = Series.load(operations["load_english"])
        if "load_hanzi" in operations:
            hanzi = Series.load(operations["load_hanzi"])

        # Operation operations
        if "clean_hanzi" in operations:
            hanzi = get_hanzi_cleaned(hanzi)
        if "clean_english" in operations:
            english = get_english_cleaned(english)
        if "flatten_english" in operations:
            english = get_english_flattened(english)
        if "flatten_hanzi" in operations:
            hanzi = get_hanzi_flattened(hanzi)
        if "simplify_hanzi" in operations:
            hanzi = get_hanzi_simplified(hanzi)
        if "sync_bilingual" in operations:
            bilingual = get_synced_series(hanzi, english)

        # Output operations
        if "save_bilingual" in operations:
            if bilingual is None:
                raise ScinoephileError(
                    "Bilingual series not loaded and cannot be saved"
                )
            bilingual.save(operations["save_bilingual"])
        if "save_english" in operations:
            if english is None:
                raise ScinoephileError("English series not loaded and cannot be saved")
            english.save(operations["save_english"])
        if "save_hanzi" in operations:
            if hanzi is None:
                raise ScinoephileError("Hanzi series not loaded and cannot be saved")
            hanzi.save(operations["save_hanzi"])

    @classmethod
    def determine_operations(
        cls,
        *,
        bilingual_infile: Path | None = None,
        bilingual_outfile: Path | None = None,
        english_infile: Path | None = None,
        english_outfile: Path | None = None,
        hanzi_infile: Path | None = None,
        hanzi_outfile: Path | None = None,
        clean: bool = False,
        flatten: bool = False,
        overwrite: bool = False,
        simplify: bool = False,
    ) -> dict[str, Any]:
        """Determine operations to be performed based on provided arguments.

        Examples of valid argument combinations and their corresponding actions:

        bif bof eif eof cif cof f   s   Actions
        --- --- --- --- --- --- --- --- ------------------------------------------------
        0   1   1   0   1   0   1   1   load_english, load_hanzi, flatten_english,
                                        flatten_hanzi, simplify_hanzi, sync_bilingual,
                                        save_bilingual
        0   0   1   1   0   0   1   0   load_english, flatten_english, save_english
        0   0   0   0   1   1   1   1   load_hanzi, flatten_hanzi, simplify_hanzi,
                                        save_hanzi

        Arguments:
            bilingual_infile: Bilingual subtitle infile
            bilingual_outfile: Bilingual subtitle outfile
            english_infile: English subtitle infile
            english_outfile: English subtitle outfile
            hanzi_infile: Hanzi subtitle infile
            hanzi_outfile: Hanzi subtitle outfile
            clean: Clean subtitles of closed-caption annotations and other anomalies
            flatten: Flatten multi-line subtitles into single lines
            overwrite: Overwrite outfiles if they exist
            simplify: Convert traditional Hanzi characters to simplified
        Returns:
            dictionary whose keys are operations to be performed and whose values are
            the arguments to be passed to the corresponding functions, if applicable
        """
        operations = {}

        # Compile input operations
        if not (bilingual_infile or english_infile or hanzi_infile):
            cls.argparser().error("At least one infile required")
        if bilingual_infile:
            operations["load_bilingual"] = bilingual_infile
        if english_infile:
            operations["load_english"] = english_infile
        if hanzi_infile:
            operations["load_hanzi"] = hanzi_infile

        # Compile output operations
        if not (bilingual_outfile or english_outfile or hanzi_outfile):
            cls.argparser().error("At least one outfile required")
        if bilingual_outfile:
            if bilingual_outfile.exists() and not overwrite:
                cls.argparser().error(f"{bilingual_outfile} already exists")
            operations["save_bilingual"] = bilingual_outfile
        if english_outfile:
            if english_outfile.exists() and not overwrite:
                cls.argparser().error(f"{english_outfile} already exists")
            operations["save_english"] = english_outfile
        if hanzi_outfile:
            if hanzi_outfile.exists() and not overwrite:
                cls.argparser().error(f"{hanzi_outfile} already exists")
            operations["save_hanzi"] = hanzi_outfile

        # Compile operations
        if clean:
            if hanzi_infile:
                operations["clean_hanzi"] = True
            if english_infile:
                operations["clean_english"] = True
        if flatten:
            if not (english_infile and (bilingual_outfile or english_outfile)) and not (
                hanzi_infile and (bilingual_outfile or hanzi_outfile)
            ):
                cls.argparser().error(
                    "At least one infile and one outfile including the same language "
                    "required for flatten"
                )
            if english_infile and (bilingual_outfile or english_outfile):
                operations["flatten_english"] = True
            if hanzi_infile and (bilingual_outfile or hanzi_outfile):
                operations["flatten_hanzi"] = True
        if simplify:
            if not hanzi_infile or bilingual_infile:
                cls.argparser().error("Hanzi infile required for simplify")
            operations["simplify_hanzi"] = True
        if "save_bilingual" in operations and "load_bilingual" not in operations:
            if "load_english" not in operations and "load_hanzi" not in operations:
                cls.argparser().error(
                    "Bilingual outfile requires English and Hanzi infiles"
                )
            operations["sync_bilingual"] = True
            operations["flatten_english"] = True
            operations["flatten_hanzi"] = True

        return operations

    @classmethod
    def _main(cls, **kwargs: Any) -> None:
        """Execute with provided keyword arguments.

        Arguments:
            kwargs: Keyword arguments
        """
        operations = cls.determine_operations(**kwargs)
        cls.run(operations)


if __name__ == "__main__":
    ScinoephileCli.main()
