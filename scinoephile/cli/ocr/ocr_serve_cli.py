#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for the OCR validation editor."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.helpers.web import (
    WEB_LOCALIZATIONS,
    WebServerArguments,
    add_web_server_args,
)
from scinoephile.common.cli.argument_parsing import (
    get_arg_groups_by_name,
    input_dir_arg,
    output_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.workflows.ocr_validation import serve_ocr_validation

from .validation_args import OCR_VALIDATION_LOCALIZATIONS, add_ocr_validation_args

__all__ = ["OcrServeCli"]

_OCR_SERVE_LOCALIZATIONS = {
    "zh-hans": {
        "start the local OCR validation editor": "启动本地 OCR 校验编辑器",
        "OCR image subtitle directory containing index.html and PNG files": (
            "包含 index.html 和 PNG 文件的 OCR 图像字幕目录"
        ),
        "SRT output rebuilt from the image index on startup": (
            "启动时从图像索引重新生成的 SRT 输出"
        ),
    },
    "zh-hant": {
        "start the local OCR validation editor": "啟動本機 OCR 驗證編輯器",
        "OCR image subtitle directory containing index.html and PNG files": (
            "包含 index.html 和 PNG 檔案的 OCR 影像字幕目錄"
        ),
        "SRT output rebuilt from the image index on startup": (
            "啟動時從影像索引重新產生的 SRT 輸出"
        ),
    },
}


class OcrServeCli(ScinoephileCliBase):
    """Start the local OCR validation editor."""

    localizations = merge_localizations(
        WEB_LOCALIZATIONS, OCR_VALIDATION_LOCALIZATIONS, _OCR_SERVE_LOCALIZATIONS
    )
    """Translated command description and argument help."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add OCR image directory, validation data, and server arguments.

        Arguments:
            parser: parser to configure
        """
        super().add_arguments_to_argparser(parser)
        groups = get_arg_groups_by_name(
            parser,
            "input arguments",
            "operation arguments",
            "web arguments",
            "output arguments",
            optional_arguments_name="additional arguments",
        )
        groups["input arguments"].add_argument(
            "-i",
            "--infile",
            dest="infile_path",
            required=True,
            type=input_dir_arg(),
            help="OCR image subtitle directory containing index.html and PNG files",
        )
        add_ocr_validation_args(groups["operation arguments"])
        add_web_server_args(groups["web arguments"])
        groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            required=True,
            type=output_file_arg(exist_ok=True, create=False),
            help="SRT output rebuilt from the image index on startup",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Return the name of the OCR editor subcommand.

        Returns:
            subcommand name
        """
        return "serve"

    @classmethod
    def _main(
        cls,
        *,
        infile_path: Path,
        outfile_path: Path,
        validation_data_dir_path: Path,
        dev: bool,
        web_args: WebServerArguments,
        _parser: ArgumentParser | None = None,
    ):
        """Open the OCR image directory in the local validation editor.

        Arguments:
            infile_path: directory containing OCR text and subtitle images
            outfile_path: SRT output updated by the editor
            validation_data_dir_path: local OCR validation data directory
            dev: whether to write validation data updates to the repository
            web_args: web server configuration
            _parser: optional parser for reporting errors
        """
        parser = _parser or cls.argparser()
        try:
            serve_ocr_validation(
                infile_path,
                outfile_path,
                validation_data_dir_path=validation_data_dir_path,
                dev=dev,
                host=web_args.host,
                port=web_args.port,
                title=web_args.title,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))


if __name__ == "__main__":
    OcrServeCli.main()
