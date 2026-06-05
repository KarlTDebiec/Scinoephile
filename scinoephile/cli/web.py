#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CLI helpers for local web UI arguments."""

from __future__ import annotations

from argparse import _ArgumentGroup  # noqa: PLC2701

from scinoephile.common.argument_parsing import int_arg

__all__ = [
    "WEB_LOCALIZATIONS",
    "add_web_server_arguments",
]

WEB_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "host for the OCR validation web UI": "OCR 校验网页界面的主机",
        "port for the OCR validation web UI": "OCR 校验网页界面的端口",
        "web arguments": "网页参数",
    },
    "zh-hant": {
        "host for the OCR validation web UI": "OCR 驗證網頁介面的主機",
        "port for the OCR validation web UI": "OCR 驗證網頁介面的連接埠",
        "web arguments": "網頁參數",
    },
}
"""Localized text shared by CLIs that expose local web UI arguments."""


def add_web_server_arguments(web_arg_group: _ArgumentGroup):
    """Add standard local web server arguments to an argument group.

    Arguments:
        web_arg_group: group to which web server arguments are added
    """
    web_arg_group.add_argument(
        "--host",
        default="127.0.0.1",
        type=str,
        help="host for the OCR validation web UI",
    )
    web_arg_group.add_argument(
        "--port",
        default=5000,
        type=int_arg(min_value=1),
        help="port for the OCR validation web UI",
    )
