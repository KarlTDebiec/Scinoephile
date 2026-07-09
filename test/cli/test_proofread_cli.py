#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ProofreadCli."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

from scinoephile.cli.proofread_cli import ProofreadCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core import Language
from scinoephile.core.subtitles import Series
from scinoephile.llms.providers.deepseek_provider import DeepSeekProvider
from test.helpers import assert_series_equal, test_data_root


def test_proofread_cli_is_top_level_subcommand():
    """Test proofread CLI is registered as a top-level subcommand."""
    assert ScinoephileCli.subcommands()["proofread"] is ProofreadCli


def test_proofread_cli_passes_llm_options_to_reviewer(tmp_path):
    """Test proofread CLI constructs configured LLM provider for review."""
    full_input_path = test_data_root / "kob/output/yue-Hant/clean.srt"
    expected = Series.load(test_data_root / "kob/output/yue-Hant/clean_review.srt")
    context_path = tmp_path / "context.txt"
    context_path.write_text("Use glossary terms.\n", encoding="utf-8")

    def review_series_blocks(
        series: Series,
        *,
        language: Language,
        provider: DeepSeekProvider,
        additional_context: str | None,
    ) -> Series:
        """Validate review options passed by the CLI."""
        assert_series_equal(series, Series.load(full_input_path))
        assert language is Language.yue_hant
        assert provider.model == "custom-model"
        assert additional_context == "Use glossary terms.\n"
        return expected

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.proofread_cli.review_series_blocks",
            side_effect=review_series_blocks,
        ):
            run_cli_with_args(
                ProofreadCli,
                f"{full_input_path} --language yue-Hant "
                "--llm-provider deepseek --llm-model custom-model "
                f"--llm-additional-content-file {context_path} "
                f"--outfile {output_path}",
            )

        output = Series.load(output_path)

    assert_series_equal(output, expected)


def test_proofread_cli_pipe_detects_language_in_workflow():
    """Test proofread CLI delegates omitted language detection to the workflow."""
    full_input_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate.srt"
    expected = Series.load(
        test_data_root / "mnt/output/eng_ocr/fuse_clean_validate_review.srt"
    )
    input_text = full_input_path.read_text(encoding="utf-8")

    def review_series_blocks(
        series: Series,
        *,
        language: Language | None,
        provider: object,
        additional_context: str | None,
    ) -> Series:
        """Validate review options passed by the CLI."""
        assert_series_equal(series, Series.load(full_input_path))
        assert language is None
        assert provider is not None
        assert additional_context is None
        return expected

    stdin_stream = StringIO(input_text)
    stdout_stream = StringIO()
    with patch("scinoephile.cli.helpers.io.stdin", stdin_stream):
        with patch("scinoephile.cli.helpers.io.stdout", stdout_stream):
            with patch(
                "scinoephile.cli.proofread_cli.review_series_blocks",
                side_effect=review_series_blocks,
            ):
                run_cli_with_args(ProofreadCli, "-")

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    assert_series_equal(output, expected)
