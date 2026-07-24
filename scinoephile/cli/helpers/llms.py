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
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from scinoephile.common.argument_parsing import input_file_arg, output_file_arg
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.llms.providers.registry import (
    DEFAULT_PROVIDER_NAME,
    get_provider_api_key_env_var_name,
    get_provider_default_model,
    get_provider_description,
    get_provider_names,
)

from .argument_bundle_field_action import ArgumentBundleFieldAction

__all__ = [
    "LLM_LOCALIZATIONS",
    "LLM_TEST_CASE_JSON_LOCALIZATIONS",
    "LlmArguments",
    "add_llm_provider_args",
    "add_llm_test_case_json_arg",
    "llm_provider_name_arg",
    "read_llm_additional_context",
]

LLM_TEST_CASE_JSON_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "JSON file containing test cases": "包含测试用例的 JSON 文件",
    },
    "zh-hant": {
        "JSON file containing test cases": "包含測試案例的 JSON 檔",
    },
}
"""Localized text shared by CLIs that expose one LLM test-case JSON file."""

LLM_LOCALIZATIONS: dict[str, dict[str, str]] = merge_localizations(
    LLM_TEST_CASE_JSON_LOCALIZATIONS,
    {
        "zh-hans": {
            "additional help": "附加帮助",
            "Available LLM providers:": "可用 LLM 提供商：",
            "text file from which to read additional LLM prompt context": (
                "用于读取 LLM 提示词附加上下文的文本文件"
            ),
            "llm arguments": "LLM 参数",
            "LLM model": "LLM 模型",
            f"LLM provider (default: {DEFAULT_PROVIDER_NAME}). Use "
            "--list-llm-providers for more information.": (
                f"LLM 提供商（默认：{DEFAULT_PROVIDER_NAME}）。使用 "
                "--list-llm-providers 获取更多信息。"
            ),
            "list available LLM providers and exit": "列出可用 LLM 提供商并退出",
        },
        "zh-hant": {
            "additional help": "附加說明",
            "Available LLM providers:": "可用 LLM 提供商：",
            "text file from which to read additional LLM prompt context": (
                "用於讀取 LLM 提示詞附加上下文的文字檔"
            ),
            "llm arguments": "LLM 參數",
            "LLM model": "LLM 模型",
            f"LLM provider (default: {DEFAULT_PROVIDER_NAME}). Use "
            "--list-llm-providers for more information.": (
                f"LLM 提供商（預設：{DEFAULT_PROVIDER_NAME}）。使用 "
                "--list-llm-providers 取得更多資訊。"
            ),
            "list available LLM providers and exit": "列出可用 LLM 提供商並結束",
        },
    },
)
"""Localized text shared by CLIs that expose LLM provider arguments."""


@dataclass(frozen=True)
class LlmArguments:
    """Parsed LLM provider CLI arguments."""

    provider_name: str = DEFAULT_PROVIDER_NAME
    """LLM provider name."""
    model_name: str | None = None
    """Optional LLM model name override."""
    additional_context_file_path: Path | None = None
    """Optional path to additional LLM prompt context."""


def add_llm_provider_args(
    llm_arg_group: _ArgumentGroup,
    additional_help_arg_group: _ArgumentGroup,
):
    """Add standard LLM provider arguments to argument groups.

    Arguments:
        llm_arg_group: group to which provider arguments are added
        additional_help_arg_group: group to which help-only arguments are added
    """
    llm_arg_group.add_argument(
        "--llm-provider",
        action=ArgumentBundleFieldAction,
        bundle_type=LlmArguments,
        dest="llm_args",
        field_name="provider_name",
        metavar="LLM_PROVIDER",
        type=llm_provider_name_arg,
        help=f"LLM provider (default: {DEFAULT_PROVIDER_NAME}). Use "
        "--list-llm-providers for more information.",
    )
    llm_arg_group.add_argument(
        "--llm-model",
        action=ArgumentBundleFieldAction,
        bundle_type=LlmArguments,
        dest="llm_args",
        field_name="model_name",
        metavar="LLM_MODEL",
        help="LLM model",
    )
    llm_arg_group.add_argument(
        "--llm-additional-content-file",
        action=ArgumentBundleFieldAction,
        bundle_type=LlmArguments,
        dest="llm_args",
        field_name="additional_context_file_path",
        metavar="FILE",
        type=input_file_arg(),
        help="text file from which to read additional LLM prompt context",
    )
    additional_help_arg_group.add_argument(
        "--list-llm-providers",
        action=_ListLLMProvidersAction,
        default=SUPPRESS,
        help="list available LLM providers and exit",
    )


def add_llm_test_case_json_arg(
    llm_arg_group: _ArgumentGroup,
    option_name: str = "--json",
    *,
    dest: str = "json_path",
    help_text: str = "JSON file containing test cases",
):
    """Add a test-case JSON persistence argument.

    Arguments:
        llm_arg_group: argument group to which the JSON argument is added
        option_name: command-line option name
        dest: parsed argument destination
        help_text: argument help text
    """
    llm_arg_group.add_argument(
        option_name,
        dest=dest,
        type=output_file_arg(exist_ok=True),
        help=help_text,
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


def read_llm_additional_context(
    parser: ArgumentParser,
    llm_additional_context_file_path: Path | None,
) -> str | None:
    """Read additional context for LLM prompts.

    Arguments:
        parser: active argument parser
        llm_additional_context_file_path: optional file from which to read context
    Returns:
        additional context text, if provided
    """
    if llm_additional_context_file_path is None:
        return None
    try:
        return llm_additional_context_file_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        parser.error(str(exc))


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
        for provider_name in get_provider_names():
            details = self._get_provider_details(provider_name)
            lines.append(
                f"  {provider_name:<9} "
                f"{get_provider_description(provider_name, locale_name)} {details}"
            )
        parser._print_message("\n".join(lines) + "\n", sys.stdout)  # noqa: SLF001
        parser.exit(0)

    @staticmethod
    def _get_provider_details(provider_name: str) -> str:
        """Get human-readable provider configuration details.

        Arguments:
            provider_name: provider identifier
        Returns:
            configuration detail string
        """
        model_name = get_provider_default_model(provider_name)
        env_var_name = get_provider_api_key_env_var_name(provider_name)
        details: list[str] = []
        if model_name is not None:
            details.append(f"default model: {model_name}")
        if env_var_name is not None:
            details.append(f"API key env: {env_var_name}")
        if not details:
            return ""
        return f"({'; '.join(details)})"
