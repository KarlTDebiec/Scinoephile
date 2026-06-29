#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ZhoProcessCli."""

from __future__ import annotations

from io import StringIO
from unittest.mock import patch

from pytest import raises

from scinoephile.cli.zho.zho_process_cli import ZhoProcessCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from scinoephile.llms.providers.deepseek_provider import DeepSeekProvider
from test.helpers import assert_series_equal, parametrize, test_data_root


@parametrize(
    ("input_path", "args", "expected_path"),
    [
        (
            "mnt/output/zho-Hans_ocr/fuse.srt",
            "--clean",
            "mnt/output/zho-Hans_ocr/fuse_clean.srt",
        ),
        (
            "mnt/output/zho-Hant_ocr/fuse_clean_validate_review_flatten.srt",
            "--convert t2s",
            "mnt/output/zho-Hant_ocr/fuse_clean_validate_review_flatten_simplify.srt",
        ),
    ],
)
def test_zho_process_cli(
    input_path: str,
    args: str,
    expected_path: str,
):
    """Test standard Chinese processing CLI with file arguments.

    Arguments:
        input_path: path to input subtitle fixture
        args: command-line arguments for operation selection
        expected_path: path to expected output subtitle fixture
    """
    full_input_path = test_data_root / input_path
    full_expected_path = test_data_root / expected_path

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            ZhoProcessCli,
            f"--infile {full_input_path} {args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert_series_equal(output, expected)


@parametrize(
    ("input_path", "args", "expected_path"),
    [
        (
            "mnt/output/zho-Hans_ocr/fuse.srt",
            "--clean",
            "mnt/output/zho-Hans_ocr/fuse_clean.srt",
        ),
    ],
)
def test_zho_process_cli_pipe(input_path: str, args: str, expected_path: str):
    """Test standard Chinese processing CLI via stdin/stdout.

    Arguments:
        input_path: path to input subtitle fixture
        args: command-line arguments for operation selection
        expected_path: path to expected output subtitle fixture
    """
    full_input_path = test_data_root / input_path
    full_expected_path = test_data_root / expected_path
    input_text = full_input_path.read_text(encoding="utf-8")

    stdin_stream = StringIO(input_text)
    stdout_stream = StringIO()
    with patch("scinoephile.cli.helpers.io.stdin", stdin_stream):
        with patch("scinoephile.cli.helpers.io.stdout", stdout_stream):
            run_cli_with_args(ZhoProcessCli, f"--infile - {args}")

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(full_expected_path)

    assert_series_equal(output, expected)


def test_zho_process_cli_offsets_timing():
    """Test standard Chinese processing CLI can offset subtitle timings."""
    full_input_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            ZhoProcessCli,
            f"--infile {full_input_path} --offset 1250 --outfile {output_path}",
        )
        output = Series.load(output_path)

    expected = Series.load(full_input_path)
    expected.shift(ms=1250)
    assert_series_equal(output, expected)


def test_zho_process_cli_rejects_bare_convert_flag():
    """Test standard Chinese processing CLI requires an explicit conversion config."""
    full_input_path = (
        test_data_root
        / "mnt/output/zho-Hant_ocr/fuse_clean_validate_review_flatten.srt"
    )

    with raises(SystemExit, match="2"):
        run_cli_with_args(ZhoProcessCli, f"--infile {full_input_path} --convert")


def test_zho_process_cli_passes_llm_options_to_reviewer(tmp_path):
    """Test standard Chinese CLI constructs configured LLM provider for review."""
    full_input_path = test_data_root / "mnt/output/zho-Hant_ocr/fuse_clean_validate.srt"
    expected = Series.load(
        test_data_root / "mnt/output/zho-Hant_ocr/fuse_clean_validate_review.srt"
    )
    context_path = tmp_path / "context.txt"
    context_path.write_text("Use glossary terms.\n", encoding="utf-8")

    def get_reviewer(
        *,
        prompt_cls: object,
        provider: DeepSeekProvider,
        additional_context: str | None,
    ) -> str:
        """Validate reviewer options passed by the CLI."""
        assert prompt_cls is not None
        assert provider.model == "custom-model"
        assert additional_context == "Use glossary terms.\n"
        return "proofreader"

    with get_temp_file_path(".srt") as output_path:
        with patch(
            "scinoephile.cli.zho.zho_process_cli.get_zho_reviewer",
            side_effect=get_reviewer,
        ):
            with patch(
                "scinoephile.cli.zho.zho_process_cli.get_zho_block_reviewed",
                return_value=expected,
            ):
                run_cli_with_args(
                    ZhoProcessCli,
                    f"--infile {full_input_path} --proofread traditional "
                    "--llm-provider deepseek --llm-model custom-model "
                    f"--llm-additional-content-file {context_path} "
                    f"--outfile {output_path}",
                )

