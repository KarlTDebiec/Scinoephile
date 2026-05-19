#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for OCR operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common import CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

__all__ = ["OcrCli"]

OCR_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        (
            "Backend commands may require optional OCR dependencies, browser access, "
            "or system OCR executables."
        ): "后端命令可能需要可选 OCR 依赖、浏览器访问或系统 OCR 可执行文件。",
        "Recognize text from image-based subtitles.": "识别图像字幕中的文本。",
    },
    "zh-hant": {
        (
            "Backend commands may require optional OCR dependencies, browser access, "
            "or system OCR executables."
        ): "後端命令可能需要可選 OCR 依賴、瀏覽器存取或系統 OCR 可執行檔。",
        "Recognize text from image-based subtitles.": "識別影像字幕中的文字。",
    },
}
"""Localized help text keyed by locale and English source text."""


class OcrCli(ScinoephileCliBase):
    """Recognize text from image-based subtitles.

    Backend commands may require optional OCR dependencies, browser access, or system
    OCR executables.
    """

    localizations = OCR_LOCALIZATIONS
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="ocr_subcommand_name",
            help="subcommand",
            required=True,
        )
        subcommands = cls.subcommands()
        for name in sorted(subcommands):
            subcommands[name].argparser(subparsers=subparsers)

    @classmethod
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Names and types of tools wrapped by command-line interface.

        Returns:
            mapping of subcommand names to CLI classes
        """
        from .ocr_fuse_cli import OcrFuseCli  # noqa: PLC0415
        from .ocr_lens_cli import OcrLensCli  # noqa: PLC0415
        from .ocr_paddle_cli import OcrPaddleCli  # noqa: PLC0415
        from .ocr_process_cli import OcrProcessCli  # noqa: PLC0415
        from .ocr_tesseract_cli import OcrTesseractCli  # noqa: PLC0415
        from .ocr_validate_cli import OcrValidateCli  # noqa: PLC0415

        return {
            OcrFuseCli.name(): OcrFuseCli,
            OcrLensCli.name(): OcrLensCli,
            OcrPaddleCli.name(): OcrPaddleCli,
            OcrProcessCli.name(): OcrProcessCli,
            OcrTesseractCli.name(): OcrTesseractCli,
            OcrValidateCli.name(): OcrValidateCli,
        }

    @classmethod
    def _main(
        cls,
        *,
        ocr_subcommand_name: str,
        **kwargs: Any,
    ):
        """Execute with provided keyword arguments."""
        cls.subcommands()[ocr_subcommand_name]._main(**kwargs)


if __name__ == "__main__":
    OcrCli.main()
