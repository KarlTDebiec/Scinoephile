#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for OCR subtitle fusion."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.helpers.cache import (
    CACHE_LOCALIZATIONS,
    CacheArguments,
    add_cache_args,
)
from scinoephile.cli.helpers.conversion import (
    CONVERSION_LOCALIZATIONS,
    add_opencc_convert_auto_argument,
)
from scinoephile.cli.helpers.io import read_series, write_series
from scinoephile.cli.helpers.llms import (
    LLM_LOCALIZATIONS,
    LlmArguments,
    add_llm_provider_args,
    add_llm_test_case_json_arg,
    read_llm_additional_context,
)
from scinoephile.common.argument_parsing import (
    enum_arg,
    enum_metavar,
    get_arg_groups_by_name,
    input_file_arg,
    output_file_arg,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.lang.zho.script.conversion import (
    SIMPLIFIED_CONFIGS,
    TRADITIONAL_CONFIGS,
    OpenCCConfig,
    get_zho_converted,
)
from scinoephile.llms.providers.registry import get_provider
from scinoephile.workflows.clean import clean_series
from scinoephile.workflows.ocr_fusion import fuse_ocr_series

__all__ = ["OcrFuseCli"]

OCR_FUSE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "Chinese subtitles OCRed using PaddleOCR or '-' for stdin": (
            "使用 PaddleOCR OCR 的中文字幕，或用 '-' 表示标准输入"
        ),
        "clean OCR subtitle inputs before fusing": "在融合前清理 OCR 字幕输入",
        "command-line interface for OCR subtitle fusion": "OCR 字幕融合命令行界面",
        "English subtitles OCRed using Tesseract or '-' for stdin": (
            "使用 Tesseract OCR 的英文字幕，或用 '-' 表示标准输入"
        ),
        "fuse OCR output for a selected language": "融合所选语言的 OCR 输出",
        "fused subtitle outfile path (default: stdout)": (
            "融合后字幕输出文件路径（默认：标准输出）"
        ),
        "language of the OCR text to fuse": "要融合的 OCR 文本语言",
        "OCR subtitles OCRed using Google Lens or '-' for stdin": (
            "使用 Google Lens OCR 的字幕，或用 '-' 表示标准输入"
        ),
    },
    "zh-hant": {
        "Chinese subtitles OCRed using PaddleOCR or '-' for stdin": (
            "使用 PaddleOCR OCR 的中文字幕，或用 '-' 表示標準輸入"
        ),
        "clean OCR subtitle inputs before fusing": "在融合前清理 OCR 字幕輸入",
        "command-line interface for OCR subtitle fusion": "OCR 字幕融合命令列介面",
        "English subtitles OCRed using Tesseract or '-' for stdin": (
            "使用 Tesseract OCR 的英文字幕，或用 '-' 表示標準輸入"
        ),
        "fuse OCR output for a selected language": "融合所選語言的 OCR 輸出",
        "fused subtitle outfile path (default: stdout)": (
            "融合後字幕輸出檔路徑（預設：標準輸出）"
        ),
        "language of the OCR text to fuse": "要融合的 OCR 文字語言",
        "OCR subtitles OCRed using Google Lens or '-' for stdin": (
            "使用 Google Lens OCR 的字幕，或用 '-' 表示標準輸入"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class OcrFuseCli(ScinoephileCliBase):
    """Fuse OCR output for a selected language."""

    localizations = merge_localizations(
        CONVERSION_LOCALIZATIONS,
        CACHE_LOCALIZATIONS,
        LLM_LOCALIZATIONS,
        OCR_FUSE_LOCALIZATIONS,
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
            "llm arguments",
            "cache arguments",
            "output arguments",
            "additional help",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
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
            type=input_file_arg(allow_stdin=True),
            help="English subtitles OCRed using Tesseract or '-' for stdin",
        )
        arg_groups["input arguments"].add_argument(
            "--paddle-infile",
            dest="paddle_infile_path",
            type=input_file_arg(allow_stdin=True),
            help="Chinese subtitles OCRed using PaddleOCR or '-' for stdin",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--language",
            required=True,
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help="language of the OCR text to fuse",
        )
        arg_groups["operation arguments"].add_argument(
            "--clean",
            action="store_true",
            help="clean OCR subtitle inputs before fusing",
        )
        add_opencc_convert_auto_argument(
            arg_groups["operation arguments"], arg_groups["additional help"]
        )
        add_llm_provider_args(
            arg_groups["llm arguments"], arg_groups["additional help"]
        )
        add_llm_test_case_json_arg(arg_groups["llm arguments"])

        # Cache arguments
        add_cache_args(arg_groups["cache arguments"])

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            type=output_file_arg(exist_ok=True),
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
    def _main(  # noqa: PLR0912, PLR0915
        cls,
        *,
        _parser: ArgumentParser | None = None,
        language: Language,
        lens_infile_path: Path | str,
        tesseract_infile_path: Path | str | None,
        paddle_infile_path: Path | str | None,
        clean: bool,
        convert: OpenCCConfig | bool | None,
        llm_args: LlmArguments,
        cache_args: CacheArguments,
        json_path: Path | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")
        if language is Language.eng:
            if tesseract_infile_path is None:
                parser.error("--tesseract-infile is required when --language is eng")
            if paddle_infile_path is not None:
                parser.error("--paddle-infile may only be used with Chinese subtitles")
            if convert is not None:
                parser.error("--convert may only be used with Chinese subtitles")
            secondary_infile_path = tesseract_infile_path
        else:
            if tesseract_infile_path is not None:
                parser.error(
                    "--tesseract-infile may only be used when --language is eng"
                )
            if paddle_infile_path is None:
                parser.error("--paddle-infile is required with Chinese subtitles")
            secondary_infile_path = paddle_infile_path
        if lens_infile_path == "-" and secondary_infile_path == "-":
            parser.error("OCR input files may not both be '-'")
        resolved_convert: OpenCCConfig | None = None
        if isinstance(convert, OpenCCConfig):
            resolved_convert = convert
        elif convert:
            if language.script == "Hans":
                resolved_convert = OpenCCConfig.s2t
            else:
                resolved_convert = OpenCCConfig.t2s

        # Read inputs
        lens = read_series(parser, lens_infile_path, allow_stdin=True)
        secondary = read_series(parser, secondary_infile_path, allow_stdin=True)

        # Clean and convert inputs
        if clean:
            lens = clean_series(lens, language=language, remove_empty=False)
            secondary = clean_series(secondary, language=language, remove_empty=False)
        fusion_language = language
        if resolved_convert is not None:
            lens = get_zho_converted(lens, resolved_convert)
            secondary = get_zho_converted(secondary, resolved_convert)
            if language.is_cantonese:
                if resolved_convert in SIMPLIFIED_CONFIGS:
                    fusion_language = Language.yue_hans
                elif resolved_convert in TRADITIONAL_CONFIGS:
                    fusion_language = Language.yue_hant
            elif resolved_convert in SIMPLIFIED_CONFIGS:
                fusion_language = Language.zho_hans
            elif resolved_convert in TRADITIONAL_CONFIGS:
                fusion_language = Language.zho_hant

        # Fuse inputs
        try:
            fused = fuse_ocr_series(
                lens,
                secondary,
                language=fusion_language,
                provider=get_provider(
                    llm_args.provider_name,
                    model=llm_args.model_name,
                ),
                additional_context=read_llm_additional_context(
                    parser,
                    llm_args.additional_context_file_path,
                ),
                cache_dir_path=cache_args.dir_path / "llm",
                overwrite_cache=cache_args.overwrite,
                test_case_path=json_path,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write output
        write_series(
            parser, fused, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    OcrFuseCli.main()
