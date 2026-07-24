#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for OCR subtitle validation."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.helpers.cache import CACHE_LOCALIZATIONS, add_cache_dir_arg
from scinoephile.cli.helpers.web import (
    WEB_LOCALIZATIONS,
    WebServerArguments,
    add_web_server_args,
)
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    output_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.workflows.ocr_validation import validate_ocr

__all__ = ["OcrValidateCli"]

OCR_VALIDATE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "cache directory for local OCR validation data (default: %(default)s)": (
            "本地 OCR 校验数据的缓存目录（默认：%(default)s）"
        ),
        "command-line interface for OCR subtitle validation": (
            "OCR 字幕校验命令行界面"
        ),
        "launch the local OCR validation web UI": "启动本地 OCR 校验网页界面",
        "OCR image subtitle infile path (directory containing index.html and png "
        "files, or a .sup file)": (
            "OCR 图像字幕输入路径（包含 index.html 和 png 文件的目录，或 .sup 文件）"
        ),
        "overwrite outfile if it exists": "若输出文件已存在则覆盖",
        "validate OCR text against subtitle images": "对照字幕图像校验 OCR 文本",
        "validated subtitle outfile path": "已校验字幕输出文件路径",
        "maintainer option: write validation data updates to repo data": (
            "维护者选项：将校验数据更新写入仓库数据"
        ),
    },
    "zh-hant": {
        "cache directory for local OCR validation data (default: %(default)s)": (
            "本機 OCR 驗證資料的快取目錄（預設：%(default)s）"
        ),
        "command-line interface for OCR subtitle validation": (
            "OCR 字幕驗證命令列介面"
        ),
        "launch the local OCR validation web UI": "啟動本機 OCR 驗證網頁介面",
        "OCR image subtitle infile path (directory containing index.html and png "
        "files, or a .sup file)": (
            "OCR 影像字幕輸入路徑（包含 index.html 和 png 檔案的目錄，或 .sup 檔）"
        ),
        "overwrite outfile if it exists": "若輸出檔已存在則覆寫",
        "validate OCR text against subtitle images": "對照字幕影像驗證 OCR 文字",
        "validated subtitle outfile path": "已驗證字幕輸出檔路徑",
        "maintainer option: write validation data updates to repo data": (
            "維護者選項：將驗證資料更新寫入儲存庫資料"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class OcrValidateCli(ScinoephileCliBase):
    """Validate OCR text against subtitle images."""

    localizations = merge_localizations(
        CACHE_LOCALIZATIONS,
        WEB_LOCALIZATIONS,
        OCR_VALIDATE_LOCALIZATIONS,
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
            "cache arguments",
            "web arguments",
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "-i",
            "--infile",
            dest="infile_path",
            required=True,
            type=Path,
            help=(
                "OCR image subtitle infile path (directory containing index.html and "
                "png files, or a .sup file)"
            ),
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--dev",
            action="store_true",
            help="maintainer option: write validation data updates to repo data",
        )
        add_cache_dir_arg(
            arg_groups["cache arguments"],
            "ocr_validation",
            help_text=(
                "cache directory for local OCR validation data (default: %(default)s)"
            ),
        )

        # Web arguments
        arg_groups["web arguments"].add_argument(
            "--interactive",
            action="store_true",
            help="launch the local OCR validation web UI",
        )
        add_web_server_args(arg_groups["web arguments"])

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            required=True,
            type=output_file_arg(exist_ok=True),
            help="validated subtitle outfile path",
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
        return "validate"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        infile_path: Path,
        interactive: bool,
        dev: bool,
        cache_dir_path: Path,
        web_args: WebServerArguments,
        outfile_path: Path,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if outfile_path.exists() and not overwrite:
            parser.error(f"{outfile_path} already exists")
        if interactive and not infile_path.is_dir():
            parser.error(f"{infile_path} must be a directory when --interactive is set")

        # Perform operations
        try:
            validate_ocr(
                infile_path,
                outfile_path,
                cache_dir_path=cache_dir_path,
                interactive=interactive,
                dev=dev,
                overwrite=overwrite,
                host=web_args.host,
                port=web_args.port,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))


if __name__ == "__main__":
    OcrValidateCli.main()
