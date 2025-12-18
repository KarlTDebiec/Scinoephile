#  Copyright 2017-2025 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for Scinoephile."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Any, override

from scinoephile.common import CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.lang.eng import get_eng_cleaned, get_eng_flattened
from scinoephile.lang.zho import get_zho_cleaned, get_zho_converted, get_zho_flattened
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.multilang import get_synced_series


class ScinoephileCli(CommandLineInterface):
    """Command-line interface for Scinoephile."""

    @classmethod
    @override
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
            metavar="FILE",
            type=input_file_arg(),
            help="Chinese subtitle infile",
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
            metavar="FILE",
            type=output_file_arg(),
            help="Chinese subtitle outfile",
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
    def run(cls, operations: dict[str, Any]):
        """Run operations.

        Arguments:
            operations: Operations to be performed, keys are operations and values are
              the arguments to be passed to the corresponding functions, if applicable
        """
        bilingual = english = chinese = None

        # Input operations
        if "load_bilingual" in operations:
            bilingual = Series.load(operations["load_bilingual"])
        if "load_english" in operations:
            english = Series.load(operations["load_english"])
        if "load_chinese" in operations:
            chinese = Series.load(operations["load_chinese"])

        # Operation operations
        if "clean_chinese" in operations:
            chinese = get_zho_cleaned(chinese)
        if "clean_english" in operations:
            english = get_eng_cleaned(english)
        if "flatten_english" in operations:
            english = get_eng_flattened(english)
        if "flatten_chinese" in operations:
            chinese = get_zho_flattened(chinese)
        if "convert_chinese" in operations:
            chinese = get_zho_converted(chinese, operations["convert_chinese"])
        if "sync_bilingual" in operations:
            bilingual = get_synced_series(chinese, english)

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
        if "save_chinese" in operations:
            if chinese is None:
                raise ScinoephileError("Chinese series not loaded and cannot be saved")
            chinese.save(operations["save_chinese"])

    @classmethod
    def determine_operations(
        cls,
        *,
        bilingual_infile: Path | None = None,
        bilingual_outfile: Path | None = None,
        english_infile: Path | None = None,
        english_outfile: Path | None = None,
        chinese_infile: Path | None = None,
        chinese_outfile: Path | None = None,
        clean: bool = False,
        flatten: bool = False,
        overwrite: bool = False,
        convert: OpenCCConfig | None = None,
    ) -> dict[str, Any]:
        """Determine operations to be performed based on provided arguments.

        Examples of valid argument combinations and their corresponding actions:

        bif bof eif eof cif cof f   c   Actions
        --- --- --- --- --- --- --- --- ------------------------------------------------
        0   1   1   0   1   0   1   1   load_english, load_chinese, flatten_english,
                                        flatten_chinese, convert_chinese,
                                        sync_bilingual, save_bilingual
        0   0   1   1   0   0   1   0   load_english, flatten_english, save_english
        0   0   0   0   1   1   1   1   load_chinese, flatten_chinese, convert_chinese,
                                        save_chinese

        Arguments:
            bilingual_infile: Bilingual subtitle infile
            bilingual_outfile: Bilingual subtitle outfile
            english_infile: English subtitle infile
            english_outfile: English subtitle outfile
            chinese_infile: Chinese subtitle infile
            chinese_outfile: Chinese subtitle outfile
            clean: Clean subtitles of closed-caption annotations and other anomalies
            flatten: Flatten multi-line subtitles into single lines
            overwrite: Overwrite outfiles if they exist
            convert: OpenCC configuration for Chinese conversion
        Returns:
            dictionary whose keys are operations to be performed and whose values are
            the arguments to be passed to the corresponding functions, if applicable
        """
        operations = {}

        # Compile input operations
        if not (bilingual_infile or english_infile or chinese_infile):
            cls.argparser().error("At least one infile required")
        if bilingual_infile:
            operations["load_bilingual"] = bilingual_infile
        if english_infile:
            operations["load_english"] = english_infile
        if chinese_infile:
            operations["load_chinese"] = chinese_infile

        # Compile output operations
        if not (bilingual_outfile or english_outfile or chinese_outfile):
            cls.argparser().error("At least one outfile required")
        if bilingual_outfile:
            if bilingual_outfile.exists() and not overwrite:
                cls.argparser().error(f"{bilingual_outfile} already exists")
            operations["save_bilingual"] = bilingual_outfile
        if english_outfile:
            if english_outfile.exists() and not overwrite:
                cls.argparser().error(f"{english_outfile} already exists")
            operations["save_english"] = english_outfile
        if chinese_outfile:
            if chinese_outfile.exists() and not overwrite:
                cls.argparser().error(f"{chinese_outfile} already exists")
            operations["save_chinese"] = chinese_outfile

        # Compile operations
        if clean:
            if chinese_infile:
                operations["clean_chinese"] = True
            if english_infile:
                operations["clean_english"] = True
        if flatten:
            if not (english_infile and (bilingual_outfile or english_outfile)) and not (
                chinese_infile and (bilingual_outfile or chinese_outfile)
            ):
                cls.argparser().error(
                    "At least one infile and one outfile including the same language "
                    "required for flatten"
                )
            if english_infile and (bilingual_outfile or english_outfile):
                operations["flatten_english"] = True
            if chinese_infile and (bilingual_outfile or chinese_outfile):
                operations["flatten_chinese"] = True
        if convert is not None:
            if not chinese_infile or bilingual_infile:
                cls.argparser().error("Chinese infile required for convert")
            operations["convert_chinese"] = convert
        if "save_bilingual" in operations and "load_bilingual" not in operations:
            if "load_english" not in operations and "load_chinese" not in operations:
                cls.argparser().error(
                    "Bilingual outfile requires English and Chinese infiles"
                )
            operations["sync_bilingual"] = True
            operations["flatten_english"] = True
            operations["flatten_chinese"] = True

        return operations

    @classmethod
    @override
    def _main(cls, **kwargs: Any):
        """Execute with provided keyword arguments.

        Arguments:
            kwargs: Keyword arguments
        """
        operations = cls.determine_operations(**kwargs)
        cls.run(operations)


if __name__ == "__main__":
    ScinoephileCli.main()
