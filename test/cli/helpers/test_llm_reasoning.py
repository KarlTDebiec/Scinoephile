#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared CLI reasoning parsing and workflow forwarding tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from scinoephile.cli.review_cli import ReviewCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.llms import ReasoningEffort
from scinoephile.core.subtitles import Series


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
