#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Shared command-line helpers for one-based subtitle block ranges."""

from __future__ import annotations

from argparse import ArgumentParser, _ArgumentGroup  # noqa: PLC2701

from scinoephile.common.argument_parsing import int_arg

__all__ = [
    "BLOCK_LOCALIZATIONS",
    "add_block_range_args",
    "get_block_range_indexes",
]

BLOCK_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "first 1-indexed subtitle block to process, inclusive": (
            "要处理的第一个字幕区块（从 1 开始，包含该区块）"
        ),
        "last 1-indexed subtitle block to process, inclusive": (
            "要处理的最后一个字幕区块（从 1 开始，包含该区块）"
        ),
    },
    "zh-hant": {
        "first 1-indexed subtitle block to process, inclusive": (
            "要處理的第一個字幕區塊（從 1 開始，包含該區塊）"
        ),
        "last 1-indexed subtitle block to process, inclusive": (
            "要處理的最後一個字幕區塊（從 1 開始，包含該區塊）"
        ),
    },
}
"""Localized text shared by CLIs that select subtitle blocks."""


def add_block_range_args(
    operation_arg_group: _ArgumentGroup,
    *,
    first_help: str = "first 1-indexed subtitle block to process, inclusive",
    last_help: str = "last 1-indexed subtitle block to process, inclusive",
):
    """Add optional inclusive subtitle block boundaries.

    Arguments:
        operation_arg_group: argument group to which block boundaries are added
        first_help: help text for the first-block argument
        last_help: help text for the last-block argument
    """
    operation_arg_group.add_argument(
        "--first-block",
        type=int_arg(min_value=1),
        help=first_help,
    )
    operation_arg_group.add_argument(
        "--last-block",
        type=int_arg(min_value=1),
        help=last_help,
    )


def get_block_range_indexes(
    parser: ArgumentParser,
    first_block: int | None,
    last_block: int | None,
    block_count: int | None = None,
) -> tuple[int, int | None]:
    """Convert optional one-based block boundaries to processor indexes.

    Arguments:
        parser: active parser used to report invalid boundaries
        first_block: first included one-based subtitle block
        last_block: last included one-based subtitle block
        block_count: number of available subtitle blocks, if known
    Returns:
        inclusive zero-based start and exclusive zero-based stop indexes
    """
    if first_block is not None and last_block is not None and first_block > last_block:
        parser.error("--first-block must be less than or equal to --last-block")
    if block_count is not None:
        if first_block is not None and first_block > block_count:
            parser.error(
                f"--first-block must not exceed available block count {block_count}"
            )
        if last_block is not None and last_block > block_count:
            parser.error(
                f"--last-block must not exceed available block count {block_count}"
            )
    start_at_idx = 0
    if first_block is not None:
        start_at_idx = first_block - 1
    return start_at_idx, last_block
