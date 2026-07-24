#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.ReviewCli."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
from unittest.mock import patch

from pytest import raises

from scinoephile.cli.review_cli import ReviewCli
from scinoephile.cli.scinoephile_cli import ScinoephileCli
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import assert_series_equal, parametrize, test_data_root


def test_review_cli_is_top_level_command():
    """Test review replaces proofread as the top-level command."""
    assert ReviewCli.name() == "review"
    assert ScinoephileCli.subcommands()["review"] is ReviewCli
    assert "proofread" not in ScinoephileCli.subcommands()


def test_review_cli_uses_guide_terminology():
    """Test guided review arguments consistently use guide terminology."""
    parser = ReviewCli.argparser()
    help_text = parser.format_help()
    actions = {
        action.dest: action
        for action in parser._actions  # noqa: SLF001
    }

    assert "--guide-infile" in help_text
    assert "--guide-language" in help_text
    assert "--reference-language" not in help_text
    assert actions["language"].help == (
        "subtitle language (detected from infile if omitted)"
    )
    assert actions["guide_language"].help == (
        "guide language (detected from infile if omitted)"
    )
    assert actions["json_path"].help == "JSON file containing test cases"
    cache_overwrite_action = next(
        action
        for action in parser._actions  # noqa: SLF001
        if "--cache-overwrite" in action.option_strings
    )
    assert cache_overwrite_action.help == "overwrite matching cache files"


@parametrize(
    ("input_path", "args", "expected_path"),
    [
        (
            "kob/output/yue-Hant/clean.srt",
            "--language yue-Hant",
            "kob/output/yue-Hant/clean_review.srt",
        ),
    ],
)
def test_review_cli(input_path: str, args: str, expected_path: str):
    """Test review CLI with file arguments.

    Arguments:
        input_path: path to input subtitle fixture
        args: command-line arguments for operation selection
        expected_path: path to expected output subtitle fixture
    """
    full_input_path = test_data_root / input_path
    full_expected_path = test_data_root / expected_path

    with get_temp_file_path(".srt") as output_path:
        run_cli_with_args(
            ReviewCli,
            f"{full_input_path} {args} --outfile {output_path}",
        )
        output = Series.load(output_path)
        expected = Series.load(full_expected_path)

    assert_series_equal(output, expected)


@parametrize(
    ("input_path", "args", "expected_path"),
    [
        (
            "mnt/output/eng_ocr/fuse_clean_validate.srt",
            "",
            "mnt/output/eng_ocr/fuse_clean_validate_review.srt",
        ),
    ],
)
def test_review_cli_pipe(input_path: str, args: str, expected_path: str):
    """Test review CLI via stdin/stdout.

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
            run_cli_with_args(ReviewCli, f"- {args}".strip())

    output = Series.from_string(stdout_stream.getvalue(), format_="srt")
    expected = Series.load(full_expected_path)

    assert_series_equal(output, expected)


@parametrize(
    ("workflow_name", "guide_argument"),
    [
        ("review_series", ""),
        ("review_series_guided", "--guide-infile"),
    ],
)
def test_review_cli_passes_block_range(
    workflow_name: str,
    guide_argument: str,
    tmp_path: Path,
):
    """Test block ranges and JSON paths are forwarded through every review mode.

    Arguments:
        workflow_name: workflow function expected to be called
        guide_argument: optional guide argument selecting the workflow mode
        tmp_path: temporary directory path
    """
    input_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate.srt"
    guide_args = ""
    if guide_argument:
        guide_args = f"{guide_argument} {input_path} --guide-language eng"
    json_path = tmp_path / "review.json"
    cache_dir_path = tmp_path / "cache"

    with patch(
        f"scinoephile.cli.review_cli.{workflow_name}",
        return_value=Series(),
    ) as workflow:
        with patch("scinoephile.cli.review_cli.write_series"):
            run_cli_with_args(
                ReviewCli,
                f"{input_path} {guide_args} --json {json_path} "
                f"--first-block 2 --last-block 3 --cache-dir {cache_dir_path} "
                "--cache-overwrite",
            )

    assert workflow.call_args.kwargs["test_case_path"] == json_path
    assert workflow.call_args.kwargs["start_at_idx"] == 1
    assert workflow.call_args.kwargs["stop_at_idx"] == 3
    assert workflow.call_args.kwargs["cache_dir_path"] == (
        cache_dir_path.resolve() / "llm"
    )
    assert workflow.call_args.kwargs["overwrite_cache"] is True
    if guide_argument:
        assert workflow.call_args.kwargs["guide_language"].code == "eng"


def test_review_cli_rejects_reversed_block_range():
    """Test the first selected block cannot follow the last selected block."""
    input_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate.srt"

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            ReviewCli,
            f"{input_path} --first-block 3 --last-block 2",
        )


@parametrize(
    "guide_args",
    (
        "",
        "--guide-infile {input_path}",
    ),
)
def test_review_cli_rejects_oversized_last_block(guide_args: str):
    """Test the last selected block cannot exceed the available block count.

    Arguments:
        guide_args: optional guide arguments selecting guided review
    """
    input_path = test_data_root / "mnt/output/eng_ocr/fuse_clean_validate.srt"
    block_count = len(Series.load(input_path).blocks)
    guide_args = guide_args.format(input_path=input_path)

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            ReviewCli,
            f"{input_path} {guide_args} --last-block {block_count + 1}",
        )
