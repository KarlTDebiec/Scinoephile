#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for 中文 OCR subtitle fusion."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import get_arg_groups_by_name, input_file_arg
from scinoephile.core.cli.io import load_subtitle_series, write_subtitle_series
from scinoephile.lang.zho import get_zho_cleaned, get_zho_converted, get_zho_ocr_fused
from scinoephile.lang.zho.conversion import (
    SIMPLIFIED_CONFIGS,
    TRADITIONAL_CONFIGS,
    OpenCCConfig,
)
from scinoephile.lang.zho.ocr_fusion import ZhoHantOcrFusionPrompt, get_zho_ocr_fuser
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionProcessor


class ZhoFuseCli(CommandLineInterface):
    """Command-line interface for 中文 OCR subtitle fusion."""

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
            "lens_infile",
            metavar="LENS_INFILE",
            type=input_file_arg(),
            help="Google Lens 中文 subtitle infile",
        )
        arg_groups["input arguments"].add_argument(
            "paddle_infile",
            metavar="PADDLE_INFILE",
            type=input_file_arg(),
            help="PaddleOCR 中文 subtitle infile",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--clean",
            action="store_true",
            help="clean both OCR inputs before fusion (default: disabled)",
        )
        arg_groups["operation arguments"].add_argument(
            "--convert",
            metavar="CONFIG",
            nargs="?",
            const=OpenCCConfig.t2s,
            type=OpenCCConfig,
            help=(
                "convert Chinese characters using specified OpenCC configuration"
                " before fusion (value when provided without argument: t2s)"
            ),
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            metavar="OUTFILE",
            default="-",
            type=str,
            help='fused 中文 subtitle outfile path or "-" for stdout',
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
            **kwargs: keyword arguments including lens_infile, paddle_infile, clean,
              convert, outfile, and overwrite
        """
        parser = kwargs.pop("_parser", cls.argparser())
        lens_infile = kwargs.pop("lens_infile")
        paddle_infile = kwargs.pop("paddle_infile")
        clean = kwargs.pop("clean")
        convert = kwargs.pop("convert")
        outfile = kwargs.pop("outfile")
        overwrite = kwargs.pop("overwrite")

        lens = load_subtitle_series(parser, lens_infile)
        paddle = load_subtitle_series(parser, paddle_infile)
        if clean:
            lens = get_zho_cleaned(lens, remove_empty=False)
            paddle = get_zho_cleaned(paddle, remove_empty=False)
        if convert is not None:
            lens = get_zho_converted(lens, convert)
            paddle = get_zho_converted(paddle, convert)

        processor = cls._get_ocr_fuser(convert)
        fused = get_zho_ocr_fused(lens, paddle, processor=processor)
        write_subtitle_series(parser, fused, outfile, overwrite)

    @classmethod
    def _get_ocr_fuser(
        cls,
        convert: OpenCCConfig | None,
    ) -> OcrFusionProcessor:
        """Get OCR fuser for selected conversion output script.

        Arguments:
            convert: OpenCC conversion configuration
        Returns:
            configured OCR fuser
        """
        script = cls._get_script_for_conversion(convert)
        if script == "traditional":
            return get_zho_ocr_fuser(prompt_cls=ZhoHantOcrFusionPrompt)
        return get_zho_ocr_fuser()

    @classmethod
    def _get_script_for_conversion(cls, convert: OpenCCConfig | None) -> str:
        """Get output script implied by conversion configuration.

        If conversion is omitted, script defaults to simplified for OCR fusion prompts.

        Arguments:
            convert: OpenCC conversion configuration
        Returns:
            "simplified" or "traditional"
        """
        if convert in TRADITIONAL_CONFIGS:
            return "traditional"
        if convert in SIMPLIFIED_CONFIGS:
            return "simplified"
        return "simplified"

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "fuse"


if __name__ == "__main__":
    ZhoFuseCli.main()
