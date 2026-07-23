#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CLI helpers for local web UI arguments."""

from __future__ import annotations

from argparse import _ArgumentGroup  # noqa: PLC2701
from dataclasses import dataclass

from scinoephile.common.argument_parsing import int_arg

from .argument_bundle_field_action import ArgumentBundleFieldAction

__all__ = [
    "WEB_LOCALIZATIONS",
    "WebServerArguments",
    "add_web_server_args",
]

WEB_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "host for the local web server": "本地网页服务器的主机",
        "port for the local web server": "本地网页服务器的端口",
        "web arguments": "网页参数",
    },
    "zh-hant": {
        "host for the local web server": "本機網頁伺服器的主機",
        "port for the local web server": "本機網頁伺服器的連接埠",
        "web arguments": "網頁參數",
    },
}
"""Localized text shared by CLIs that expose local web UI arguments."""


@dataclass(frozen=True)
class WebServerArguments:
    """Parsed local web server CLI arguments."""

    host: str = "127.0.0.1"
    """Host for the local web server."""
    port: int = 5000
    """Port for the local web server."""


def add_web_server_args(web_arg_group: _ArgumentGroup):
    """Add standard local web server arguments to an argument group.

    Arguments:
        web_arg_group: group to which web server arguments are added
    """
    web_arg_group.add_argument(
        "--host",
        action=ArgumentBundleFieldAction,
        bundle_type=WebServerArguments,
        dest="web_args",
        field_name="host",
        metavar="HOST",
        type=str,
        help="host for the local web server",
    )
    web_arg_group.add_argument(
        "--port",
        action=ArgumentBundleFieldAction,
        bundle_type=WebServerArguments,
        dest="web_args",
        field_name="port",
        metavar="PORT",
        type=int_arg(min_value=1, max_value=65535),
        help="port for the local web server",
    )
