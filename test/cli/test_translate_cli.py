#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of scinoephile.cli.translate_cli."""

from __future__ import annotations

from unittest.mock import patch

from pytest import mark, raises

from scinoephile.cli.translate_cli import TranslateCli
from scinoephile.common.testing import run_cli_with_args
from scinoephile.core.subtitles import Series
from test.helpers import test_data_root


def test_translate_cli_help_includes_block_range():
    """Test translation help exposes inclusive workflow block boundaries."""
    parser = TranslateCli.argparser()
    actions = {action.dest: action for action in parser._actions}  # noqa: SLF001

    assert actions["first_block"].help == (
        "first 1-indexed workflow block to process, inclusive"
    )
    assert actions["last_block"].help == (
        "last 1-indexed workflow block to process, inclusive"
    )


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
):
    """Test block ranges are forwarded through every translation mode.

    Arguments:
        workflow_name: workflow function expected to be called
        mode_arguments: arguments selecting the workflow mode
    """
    input_path = test_data_root / "mnt/output/zho-Hans_ocr/fuse.srt"
    mode_arguments = mode_arguments.format(input_path=input_path)

    with patch(
        f"scinoephile.cli.translate_cli.{workflow_name}",
        return_value=Series(),
    ) as workflow:
        with patch("scinoephile.cli.translate_cli.write_series"):
            run_cli_with_args(
                TranslateCli,
                f"{input_path} {mode_arguments} --first-block 2 --last-block 3",
            )

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
