#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared CLI localization helpers."""

from __future__ import annotations

__all__ = [
    "BASE_CLI_LOCALIZATIONS",
    "merge_localizations",
]

BASE_CLI_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "additional arguments": "附加参数",
        "at least one operation required": "至少需要一种操作",
        "disable verbose output": "禁用详细输出",
        "enable verbose output, may be specified more than once": (
            "启用详细输出，可重复指定"
        ),
        "input arguments": "输入参数",
        "log to file (default: 'YYYY-MM-DD_hh-mm-ss.log')": (
            "写入日志文件（默认：'YYYY-MM-DD_hh-mm-ss.log'）"
        ),
        "operation arguments": "操作参数",
        "options": "选项",
        "overwrite outfile if it exists": "若输出文件已存在则覆盖",
        "output arguments": "输出参数",
        "positional arguments": "位置参数",
        "show this help message and exit": "显示此帮助信息并退出",
        "subcommand": "子命令",
        "usage": "用法",
    },
    "zh-hant": {
        "additional arguments": "附加參數",
        "at least one operation required": "至少需要一種操作",
        "disable verbose output": "停用詳細輸出",
        "enable verbose output, may be specified more than once": (
            "啟用詳細輸出，可重複指定"
        ),
        "input arguments": "輸入參數",
        "log to file (default: 'YYYY-MM-DD_hh-mm-ss.log')": (
            "寫入日誌檔（預設：'YYYY-MM-DD_hh-mm-ss.log'）"
        ),
        "operation arguments": "操作參數",
        "options": "選項",
        "overwrite outfile if it exists": "若輸出檔已存在則覆寫",
        "output arguments": "輸出參數",
        "positional arguments": "位置參數",
        "show this help message and exit": "顯示此說明訊息並結束",
        "subcommand": "子命令",
        "usage": "用法",
    },
}
"""Localized text shared by all Scinoephile CLI classes."""


def merge_localizations(
    *localizations_by_locale: dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    """Merge localization maps.

    Later maps override earlier maps for matching locale/source-text pairs.

    Arguments:
        *localizations_by_locale: localization maps to merge
    Returns:
        merged localization map
    """
    merged: dict[str, dict[str, str]] = {}
    for localizations in localizations_by_locale:
        for locale_name, locale_text in localizations.items():
            merged.setdefault(locale_name, {})
            merged[locale_name].update(locale_text)
    return merged
