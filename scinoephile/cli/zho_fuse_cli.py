#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for 中文 OCR subtitle fusion."""

from __future__ import annotations

from argparse import ArgumentParser
from sys import stdout
from typing import Unpack

from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import get_arg_groups_by_name, input_file_arg
from scinoephile.common.validation import val_output_path
from scinoephile.core.subtitles import Series
from scinoephile.lang.zho import get_zho_cleaned, get_zho_converted, get_zho_ocr_fused
from scinoephile.lang.zho.conversion import OpenCCConfig
from scinoephile.lang.zho.ocr_fusion import ZhoHantOcrFusionPrompt, get_zho_ocr_fuser
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionProcessor


class ZhoFuseCli(CommandLineInterface):
    """Command-line interface for 中文 OCR subtitle fusion."""

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
            metavar="lens-infile",
            type=input_file_arg(),
            help="Google Lens 中文 subtitle infile",
        )
        arg_groups["input arguments"].add_argument(
            "paddle_infile",
            metavar="paddle-infile",
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
            metavar="FILE",
            default="-",
            type=str,
            help="fused 中文 subtitle outfile (default: stdout)",
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

        lens = Series.load(lens_infile)
        paddle = Series.load(paddle_infile)
        if clean:
            lens = get_zho_cleaned(lens, remove_empty=False)
            paddle = get_zho_cleaned(paddle, remove_empty=False)
        if convert is not None:
            lens = get_zho_converted(lens, convert)
            paddle = get_zho_converted(paddle, convert)

        processor = cls._get_ocr_fuser(convert)
        fused = get_zho_ocr_fused(lens, paddle, processor=processor)
        cls._write_series(parser, fused, outfile, overwrite)

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
        if convert in cls._traditional_configs:
            return "traditional"
        if convert in cls._simplified_configs:
            return "simplified"
        return "simplified"

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
            parser: argument parser for error reporting
            series: series to write
            outfile: output file path or "-" for stdout
            overwrite: whether to overwrite an existing file
        """
        if outfile == "-":
            stdout.write(series.to_string(format_="srt"))
            return
        output_path = val_output_path(outfile, exist_ok=True)
        if output_path.exists() and not overwrite:
            parser.error(f"{output_path} already exists")
        series.save(output_path)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "fuse"


if __name__ == "__main__":
    ZhoFuseCli.main()
