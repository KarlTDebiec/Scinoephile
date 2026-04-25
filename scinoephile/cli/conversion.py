#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CLI helpers for Chinese text conversion arguments."""

from __future__ import annotations

import sys
from argparse import Action, ArgumentParser, Namespace, _ArgumentGroup  # noqa: PLC2701

from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.lang.zho.conversion import OpenCCConfig

__all__ = [
    "CONVERSION_LOCALIZATIONS",
    "add_opencc_convert_argument",
    "merge_conversion_localizations",
    "opencc_config_arg",
]

CONVERSION_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "additional help": "附加帮助",
        "Available OpenCC configurations:": "可用 OpenCC 配置：",
        "convert Chinese characters using specified OpenCC configuration. Use "
        "--list-opencc-configs to show available codes.": (
            "使用指定 OpenCC 配置转换中文字符。使用 "
            "--list-opencc-configs 查看可用代码。"
        ),
        "list available OpenCC configurations and exit": ("列出可用 OpenCC 配置并退出"),
    },
    "zh-hant": {
        "additional help": "附加說明",
        "Available OpenCC configurations:": "可用 OpenCC 設定：",
        "convert Chinese characters using specified OpenCC configuration. Use "
        "--list-opencc-configs to show available codes.": (
            "使用指定 OpenCC 設定轉換中文字符。使用 "
            "--list-opencc-configs 查看可用代碼。"
        ),
        "list available OpenCC configurations and exit": ("列出可用 OpenCC 設定並結束"),
    },
}
"""Localized text shared by CLIs that expose OpenCC conversion arguments."""


class _ListOpenCCConfigsAction(Action):
    """Print available OpenCC configurations and exit."""

    def __init__(self, option_strings, dest, **kwargs):
        """Initialize.

        Arguments:
            option_strings: option strings
            dest: argparse destination name
            **kwargs: additional keyword arguments
        """
        kwargs.setdefault("nargs", 0)
        super().__init__(option_strings=option_strings, dest=dest, **kwargs)

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values,
        option_string: str | None = None,
    ):
        """Handle the action.

        Arguments:
            parser: active argument parser
            namespace: parsed namespace
            values: parsed argument value
            option_string: option string used
        """
        del namespace, values, option_string
        locale_name = ScinoephileCliBase.locale_name
        heading = CONVERSION_LOCALIZATIONS.get(locale_name, {}).get(
            "Available OpenCC configurations:",
            "Available OpenCC configurations:",
        )
        lines = [heading]
        lines.extend(
            f"  {config.value:<5} {config.description}" for config in OpenCCConfig
        )
        parser._print_message("\n".join(lines) + "\n", sys.stdout)  # noqa: SLF001
        parser.exit(0)


def add_opencc_convert_argument(
    operation_arg_group: _ArgumentGroup,
    additional_help_arg_group: _ArgumentGroup,
):
    """Add standard OpenCC conversion and help arguments to argument groups.

    Arguments:
        operation_arg_group: group to which to add `--convert`
        additional_help_arg_group: group to which to add help-only OpenCC arguments
    """
    operation_arg_group.add_argument(
        "--convert",
        type=opencc_config_arg,
        help=(
            "convert Chinese characters using specified OpenCC configuration. "
            "Use --list-opencc-configs to show available codes."
        ),
    )
    additional_help_arg_group.add_argument(
        "--list-opencc-configs",
        action=_ListOpenCCConfigsAction,
        help="list available OpenCC configurations and exit",
    )


def merge_conversion_localizations(
    localizations: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    """Merge shared conversion localizations with CLI-specific localizations.

    Arguments:
        localizations: CLI-specific localizations
    Returns:
        merged localizations
    """
    merged: dict[str, dict[str, str]] = {
        locale_name: dict(locale_text)
        for locale_name, locale_text in CONVERSION_LOCALIZATIONS.items()
    }
    for locale_name, locale_text in localizations.items():
        merged.setdefault(locale_name, {})
        merged[locale_name].update(locale_text)
    return merged


def opencc_config_arg(value: str) -> OpenCCConfig:
    """Validate an OpenCC configuration CLI argument.

    Arguments:
        value: raw CLI argument value
    Returns:
        parsed OpenCC configuration
    """
    return OpenCCConfig(value)
