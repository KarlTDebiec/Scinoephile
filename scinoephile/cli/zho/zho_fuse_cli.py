#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for standard Chinese OCR subtitle fusion."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Unpack

from scinoephile.common import CLIKwargs
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
from scinoephile.common.exception import ArgumentConflictError
from scinoephile.core.cli import ScinoephileCliBase, read_series, write_series
from scinoephile.lang.zho import get_zho_cleaned, get_zho_converted, get_zho_ocr_fused
from scinoephile.lang.zho.conversion import (
    SIMPLIFIED_CONFIGS,
    TRADITIONAL_CONFIGS,
    OpenCCConfig,
)
from scinoephile.lang.zho.ocr_fusion import ZhoHantOcrFusionPrompt, get_zho_ocr_fuser
from scinoephile.llms.dual_single.ocr_fusion import OcrFusionProcessor

__all__ = ["ZhoFuseCli"]


class ZhoFuseCli(ScinoephileCliBase):
    """Fuse OCR output from Google Lens and PaddleOCR."""

    localizations = {
        "zh-hans": {
            "command-line interface for standard Chinese OCR subtitle fusion": (
                "标准中文 OCR 字幕融合命令行界面"
            ),
            "Standard Chinese subtitle outfile path (default: stdout)": (
                "标准中文字幕输出文件路径（默认：标准输出）"
            ),
        },
        "zh-hant": {
            "command-line interface for standard Chinese OCR subtitle fusion": (
                "標準中文 OCR 字幕融合命令列介面"
            ),
            "Standard Chinese subtitle outfile path (default: stdout)": (
                "標準中文字幕輸出檔路徑（預設：標準輸出）"
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
            "--lens-infile",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='Standard Chinese subtitles OCRed using Google Lens or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--paddle-infile",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='Standard Chinese subtitles OCRed using PaddleOCR or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--clean",
            action="store_true",
            help="clean both OCR inputs before fusion (default: disabled)",
        )
        arg_groups["operation arguments"].add_argument(
            "--convert",
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
            default=None,
            type=output_file_arg(),
            help="Standard Chinese subtitle outfile path (default: stdout)",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "fuse"

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        # Validate arguments
        parser = kwargs.pop("_parser", cls.argparser())
        lens_infile_path = kwargs.pop("lens_infile")
        paddle_infile_path = kwargs.pop("paddle_infile")
        clean = kwargs.pop("clean")
        convert = kwargs.pop("convert")
        outfile_path: Path | None = kwargs.pop("outfile")
        overwrite = kwargs.pop("overwrite")
        if lens_infile_path == "-" and paddle_infile_path == "-":
            try:
                raise ArgumentConflictError(
                    "--lens-infile and --paddle-infile may not both be '-'"
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
        lens = read_series(parser, lens_infile_path, allow_stdin=True)
        paddle = read_series(parser, paddle_infile_path, allow_stdin=True)

        # Perform operations
        if clean:
            lens = get_zho_cleaned(lens, remove_empty=False)
            paddle = get_zho_cleaned(paddle, remove_empty=False)
        if convert is not None:
            lens = get_zho_converted(lens, convert)
            paddle = get_zho_converted(paddle, convert)

        processor = cls._get_ocr_fuser(convert)
        fused = get_zho_ocr_fused(lens, paddle, processor=processor)

        # Write outputs
        write_series(
            parser, fused, outfile_path if outfile_path is not None else "-", overwrite
        )

    @classmethod
    def _get_ocr_fuser(cls, convert: OpenCCConfig | None) -> OcrFusionProcessor:
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


if __name__ == "__main__":
    ZhoFuseCli.main()
