#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests for CLI argument group assignments."""

from __future__ import annotations

from argparse import Action, ArgumentParser
from pathlib import Path

import pytest

from scinoephile.cli.eng.eng_process_cli import EngProcessCli
from scinoephile.cli.eng.eng_translate_from_yue_cli import EngTranslateFromYueCli
from scinoephile.cli.eng.eng_translate_from_zho_cli import EngTranslateFromZhoCli
from scinoephile.cli.helpers.cache import add_cache_dir_arg
from scinoephile.cli.helpers.llms import LlmArguments, add_llm_provider_args
from scinoephile.cli.helpers.web import (
    WebServerArguments,
    add_web_server_args,
)
from scinoephile.cli.ocr.ocr_fuse_cli import OcrFuseCli
from scinoephile.cli.ocr.ocr_process_cli import OcrProcessCli
from scinoephile.cli.ocr.ocr_validate_cli import OcrValidateCli
from scinoephile.cli.yue.yue_process_cli import YueProcessCli
from scinoephile.cli.yue.yue_review_vs_zho_cli import YueReviewVsZhoCli
from scinoephile.cli.yue.yue_transcribe_vs_zho_cli import YueTranscribeVsZhoCli
from scinoephile.cli.yue.yue_translate_from_eng_cli import YueTranslateFromEngCli
from scinoephile.cli.yue.yue_translate_from_zho_cli import YueTranslateFromZhoCli
from scinoephile.cli.zho.zho_process_cli import ZhoProcessCli
from scinoephile.cli.zho.zho_translate_from_eng_cli import ZhoTranslateFromEngCli
from scinoephile.cli.zho.zho_translate_from_yue_cli import ZhoTranslateFromYueCli
from scinoephile.common import CommandLineInterface

LLM_CLIS: tuple[type[CommandLineInterface], ...] = (
    EngProcessCli,
    EngTranslateFromYueCli,
    EngTranslateFromZhoCli,
    OcrFuseCli,
    OcrProcessCli,
    YueProcessCli,
    YueReviewVsZhoCli,
    YueTranscribeVsZhoCli,
    YueTranslateFromEngCli,
    YueTranslateFromZhoCli,
    ZhoProcessCli,
    ZhoTranslateFromEngCli,
    ZhoTranslateFromYueCli,
)
"""CLI classes that expose shared LLM arguments."""


@pytest.mark.parametrize("cli", LLM_CLIS)
def test_llm_options_are_in_llm_argument_group(cli: type[CommandLineInterface]):
    """Test shared LLM options are grouped separately from operation options.

    Arguments:
        cli: CLI class to inspect
    """
    assert _get_action_group_title(cli, "--llm-provider") == "llm arguments"
    assert _get_action_group_title(cli, "--llm-model") == "llm arguments"
    assert (
        _get_action_group_title(cli, "--llm-additional-content-file") == "llm arguments"
    )
    assert _get_action_group_title(cli, "--list-llm-providers") == "additional help"


def test_add_llm_provider_args_bundles_standard_llm_options(tmp_path):
    """Test the shared LLM helper bundles standard LLM provider options.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    context_file_path = tmp_path / "context.txt"
    context_file_path.write_text("context", encoding="utf-8")
    parser = ArgumentParser()
    llm_arg_group = parser.add_argument_group("llm arguments")
    additional_help_arg_group = parser.add_argument_group("additional help")

    add_llm_provider_args(llm_arg_group, additional_help_arg_group)

    namespace = parser.parse_args(
        [
            "--llm-provider",
            "openai",
            "--llm-model",
            "gpt-test",
            "--llm-additional-content-file",
            str(context_file_path),
        ]
    )
    assert namespace.llm_args == LlmArguments(
        provider_name="openai",
        model_name="gpt-test",
        additional_context_file_path=context_file_path.resolve(),
    )
    assert not hasattr(namespace, "llm")
    assert not hasattr(namespace, "llm_provider_name")
    assert not hasattr(namespace, "llm_model_name")
    assert not hasattr(namespace, "llm_additional_context_file_path")

    model_namespace = parser.parse_args(["--llm-model", "gpt-test"])
    assert model_namespace.llm_args == LlmArguments(model_name="gpt-test")

    default_namespace = parser.parse_args([])
    assert default_namespace.llm_args == LlmArguments()


@pytest.mark.parametrize("cli", (OcrProcessCli, OcrValidateCli))
def test_ocr_web_options_are_in_web_argument_group(cli: type[CommandLineInterface]):
    """Test OCR web options are grouped separately from operation options.

    Arguments:
        cli: CLI class to inspect
    """
    assert _get_action_group_title(cli, "--interactive") == "web arguments"
    assert _get_action_group_title(cli, "--host") == "web arguments"
    assert _get_action_group_title(cli, "--port") == "web arguments"


def test_add_web_server_args_bundles_standard_host_and_port():
    """Test the shared web server helper bundles standard host and port options."""
    parser = ArgumentParser()
    web_arg_group = parser.add_argument_group("web arguments")

    add_web_server_args(web_arg_group)

    namespace = parser.parse_args(["--host", "0.0.0.0", "--port", "5050"])
    assert namespace.web_args == WebServerArguments(host="0.0.0.0", port=5050)
    assert not hasattr(namespace, "web")
    assert not hasattr(namespace, "host")
    assert not hasattr(namespace, "port")

    port_namespace = parser.parse_args(["--port", "5051"])
    assert port_namespace.web_args == WebServerArguments(host="127.0.0.1", port=5051)

    default_namespace = parser.parse_args([])
    assert default_namespace.web_args == WebServerArguments()

    with pytest.raises(SystemExit):
        parser.parse_args(["--port", "65536"])


def test_add_cache_dir_arg_adds_standard_cache_option(tmp_path: Path):
    """Test the shared cache helper adds a standard cache directory option.

    Arguments:
        tmp_path: pytest temporary path fixture
    """
    parser = ArgumentParser()
    cache_arg_group = parser.add_argument_group("operation arguments")

    add_cache_dir_arg(cache_arg_group, "media", "subtitles")

    cache_dir_path = tmp_path / "cache"
    namespace = parser.parse_args(["--cache-dir", str(cache_dir_path)])
    assert namespace.cache_dir_path == cache_dir_path.resolve()
    assert not cache_dir_path.exists()


def test_add_cache_dir_arg_accepts_custom_help_text():
    """Test CLI-specific cache help text can override generic helper text."""
    parser = ArgumentParser()
    cache_arg_group = parser.add_argument_group("operation arguments")

    add_cache_dir_arg(
        cache_arg_group,
        "ocr_validation",
        help_text="custom cache directory help (default: %(default)s)",
    )

    action = _get_action(parser, "--cache-dir")
    assert action.help == "custom cache directory help (default: %(default)s)"


def _get_action(parser: ArgumentParser, option: str) -> Action:
    """Get a parser action by option string.

    Arguments:
        parser: parser to inspect
        option: option string to inspect
    Returns:
        matching argparse action
    Raises:
        AssertionError: if the option is not present
    """
    for action in parser._actions:  # noqa: SLF001
        if option in action.option_strings:
            return action
    raise AssertionError(f"{option} not found in {parser.prog}")


def _get_action_group_title(cli: type[CommandLineInterface], option: str) -> str:
    """Get the group title for a parser option.

    Arguments:
        cli: CLI class to inspect
        option: option string to inspect
    Returns:
        title of the argument group containing the option
    Raises:
        AssertionError: if the option is not assigned to a group
    """
    parser = cli.argparser()
    action = _get_action(parser, option)
    for group in parser._action_groups:  # noqa: SLF001
        if action in group._group_actions:  # noqa: SLF001
            if group.title is not None:
                return group.title
            break
    raise AssertionError(f"{option} is not assigned to an argument group")
