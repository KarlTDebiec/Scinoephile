#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for OCR subtitle fusion."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import ClassVar

from scinoephile.cli.conversion import (
    add_opencc_convert_argument,
    merge_conversion_localizations,
)
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
    str_arg,
)
from scinoephile.core.cli import ScinoephileCliBase, read_series, write_series
from scinoephile.lang.eng.cleaning import get_eng_cleaned
from scinoephile.lang.eng.ocr_fusion import get_eng_ocr_fused
from scinoephile.lang.zho.cleaning import get_zho_cleaned
from scinoephile.lang.zho.ocr_fusion import (
    OcrFusionPromptZhoHant,
    get_zho_ocr_fused,
    get_zho_ocr_fuser,
)
from scinoephile.lang.zho.script.conversion import (
    SIMPLIFIED_CONFIGS,
    TRADITIONAL_CONFIGS,
    OpenCCConfig,
    get_zho_converted,
)
from scinoephile.llms.dual_1_to_1.ocr_fusion import OcrFusionProcessor

__all__ = ["OcrFuseCli"]


class OcrFuseCli(ScinoephileCliBase):
    """Fuse OCR output for a selected language."""

    localizations: ClassVar[dict[str, dict[str, str]]] = merge_conversion_localizations(
        {
            "zh-hans": {
                "clean OCR subtitle inputs before fusing": (
                    "在融合前清理 OCR 字幕输入"
                ),
                "command-line interface for OCR subtitle fusion": (
                    "OCR 字幕融合命令行界面"
                ),
                "English subtitles OCRed using Tesseract or '-' for stdin": (
                    "使用 Tesseract OCR 的英文字幕，或用 '-' 表示标准输入"
                ),
                "fuse OCR output for a selected language": ("融合所选语言的 OCR 输出"),
                "language of the OCR text to fuse (eng or zho)": (
                    "要融合的 OCR 文本语言（eng 或 zho）"
                ),
                "OCR subtitles OCRed using Google Lens or '-' for stdin": (
                    "使用 Google Lens OCR 的字幕，或用 '-' 表示标准输入"
                ),
                "Standard Chinese subtitles OCRed using PaddleOCR or '-' for stdin": (
                    "使用 PaddleOCR OCR 的标准中文字幕，或用 '-' 表示标准输入"
                ),
                "fused subtitle outfile path (default: stdout)": (
                    "融合后字幕输出文件路径（默认：标准输出）"
                ),
            },
            "zh-hant": {
                "clean OCR subtitle inputs before fusing": (
                    "在融合前清理 OCR 字幕輸入"
                ),
                "command-line interface for OCR subtitle fusion": (
                    "OCR 字幕融合命令列介面"
                ),
                "English subtitles OCRed using Tesseract or '-' for stdin": (
                    "使用 Tesseract OCR 的英文字幕，或用 '-' 表示標準輸入"
                ),
                "fuse OCR output for a selected language": ("融合所選語言的 OCR 輸出"),
                "language of the OCR text to fuse (eng or zho)": (
                    "要融合的 OCR 文字語言（eng 或 zho）"
                ),
                "OCR subtitles OCRed using Google Lens or '-' for stdin": (
                    "使用 Google Lens OCR 的字幕，或用 '-' 表示標準輸入"
                ),
                "Standard Chinese subtitles OCRed using PaddleOCR or '-' for stdin": (
                    "使用 PaddleOCR OCR 的標準中文字幕，或用 '-' 表示標準輸入"
                ),
                "fused subtitle outfile path (default: stdout)": (
                    "融合後字幕輸出檔路徑（預設：標準輸出）"
                ),
            },
        }
    )
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
            "additional help",
            optional_arguments_name="additional arguments",
        )

        arg_groups["input arguments"].add_argument(
            "--lens-infile",
            dest="lens_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help="OCR subtitles OCRed using Google Lens or '-' for stdin",
        )
        arg_groups["input arguments"].add_argument(
            "--tesseract-infile",
            dest="tesseract_infile_path",
            default=None,
            type=input_file_arg(allow_stdin=True),
            help="English subtitles OCRed using Tesseract or '-' for stdin",
        )
        arg_groups["input arguments"].add_argument(
            "--paddle-infile",
            dest="paddle_infile_path",
            default=None,
            type=input_file_arg(allow_stdin=True),
            help="Standard Chinese subtitles OCRed using PaddleOCR or '-' for stdin",
        )

        arg_groups["operation arguments"].add_argument(
            "--language",
            required=True,
            type=str_arg(options=("eng", "zho")),
            help="language of the OCR text to fuse (eng or zho)",
        )
        arg_groups["operation arguments"].add_argument(
            "--clean",
            action="store_true",
            default=False,
            help="clean OCR subtitle inputs before fusing",
        )
        add_opencc_convert_argument(
            arg_groups["operation arguments"], arg_groups["additional help"]
        )

        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            default=None,
            dest="outfile_path",
            type=output_file_arg(),
            help="fused subtitle outfile path (default: stdout)",
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
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        language: str,
        lens_infile_path: Path | str,
        tesseract_infile_path: Path | str | None,
        paddle_infile_path: Path | str | None,
        clean: bool,
        convert: OpenCCConfig | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")

        if language == "eng":
            cls._main_eng(
                parser=parser,
                lens_infile_path=lens_infile_path,
                tesseract_infile_path=tesseract_infile_path,
                paddle_infile_path=paddle_infile_path,
                clean=clean,
                convert=convert,
                outfile_path=outfile_path,
                overwrite=overwrite,
            )
        else:
            cls._main_zho(
                parser=parser,
                lens_infile_path=lens_infile_path,
                tesseract_infile_path=tesseract_infile_path,
                paddle_infile_path=paddle_infile_path,
                clean=clean,
                convert=convert,
                outfile_path=outfile_path,
                overwrite=overwrite,
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
            return get_zho_ocr_fuser(prompt_cls=OcrFusionPromptZhoHant)
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
    def _main_eng(
        cls,
        *,
        parser: ArgumentParser,
        lens_infile_path: Path | str,
        tesseract_infile_path: Path | str | None,
        paddle_infile_path: Path | str | None,
        clean: bool,
        convert: OpenCCConfig | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute English OCR fusion.

        Arguments:
            parser: active argument parser
            lens_infile_path: Google Lens OCR subtitle path
            tesseract_infile_path: Tesseract OCR subtitle path
            paddle_infile_path: PaddleOCR subtitle path, if provided
            clean: whether to clean inputs before fusion
            convert: OpenCC conversion configuration, if provided
            outfile_path: output subtitle path
            overwrite: whether to overwrite an existing output file
        """
        if tesseract_infile_path is None:
            parser.error("--tesseract-infile is required when --language is eng")
        if paddle_infile_path is not None:
            parser.error("--paddle-infile may only be used when --language is zho")
        if convert is not None:
            parser.error("--convert may only be used when --language is zho")
        if lens_infile_path == "-" and tesseract_infile_path == "-":
            parser.error("--lens-infile and --tesseract-infile may not both be '-'")

        lens = read_series(parser, lens_infile_path, allow_stdin=True)
        tesseract = read_series(parser, tesseract_infile_path, allow_stdin=True)

        if clean:
            lens = get_eng_cleaned(lens, remove_empty=False)
            tesseract = get_eng_cleaned(tesseract, remove_empty=False)
        fused = get_eng_ocr_fused(lens, tesseract)

        write_series(
            parser, fused, outfile_path if outfile_path is not None else "-", overwrite
        )

    @classmethod
    def _main_zho(
        cls,
        *,
        parser: ArgumentParser,
        lens_infile_path: Path | str,
        tesseract_infile_path: Path | str | None,
        paddle_infile_path: Path | str | None,
        clean: bool,
        convert: OpenCCConfig | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute standard Chinese OCR fusion.

        Arguments:
            parser: active argument parser
            lens_infile_path: Google Lens OCR subtitle path
            tesseract_infile_path: Tesseract subtitle path, if provided
            paddle_infile_path: PaddleOCR OCR subtitle path
            clean: whether to clean inputs before fusion
            convert: OpenCC conversion configuration, if provided
            outfile_path: output subtitle path
            overwrite: whether to overwrite an existing output file
        """
        if tesseract_infile_path is not None:
            parser.error("--tesseract-infile may only be used when --language is eng")
        if paddle_infile_path is None:
            parser.error("--paddle-infile is required when --language is zho")
        if lens_infile_path == "-" and paddle_infile_path == "-":
            parser.error("--lens-infile and --paddle-infile may not both be '-'")

        lens = read_series(parser, lens_infile_path, allow_stdin=True)
        paddle = read_series(parser, paddle_infile_path, allow_stdin=True)

        if clean:
            lens = get_zho_cleaned(lens, remove_empty=False)
            paddle = get_zho_cleaned(paddle, remove_empty=False)
        if convert is not None:
            lens = get_zho_converted(lens, convert)
            paddle = get_zho_converted(paddle, convert)

        processor = cls._get_ocr_fuser(convert)
        fused = get_zho_ocr_fused(lens, paddle, processor=processor)

        write_series(
            parser, fused, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    OcrFuseCli.main()
