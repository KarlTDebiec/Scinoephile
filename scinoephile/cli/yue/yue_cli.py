#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for 粤文 subtitle operations."""

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
from scinoephile.lang.yue import get_yue_romanized
from scinoephile.lang.zho import get_zho_cleaned, get_zho_converted, get_zho_flattened
from scinoephile.lang.zho.conversion import (
    SIMPLIFIED_CONFIGS,
    TRADITIONAL_CONFIGS,
    OpenCCConfig,
)
from scinoephile.lang.zho.proofreading import (
    ZhoHansProofreadingPrompt,
    ZhoHantProofreadingPrompt,
    get_zho_proofread,
    get_zho_proofreader,
)

from .yue_review_cli import YueReviewCli
from .yue_transcribe_cli import YueTranscribeCli

__all__ = ["YueCli"]


class YueCli(CommandLineInterface):
    """Modify Written Cantonese (粤文) subtitles."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)
        arg_groups = get_arg_groups_by_name(
            parser,
            "positional arguments",
            "input arguments",
            "operation arguments",
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "-i",
            "--infile",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='粤文 subtitle infile path or "-" for stdin',
        )

        # Operation arguments
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
            nargs="?",
            const=OpenCCConfig.t2s,
            type=OpenCCConfig,
            help=(
                "convert Chinese characters using specified OpenCC configuration"
                " (default: t2s)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--proofread",
            nargs="?",
            const="traditional",
            type=str_arg(options=("simplified", "traditional")),
            help="proofread subtitles using LLM (default: traditional)",
        )
        arg_groups["operation arguments"].add_argument(
            "--romanize",
            action="store_true",
            help="append Cantonese romanization to subtitles",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            default=None,
            type=output_file_arg(),
            help="粤文 subtitle outfile path (default: stdout)",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )

        # Subcommands
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
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Names and types of tools wrapped by command-line interface.

        Returns:
            mapping of subcommand names to CLI classes
        """
        return {
            YueReviewCli.name(): YueReviewCli,
            YueTranscribeCli.name(): YueTranscribeCli,
        }

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        # Validate arguments
        parser = kwargs.pop("_parser", cls.argparser())
        subcommand_name = kwargs.pop("yue_subcommand", None)
        if subcommand_name is not None:
            subcommand_cli_class = cls.subcommands()[subcommand_name]
            subcommand_cli_class._main(**kwargs)
            return

        infile_path = kwargs.pop("infile")
        outfile_path: Path | None = kwargs.pop("outfile")
        clean = kwargs.pop("clean")
        flatten = kwargs.pop("flatten")
        convert = kwargs.pop("convert")
        proofread_script = kwargs.pop("proofread")
        romanize = kwargs.pop("romanize")
        overwrite = kwargs.pop("overwrite")

        if not (clean or flatten or convert or proofread_script or romanize):
            parser.error("At least one operation required")
        if overwrite and outfile_path is None:
            try:
                raise ArgumentConflictError(
                    "--overwrite may only be used with --outfile"
                )
            except ArgumentConflictError as exc:
                parser.error(str(exc))
        cls._validate_proofread_script(parser, convert, proofread_script)

        # Read input
        series = read_series(parser, infile_path, allow_stdin=True)

        # Perform operations
        if clean:
            series = get_zho_cleaned(series)
        if convert is not None:
            series = get_zho_converted(series, convert)
        if flatten:
            series = get_zho_flattened(series)
        if proofread_script is not None:
            prompt_cls = cls._get_proofread_prompt_cls(proofread_script)
            proofreader = get_zho_proofreader(prompt_cls=prompt_cls)
            series = get_zho_proofread(series, processor=proofreader)
        if romanize:
            series = get_yue_romanized(series, append=True)

        # Write output
        write_series(
            parser, series, outfile_path if outfile_path is not None else "-", overwrite
        )

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
    def _get_script_for_conversion(cls, convert: OpenCCConfig) -> str | None:
        """Get the script implied by a conversion configuration.

        Arguments:
            convert: OpenCC configuration
        Returns:
            "simplified", "traditional", or None if not implied
        """
        if convert in SIMPLIFIED_CONFIGS:
            return "simplified"
        if convert in TRADITIONAL_CONFIGS:
            return "traditional"
        return None

    @classmethod
    def _validate_proofread_script(
        cls,
        parser: ArgumentParser,
        convert: OpenCCConfig | None,
        proofread_script: str | None,
    ):
        """Validate that proofread script matches conversion output.

        Arguments:
            parser: argument parser for error reporting
            convert: OpenCC configuration
            proofread_script: script identifier for proofreading
        """
        if proofread_script is None or convert is None:
            return
        convert_script = cls._get_script_for_conversion(convert)
        if convert_script is None:
            return
        if convert_script != proofread_script:
            parser.error(
                "Proofread script must match post-conversion script: "
                f"{convert} yields {convert_script}"
            )


if __name__ == "__main__":
    YueCli.main()
