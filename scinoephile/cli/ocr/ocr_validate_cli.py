#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for OCR subtitle validation."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.common import DirectoryNotFoundError
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    int_arg,
    output_file_arg,
    str_arg,
)
from scinoephile.common.exceptions import NotAFileError
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.image.subtitles import ImageSeries
from scinoephile.lang.eng.ocr_validation import validate_eng_ocr
from scinoephile.lang.zho.ocr_validation import validate_zho_ocr
from scinoephile.web.ocr_validation import OcrValidationSession, create_app

__all__ = ["OcrValidateCli"]

OCR_VALIDATE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for OCR subtitle validation": (
            "OCR 字幕校验命令行界面"
        ),
        "host for the OCR validation web UI": "OCR 校验网页界面的主机",
        "launch the local OCR validation web UI": "启动本地 OCR 校验网页界面",
        "language of the OCR text to validate (eng or zho)": (
            "要校验的 OCR 文本语言（eng 或 zho）"
        ),
        "OCR image subtitle infile path (directory containing index.html and png "
        "files, or a .sup file)": (
            "OCR 图像字幕输入路径（包含 index.html 和 png 文件的目录，或 .sup 文件）"
        ),
        "overwrite outfile if it exists": "若输出文件已存在则覆盖",
        "port for the OCR validation web UI": "OCR 校验网页界面的端口",
        "validate OCR text against subtitle images": "对照字幕图像校验 OCR 文本",
        "validated subtitle outfile path": "已校验字幕输出文件路径",
        "maintainer option: write validation data updates to repo data": (
            "维护者选项：将校验数据更新写入仓库数据"
        ),
        "web arguments": "网页参数",
    },
    "zh-hant": {
        "command-line interface for OCR subtitle validation": (
            "OCR 字幕驗證命令列介面"
        ),
        "host for the OCR validation web UI": "OCR 驗證網頁介面的主機",
        "launch the local OCR validation web UI": "啟動本機 OCR 驗證網頁介面",
        "language of the OCR text to validate (eng or zho)": (
            "要驗證的 OCR 文字語言（eng 或 zho）"
        ),
        "OCR image subtitle infile path (directory containing index.html and png "
        "files, or a .sup file)": (
            "OCR 影像字幕輸入路徑（包含 index.html 和 png 檔案的目錄，或 .sup 檔）"
        ),
        "overwrite outfile if it exists": "若輸出檔已存在則覆寫",
        "port for the OCR validation web UI": "OCR 驗證網頁介面的連接埠",
        "validate OCR text against subtitle images": "對照字幕影像驗證 OCR 文字",
        "validated subtitle outfile path": "已驗證字幕輸出檔路徑",
        "maintainer option: write validation data updates to repo data": (
            "維護者選項：將驗證資料更新寫入儲存庫資料"
        ),
        "web arguments": "網頁參數",
    },
}
"""Localized help text keyed by locale and English source text."""


class OcrValidateCli(ScinoephileCliBase):
    """Validate OCR text against subtitle images."""

    localizations = OCR_VALIDATE_LOCALIZATIONS
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
            "--language",
            required=True,
            metavar="{eng,zho}",
            type=str_arg(options=("eng", "zho")),
            help="language of the OCR text to validate (eng or zho)",
        )
        arg_groups["operation arguments"].add_argument(
            "--dev",
            action="store_true",
            help="maintainer option: write validation data updates to repo data",
        )

        # Web arguments
        arg_groups["web arguments"].add_argument(
            "--interactive",
            action="store_true",
            help="launch the local OCR validation web UI",
        )
        arg_groups["web arguments"].add_argument(
            "--host",
            default="127.0.0.1",
            type=str,
            help="host for the OCR validation web UI",
        )
        arg_groups["web arguments"].add_argument(
            "--port",
            default=5000,
            type=int_arg(min_value=1),
            help="port for the OCR validation web UI",
        )

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
        language: str,
        interactive: bool,
        dev: bool,
        host: str,
        port: int,
        outfile_path: Path,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        if outfile_path.exists() and not overwrite:
            parser.error(f"{outfile_path} already exists")

        if interactive:
            if not infile_path.is_dir():
                parser.error(
                    f"{infile_path} must be a directory when --interactive is set"
                )
            if not (infile_path / "index.html").is_file():
                parser.error(
                    f"{infile_path} must contain index.html when --interactive is set"
                )
            session = OcrValidationSession.from_dir_path(
                infile_path,
                outfile_path=outfile_path,
                dev=dev,
            )
            create_app(session).run(host=host, port=port)
            return

        try:
            series = ImageSeries.load(infile_path)
        except (
            DirectoryNotFoundError,
            FileNotFoundError,
            NotADirectoryError,
            NotAFileError,
            ScinoephileError,
            ValueError,
        ) as exc:
            parser.error(str(exc))

        if language == "eng":
            validated = validate_eng_ocr(
                series,
                dev=dev,
            )
        else:
            validated = validate_zho_ocr(
                series,
                dev=dev,
            )

        validated.save(outfile_path, format_="srt", exist_ok=True)


if __name__ == "__main__":
    OcrValidateCli.main()
