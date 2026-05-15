#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""CLI helpers for LLM provider arguments."""

from __future__ import annotations

import sys
from argparse import (  # noqa: PLC2701
    SUPPRESS,
    Action,
    ArgumentParser,
    ArgumentTypeError,
    Namespace,
    _ArgumentGroup,
)
from typing import Any

from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.llms.providers.registry import (
    get_default_provider_name,
    get_provider_description,
    get_provider_names,
)

__all__ = [
    "LLM_LOCALIZATIONS",
    "add_llm_provider_arguments",
    "llm_provider_name_arg",
]

LLM_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "additional help": "附加帮助",
        "Available LLM providers:": "可用 LLM 提供商：",
        "LLM model identifier override": "LLM 模型标识符覆盖值",
        "LLM provider to use (default: %(default)s). Use --list-llm-providers "
        "to show available providers.": (
            "要使用的 LLM 提供商（默认：%(default)s）。使用 "
            "--list-llm-providers 查看可用提供商。"
        ),
        "list available LLM providers and exit": "列出可用 LLM 提供商并退出",
    },
    "zh-hant": {
        "additional help": "附加說明",
        "Available LLM providers:": "可用 LLM 提供商：",
        "LLM model identifier override": "LLM 模型識別碼覆寫值",
        "LLM provider to use (default: %(default)s). Use --list-llm-providers "
        "to show available providers.": (
            "要使用的 LLM 提供商（預設：%(default)s）。使用 "
            "--list-llm-providers 查看可用提供商。"
        ),
        "list available LLM providers and exit": "列出可用 LLM 提供商並結束",
    },
}
"""Localized text shared by CLIs that expose LLM provider arguments."""


class _ListLLMProvidersAction(Action):
    """Print available LLM providers and exit."""

    def __init__(self, option_strings: list[str], dest: str, **kwargs: Any):
        """Initialize.

        Arguments:
            option_strings: option strings
            dest: argparse destination name
            **kwargs: additional keyword arguments
        """
        kwargs.setdefault("nargs", 0)
        super().__init__(option_strings=option_strings, dest=dest, **kwargs)

    def __call__(  # noqa: ARG002
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: Any,
        option_string: str | None = None,
    ):
        """Handle the action.

        Arguments:
            parser: active argument parser
            namespace: parsed namespace
            values: parsed argument value
            option_string: option string used
        """
        locale_name = ScinoephileCliBase.locale_name
        heading = LLM_LOCALIZATIONS.get(locale_name, {}).get(
            "Available LLM providers:",
            "Available LLM providers:",
        )
        lines = [heading]
        lines.extend(
            f"  {provider_name:<9} "
            f"{get_provider_description(provider_name, locale_name)}"
            for provider_name in get_provider_names()
        )
        parser._print_message("\n".join(lines) + "\n", sys.stdout)  # noqa: SLF001
        parser.exit(0)


def add_llm_provider_arguments(
    operation_arg_group: _ArgumentGroup,
    additional_help_arg_group: _ArgumentGroup,
):
    """Add standard LLM provider arguments to argument groups.

    Arguments:
        operation_arg_group: group to which provider arguments are added
        additional_help_arg_group: group to which help-only arguments are added
    """
    operation_arg_group.add_argument(
        "--llm-provider",
        default=get_default_provider_name(),
        dest="llm_provider_name",
        type=llm_provider_name_arg,
        help=(
            "LLM provider to use (default: %(default)s). Use --list-llm-providers "
            "to show available providers."
        ),
    )
    operation_arg_group.add_argument(
        "--llm-model",
        default=None,
        dest="llm_model_name",
        help="LLM model identifier override",
    )
    additional_help_arg_group.add_argument(
        "--list-llm-providers",
        action=_ListLLMProvidersAction,
        default=SUPPRESS,
        help="list available LLM providers and exit",
    )


def llm_provider_name_arg(value: str) -> str:
    """Validate an LLM provider name CLI argument.

    Arguments:
        value: raw CLI argument value
    Returns:
        validated provider name
    Raises:
        ArgumentTypeError: if provider name is not registered
    """
    provider_names = get_provider_names()
    if value in provider_names:
        return value
    options = ", ".join(provider_names)
    raise ArgumentTypeError(
        f"{value!r} is not one of the supported LLM providers: {options}"
    )
