#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Validation data arguments shared by the OCR commands."""

from __future__ import annotations

from argparse import _ArgumentGroup  # noqa: PLC2701

from scinoephile.common.cli.argument_parsing import output_dir_arg
from scinoephile.core.paths import get_runtime_data_root_path

__all__ = ["OCR_VALIDATION_LOCALIZATIONS", "add_ocr_validation_args"]

OCR_VALIDATION_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "local OCR validation data directory path (default: %(default)s)": (
            "本地 OCR 校验数据目录路径（默认：%(default)s）"
        ),
        "maintainer option: write validation data updates to repo data": (
            "维护者选项：将校验数据更新写入仓库数据"
        ),
    },
    "zh-hant": {
        "local OCR validation data directory path (default: %(default)s)": (
            "本機 OCR 驗證資料目錄路徑（預設：%(default)s）"
        ),
        "maintainer option: write validation data updates to repo data": (
            "維護者選項：將驗證資料更新寫入儲存庫資料"
        ),
    },
}
"""Translations for persistent OCR validation data options."""


def add_ocr_validation_args(operation_args: _ArgumentGroup):
    """Register the shared OCR validation data options.

    Arguments:
        operation_args: argument group for OCR validation settings
    """
    operation_args.add_argument(
        "--dev",
        action="store_true",
        help="maintainer option: write validation data updates to repo data",
    )
    operation_args.add_argument(
        "--validation-data-dir",
        default=get_runtime_data_root_path(create=False) / "ocr_validation",
        dest="validation_data_dir_path",
        metavar="VALIDATION_DATA_DIR",
        type=output_dir_arg(create=False),
        help="local OCR validation data directory path (default: %(default)s)",
    )
