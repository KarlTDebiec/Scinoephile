#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.translate_cli."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from pytest import mark, raises

from scinoephile.cli.translate_cli import TranslateCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import test_data_root


def test_translate_cli_help_includes_block_range():
    """Test translation help exposes inclusive subtitle block boundaries."""
    parser = TranslateCli.argparser()
    actions = {action.dest: action for action in parser._actions}  # noqa: SLF001

    assert actions["first_block"].help == (
        "first 1-indexed subtitle block to process, inclusive"
    )
    assert actions["last_block"].help == (
        "last 1-indexed subtitle block to process, inclusive"
    )
    assert actions["source_language"].help == (
        "source language (detected from infile if omitted)"
    )
    assert actions["target_language"].help == (
        "target language (required unless guide or gapped input is detected)"
    )
    assert actions["json_path"].help == "JSON file containing test cases"


@mark.parametrize(
    ("workflow_name", "mode_arguments"),
    (
        ("translate_series", "--target-language eng"),
        ("translate_series_gaps", "--gapped-infile {input_path}"),
        ("translate_series_guided", "--guide-infile {input_path}"),
    ),
)
def test_translate_cli_passes_block_range(
    workflow_name: str,
    mode_arguments: str,
    tmp_path: Path,
):
    """Test block ranges and JSON paths reach every translation mode.

    Arguments:
        workflow_name: workflow function expected to be called
        mode_arguments: arguments selecting the workflow mode
        tmp_path: temporary directory path
    """
    input_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    mode_arguments = mode_arguments.format(input_path=input_path)
    json_path = tmp_path / "translation.json"

    with patch(
        f"scinoephile.cli.translate_cli.{workflow_name}",
        return_value=Series(),
    ) as workflow:
        with patch("scinoephile.cli.translate_cli.write_series"):
            run_cli_with_args(
                TranslateCli,
                f"{input_path} {mode_arguments} --json {json_path} "
                "--first-block 2 --last-block 3",
            )

    assert workflow.call_args.kwargs["test_case_path"] == json_path
    assert workflow.call_args.kwargs["start_at_idx"] == 1
    assert workflow.call_args.kwargs["stop_at_idx"] == 3


def test_translate_cli_rejects_reversed_block_range():
    """Test the first selected block cannot follow the last selected block."""
    input_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            TranslateCli,
            f"{input_path} --target-language eng --first-block 3 --last-block 2",
        )


@mark.parametrize(
    "mode_arguments",
    (
        "--target-language eng",
        "--gapped-infile {input_path}",
        "--guide-infile {input_path}",
    ),
)
def test_translate_cli_rejects_oversized_last_block(mode_arguments: str):
    """Test every translation mode rejects a last block beyond its input.

    Arguments:
        mode_arguments: arguments selecting the workflow mode
    """
    input_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    block_count = len(Series.load(input_path).blocks)
    mode_arguments = mode_arguments.format(input_path=input_path)

    with raises(SystemExit, match="2"):
        run_cli_with_args(
            TranslateCli,
            f"{input_path} {mode_arguments} --last-block {block_count + 1}",
        )
