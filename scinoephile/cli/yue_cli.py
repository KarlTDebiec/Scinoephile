#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for 粤文 workflows."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import get_arg_groups_by_name, str_arg
from scinoephile.core.cli.io import read_series, write_series
from scinoephile.core.subtitles import Series
from scinoephile.lang.yue import get_yue_converted, get_yue_romanized
from scinoephile.lang.zho import get_zho_cleaned, get_zho_flattened
from scinoephile.lang.zho.proofreading import (
    ZhoHansProofreadingPrompt,
    ZhoHantProofreadingPrompt,
    get_zho_proofread,
    get_zho_proofreader,
)

from .yue_transcribe_cli import YueTranscribeCli


class YueCli(CommandLineInterface):
    """Command-line interface for 粤文 workflows."""

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

        arg_groups["input arguments"].add_argument(
            "-i",
            "--infile",
            metavar="INFILE",
            default="-",
            type=str,
            help='粤文 subtitle infile path or "-" for stdin',
        )

        arg_groups["operation arguments"].add_argument(
            "--clean",
            action="store_true",
            help="clean subtitles of closed-caption annotations and other anomalies",
        )
        arg_groups["operation arguments"].add_argument(
            "--flatten",
            action="store_true",
            help="flatten multi-line subtitles into single lines",
        )
        arg_groups["operation arguments"].add_argument(
            "--convert",
            action="store_true",
            help="normalize HKSCS private-use characters to Unicode",
        )
        arg_groups["operation arguments"].add_argument(
            "--proofread",
            metavar="SCRIPT",
            nargs="?",
            const="traditional",
            type=str_arg(options=("simplified", "traditional")),
            help=(
                "proofread subtitles using configured LLM workflow"
                " (default: traditional)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--romanize",
            action="store_true",
            help="append Cantonese romanization to subtitles",
        )

        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            metavar="OUTFILE",
            default="-",
            type=str,
            help='粤文 subtitle outfile path or "-" for stdout',
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )

        subparsers = parser.add_subparsers(
            dest="yue_subcommand",
            help="subcommand",
            required=False,
        )
        subcommands = cls.subcommands()
        for name in sorted(subcommands):
            subcommands[name].argparser(subparsers=subparsers)
        parser.set_defaults(_parser=parser)

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        subcommand_name = kwargs.pop("yue_subcommand", None)
        if subcommand_name is not None:
            subcommand_cli_class = cls.subcommands()[subcommand_name]
            subcommand_cli_class._main(**kwargs)
            return

        parser = kwargs.pop("_parser", cls.argparser())
        infile = kwargs.pop("infile")
        outfile = kwargs.pop("outfile")
        clean = kwargs.pop("clean")
        flatten = kwargs.pop("flatten")
        convert = kwargs.pop("convert")
        proofread_script = kwargs.pop("proofread")
        romanize = kwargs.pop("romanize")
        overwrite = kwargs.pop("overwrite")

        if not (clean or flatten or convert or proofread_script or romanize):
            parser.error("At least one operation required")

        series = read_series(parser, infile, allow_stdin=True)
        if clean:
            series = get_zho_cleaned(series)
        if flatten:
            series = get_zho_flattened(series)
        if convert:
            series = cls._get_series_converted(series)
        if proofread_script is not None:
            prompt_cls = cls._get_proofread_prompt_cls(proofread_script)
            proofreader = get_zho_proofreader(prompt_cls=prompt_cls)
            series = get_zho_proofread(series, processor=proofreader)
        if romanize:
            series = get_yue_romanized(series, append=True)
        write_series(parser, series, outfile, overwrite)

    @classmethod
    def _get_proofread_prompt_cls(
        cls, proofread_script: str
    ) -> type[ZhoHansProofreadingPrompt] | type[ZhoHantProofreadingPrompt]:
        """Get the proofreading prompt class for the selected script.

        Arguments:
            proofread_script: script identifier
        Returns:
            proofreading prompt class
        """
        if proofread_script == "traditional":
            return ZhoHantProofreadingPrompt
        return ZhoHansProofreadingPrompt

    @classmethod
    def _get_series_converted(cls, series: Series) -> Series:
        """Normalize HKSCS private-use characters in a subtitle series.

        Arguments:
            series: subtitle series to convert
        Returns:
            converted series
        """
        for event in series:
            event.text = get_yue_converted(event.text)
        return series

    @classmethod
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Names and types of tools wrapped by command-line interface.

        Returns:
            mapping of subcommand names to CLI classes
        """
        return {
            YueTranscribeCli.name(): YueTranscribeCli,
        }


if __name__ == "__main__":
    YueCli.main()
