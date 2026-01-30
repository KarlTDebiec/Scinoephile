#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for 中文 subtitle operations."""

from __future__ import annotations

from argparse import ArgumentParser
from sys import stdin, stdout
from typing import Unpack

from scinoephile.common import CommandLineInterface
from scinoephile.common.argument_parsing import get_arg_groups_by_name, str_arg
from scinoephile.common.command_line_interface import CLIKwargs
from scinoephile.common.validation import val_input_path, val_output_path
from scinoephile.core.subtitles import Series
from scinoephile.lang.zho import get_zho_cleaned, get_zho_converted, get_zho_flattened
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.lang.zho.proofreading import (
    ZhoHansProofreadingPrompt,
    ZhoHantProofreadingPrompt,
    get_zho_proofread,
    get_zho_proofreader,
)


class ZhoCli(CommandLineInterface):
    """Command-line interface for 中文 subtitle operations."""

    _simplified_configs = {
        OpenCCConfig.t2s,
        OpenCCConfig.tw2s,
        OpenCCConfig.hk2s,
        OpenCCConfig.tw2sp,
    }
    _traditional_configs = {
        OpenCCConfig.s2t,
        OpenCCConfig.s2tw,
        OpenCCConfig.s2hk,
        OpenCCConfig.s2twp,
        OpenCCConfig.t2tw,
        OpenCCConfig.hk2t,
        OpenCCConfig.t2hk,
        OpenCCConfig.tw2t,
        OpenCCConfig.t2jp,
        OpenCCConfig.jp2t,
    }

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
            "-i",
            "--infile",
            metavar="FILE",
            default="-",
            type=str,
            help="中文 subtitle infile (default: stdin)",
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
            metavar="CONFIG",
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
            metavar="SCRIPT",
            nargs="?",
            const="simplified",
            type=str_arg(options=("simplified", "traditional")),
            help=(
                "proofread subtitles using configured LLM workflow"
                " (default: simplified)"
            ),
        )
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            metavar="FILE",
            default="-",
            type=str,
            help="中文 subtitle outfile (default: stdout)",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: Keyword arguments
        """
        parser = kwargs.pop("_parser", cls.argparser())
        infile = kwargs.pop("infile")
        outfile = kwargs.pop("outfile")
        clean = kwargs.pop("clean")
        flatten = kwargs.pop("flatten")
        convert = kwargs.pop("convert")
        proofread_script = kwargs.pop("proofread")
        overwrite = kwargs.pop("overwrite")

        if not (clean or flatten or convert or proofread_script):
            parser.error("At least one operation required")
        cls._validate_proofread_script(parser, convert, proofread_script)

        series = cls._load_series(infile)
        if clean:
            series = get_zho_cleaned(series)
        if convert is not None:
            series = get_zho_converted(series, convert)
        if proofread_script is not None:
            prompt_cls = cls._get_proofread_prompt_cls(proofread_script)
            proofreader = get_zho_proofreader(prompt_cls=prompt_cls)
            series = get_zho_proofread(series, processor=proofreader)
        if flatten:
            series = get_zho_flattened(series)
        cls._write_series(parser, series, outfile, overwrite)

    @classmethod
    def _get_proofread_prompt_cls(
        cls, proofread_script: str
    ) -> type[ZhoHansProofreadingPrompt] | type[ZhoHantProofreadingPrompt]:
        """Get the proofreading prompt class for the selected script.

        Arguments:
            proofread_script: Script identifier
        Returns:
            Proofreading prompt class
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
        if convert in cls._simplified_configs:
            return "simplified"
        if convert in cls._traditional_configs:
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
            parser: Argument parser for error reporting
            convert: OpenCC configuration
            proofread_script: Script identifier for proofreading
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

    @classmethod
    def _load_series(cls, infile: str) -> Series:
        """Load a Series from a file path or stdin.

        Arguments:
            infile: Input file path or "-" for stdin
        Returns:
            loaded Series
        """
        if infile == "-":
            return Series.from_string(stdin.read(), format_="srt")
        input_path = val_input_path(infile)
        return Series.load(input_path)

    @classmethod
    def _write_series(
        cls,
        parser: ArgumentParser,
        series: Series,
        outfile: str,
        overwrite: bool,
    ):
        """Write a Series to a file path or stdout.

        Arguments:
            parser: Argument parser for error reporting
            series: Series to write
            outfile: Output file path or "-" for stdout
            overwrite: Whether to overwrite an existing file
        """
        if outfile == "-":
            stdout.write(series.to_string(format_="srt"))
            return
        output_path = val_output_path(outfile, exist_ok=True)
        if output_path.exists() and not overwrite:
            parser.error(f"{output_path} already exists")
        series.save(output_path)


if __name__ == "__main__":
    ZhoCli.main()
