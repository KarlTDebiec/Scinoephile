#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Scinoephile-specific CLI base class with localization support."""

from __future__ import annotations

import locale
import re
from argparse import ArgumentParser
from inspect import cleandoc
from os import getenv
from typing import ClassVar

from scinoephile.common import CommandLineInterface

from .constants import DEFAULT_CLI_LOCALE, LOCALE_ALIASES


class ScinoephileCliBase(CommandLineInterface):
    """Scinoephile CLI base class."""

    locale_name = DEFAULT_CLI_LOCALE
    localizations: ClassVar[dict[str, dict[str, str]]] = {
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
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def get_localized_text(cls) -> dict[str, dict[str, str]]:
        """Get class-localized text mapping.

        Returns:
            locale to source/target text mapping
        """
        if cls is ScinoephileCliBase:
            return cls.localizations
        merged: dict[str, dict[str, str]] = {
            locale_name: dict(locale_text)
            for locale_name, locale_text in ScinoephileCliBase.localizations.items()
        }
        for locale_name, locale_text in cls.localizations.items():
            merged.setdefault(locale_name, {})
            merged[locale_name].update(locale_text)
        return merged

    @classmethod
    def _canonicalize_text(cls, text: str) -> str:
        """Canonicalize text for translation lookup.

        Arguments:
            text: source text
        Returns:
            canonicalized source text
        """
        return re.sub(r"\s+", " ", text.strip()).rstrip(".").casefold()

    @classmethod
    def _resolve_locale(cls) -> str:
        """Resolve active locale from environment and system settings.

        Returns:
            supported locale code
        """

        def normalize(locale_name: str | None) -> str | None:
            """Normalize locale names to supported values."""
            if locale_name is None:
                return None
            compact = locale_name.strip().replace(".", "_").split("@")[0].lower()
            mapped = LOCALE_ALIASES.get(compact)
            if mapped is not None:
                return mapped
            compact = compact.replace("-", "_")
            return LOCALE_ALIASES.get(compact)

        for variable_name in ("LC_ALL", "LC_MESSAGES", "LANG"):
            resolved = normalize(getenv(variable_name))
            if resolved is not None:
                return resolved
        system_locale_name, _ = locale.getlocale()
        resolved = normalize(system_locale_name)
        if resolved is not None:
            return resolved
        return DEFAULT_CLI_LOCALE

    @classmethod
    def translate_text(cls, text: str | None) -> str:
        """Translate text for active locale.

        Arguments:
            text: source text
        Returns:
            translated text
        """
        if text is None:
            return ""
        active_locale_name = ScinoephileCliBase.locale_name
        if active_locale_name == DEFAULT_CLI_LOCALE:
            return text

        canonical_text = cls._canonicalize_text(text)
        localized_text = cls.get_localized_text().get(active_locale_name, {})
        translations = {
            cls._canonicalize_text(source_text): target_text
            for source_text, target_text in localized_text.items()
        }
        translated = translations.get(canonical_text, canonical_text)
        if translated == canonical_text:
            return text
        return translated

    @classmethod
    def description(cls) -> str:
        """Long description of this tool displayed below usage."""
        if cls.__doc__ is None:
            return ""
        return "\n\n".join(
            cls.translate_text(paragraph)
            for paragraph in cleandoc(cls.__doc__).split("\n\n")
        )

    @classmethod
    def localize_parser(cls, parser: ArgumentParser):
        """Apply localization to parser text.

        Arguments:
            parser: parser to localize
        """
        parser.description = cls.translate_text(parser.description)
        if parser.epilog is not None:
            parser.epilog = cls.translate_text(parser.epilog)
        if parser.usage is not None:
            parser.usage = cls.translate_text(parser.usage)
        for action_group in parser._action_groups:  # noqa pylint: disable=protected-access
            action_group.title = cls.translate_text(action_group.title)
            action_group.description = cls.translate_text(action_group.description)
            for action in action_group._group_actions:  # noqa pylint: disable=protected-access
                if isinstance(action.help, str):
                    action.help = cls.translate_text(action.help)

    @classmethod
    def argparser(cls, *, subparsers=None) -> ArgumentParser:
        """Construct localized argument parser."""
        parser = super().argparser(subparsers=subparsers)
        cls.localize_parser(parser)
        return parser

    @classmethod
    def main(cls):
        """Execute with locale detection."""
        ScinoephileCliBase.locale_name = cls._resolve_locale()
        super().main()
