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
    "ListOpenCCConfigsAction",
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

OPENCC_CONFIG_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "s2t": "简体中文转繁体中文。",
        "t2s": "繁体中文转简体中文。",
        "s2tw": "简体中文转繁体中文（台湾标准）。",
        "tw2s": "繁体中文（台湾标准）转简体中文。",
        "s2hk": "简体中文转繁体中文（香港标准）。",
        "hk2s": "繁体中文（香港标准）转简体中文。",
        "s2twp": "简体中文转繁体中文（台湾标准，包含台湾惯用词）。",
        "tw2sp": "繁体中文（台湾标准）转简体中文（包含大陆惯用词）。",
        "t2tw": "繁体中文（OpenCC 标准）转台湾标准。",
        "hk2t": "繁体中文（香港标准）转繁体中文。",
        "t2hk": "繁体中文（OpenCC 标准）转香港标准。",
        "t2jp": "繁体汉字（旧字体）转新字体（日本汉字）。",
        "jp2t": "新字体（日本汉字）转繁体汉字（旧字体）。",
        "tw2t": "繁体中文（台湾标准）转繁体中文。",
    },
    "zh-hant": {
        "s2t": "簡體中文轉繁體中文。",
        "t2s": "繁體中文轉簡體中文。",
        "s2tw": "簡體中文轉繁體中文（臺灣標準）。",
        "tw2s": "繁體中文（臺灣標準）轉簡體中文。",
        "s2hk": "簡體中文轉繁體中文（香港標準）。",
        "hk2s": "繁體中文（香港標準）轉簡體中文。",
        "s2twp": "簡體中文轉繁體中文（臺灣標準，包含臺灣慣用詞）。",
        "tw2sp": "繁體中文（臺灣標準）轉簡體中文（包含大陸慣用詞）。",
        "t2tw": "繁體中文（OpenCC 標準）轉臺灣標準。",
        "hk2t": "繁體中文（香港標準）轉繁體中文。",
        "t2hk": "繁體中文（OpenCC 標準）轉香港標準。",
        "t2jp": "繁體漢字（舊字體）轉新字體（日語漢字）。",
        "jp2t": "新字體（日語漢字）轉繁體漢字（舊字體）。",
        "tw2t": "繁體中文（臺灣標準）轉繁體中文。",
    },
}
"""Localized OpenCC configuration descriptions keyed by locale and config code."""


def get_opencc_config_description(config: OpenCCConfig, locale_name: str = "en") -> str:
    """Get localized description for an OpenCC configuration.

    Arguments:
        config: OpenCC configuration
        locale_name: locale name to use for description lookup
    Returns:
        localized description when available, otherwise English description
    """
    return OPENCC_CONFIG_LOCALIZATIONS.get(locale_name, {}).get(
        config.code, config.description
    )


class ListOpenCCConfigsAction(Action):
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
            f"  {config.value:<5} {get_opencc_config_description(config, locale_name)}"
            for config in OpenCCConfig
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
        action=ListOpenCCConfigsAction,
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
