#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared CLI reasoning parsing and workflow forwarding tests."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from unittest.mock import patch

from pytest import mark, raises

from scinoephile.cli.helpers.llms import (
    LLM_LOCALIZATIONS,
    LlmArguments,
    add_llm_provider_args,
)
from scinoephile.cli.ocr.ocr_fuse_cli import OcrFuseCli
from scinoephile.cli.ocr.ocr_process_cli import OcrProcessCli
from scinoephile.cli.review_cli import ReviewCli
from scinoephile.cli.transcribe_cli import TranscribeCli
from scinoephile.cli.translate_cli import TranslateCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.llms import ReasoningEffort
from scinoephile.core.subtitles import Series


@mark.parametrize(
    "cli", [ReviewCli, TranslateCli, TranscribeCli, OcrFuseCli, OcrProcessCli]
)
def test_all_llm_commands_expose_shared_effort(cli: type[ScinoephileCliBase]):
    """Expose the same flag throughout every LLM workflow CLI.

    Arguments:
        cli: LLM workflow command
    """
    assert "--llm-reasoning-effort" in cli.argparser().format_help()


def test_shared_argument_bundle_parses_and_rejects_effort():
    """Validate levels at parsing time and retain provider defaults on omission."""
    parser = ArgumentParser()
    add_llm_provider_args(
        parser.add_argument_group("llm arguments"),
        parser.add_argument_group("additional help"),
    )
    parsed = parser.parse_args(
        ["--llm-provider", "deepseek", "--llm-reasoning-effort", "max"]
    )
    assert parsed.llm_args.reasoning_effort is ReasoningEffort.max
    assert parsed.llm_args.provider_kwargs == {"model": None, "reasoning_effort": "max"}
    assert LlmArguments().provider_kwargs == {"model": None}
    with raises(SystemExit):
        parser.parse_args(["--llm-reasoning-effort", "typo"])
    help_text = (
        "LLM reasoning effort (default: provider default; "
        "supported levels depend on model)"
    )
    for locale in ("zh-hans", "zh-hant"):
        assert help_text in LLM_LOCALIZATIONS[locale]


def test_review_forwards_model_and_reasoning_to_provider(tmp_path: Path):
    """Forward parsed effort from a real command into the provider constructor.

    Arguments:
        tmp_path: temporary subtitle directory
    """
    infile_path = tmp_path / "input.srt"
    infile_path.write_text(
        "1\n00:00:01,000 --> 00:00:02,000\nHello.\n", encoding="utf-8"
    )
    with patch("scinoephile.cli.review_cli.get_provider") as provider:
        with patch("scinoephile.cli.review_cli.review_series", return_value=Series()):
            with patch("scinoephile.cli.review_cli.write_series"):
                run_cli_with_args(
                    ReviewCli,
                    f"{infile_path} --language eng --llm-model gpt-6-luna "
                    "--llm-reasoning-effort xhigh",
                )
    provider.assert_called_once_with(
        "openai", model="gpt-6-luna", reasoning_effort=ReasoningEffort.xhigh
    )
