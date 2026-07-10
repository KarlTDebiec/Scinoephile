#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for stacking two subtitle series."""

from __future__ import annotations

from argparse import ArgumentParser
from copy import deepcopy
from enum import StrEnum
from logging import getLogger
from pathlib import Path

from scinoephile.cli.helpers.io import read_series, write_series
from scinoephile.common.argument_parsing import (
    enum_arg,
    float_arg,
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.stacking import StackTimingMode, get_stacked_series
from scinoephile.core.synchronization import (
    get_sync_offset_stats,
)

__all__ = [
    "MultiStackCli",
    "StackSyncMode",
]

logger = getLogger(__name__)


class StackSyncMode(StrEnum):
    """Pre-stack sync modes."""

    ANCHOR_TOP = "anchor-top"
    """Shift bottom subtitles to the top subtitle timing before stacking."""
    ANCHOR_BOTTOM = "anchor-bottom"
    """Shift top subtitles to the bottom subtitle timing before stacking."""
    OFF = "off"
    """Stack subtitles without shifting either input series."""


MULTI_STACK_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "stack two series into top and bottom subtitle lines": (
            "将两个序列堆叠为上下行字幕"
        ),
        (
            "minimum timing-overlap score from 0.0 to 1.0 used to form sync "
            "groups (default: 0.16)"
        ): ("用于形成同步组的最小时间重叠分数，范围 0.0 到 1.0（默认：0.16）"),
        "pause length in milliseconds used to split subtitle blocks (default: 3000)": (
            "用于分割字幕块的停顿时长，单位为毫秒（默认：3000）"
        ),
        (
            "pre-stack sync mode (options: anchor-top, anchor-bottom, off; "
            "default: off)"
        ): ("堆叠前同步模式（选项：anchor-top、anchor-bottom、off；默认：off）"),
        "stacked subtitle outfile path (default: stdout)": (
            "堆叠字幕输出文件路径（默认：标准输出）"
        ),
        'subtitle infile for bottom line or "-" for stdin': (
            '底行字幕输入文件，或使用 "-" 表示标准输入'
        ),
        'subtitle infile for top line or "-" for stdin': (
            '顶行字幕输入文件，或使用 "-" 表示标准输入'
        ),
    },
    "zh-hant": {
        "stack two series into top and bottom subtitle lines": (
            "將兩個序列堆疊為上下行字幕"
        ),
        (
            "minimum timing-overlap score from 0.0 to 1.0 used to form sync "
            "groups (default: 0.16)"
        ): ("用於形成同步組的最小時間重疊分數，範圍 0.0 到 1.0（預設：0.16）"),
        "pause length in milliseconds used to split subtitle blocks (default: 3000)": (
            "用於分割字幕區塊的停頓時長，單位為毫秒（預設：3000）"
        ),
        (
            "pre-stack sync mode (options: anchor-top, anchor-bottom, off; "
            "default: off)"
        ): ("堆疊前同步模式（選項：anchor-top、anchor-bottom、off；預設：off）"),
        "stacked subtitle outfile path (default: stdout)": (
            "堆疊字幕輸出檔路徑（預設：標準輸出）"
        ),
        'subtitle infile for bottom line or "-" for stdin': (
            '底行字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        'subtitle infile for top line or "-" for stdin': (
            '頂行字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class MultiStackCli(ScinoephileCliBase):
    """Stack two series into top and bottom subtitle lines."""

    localizations = MULTI_STACK_LOCALIZATIONS
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)
        arg_groups = get_arg_groups_by_name(
            parser,
            "input arguments",
            "operation arguments",
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--top-infile",
            dest="top_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='subtitle infile for top line or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--bottom-infile",
            dest="bottom_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='subtitle infile for bottom line or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--sync-cutoff",
            default=0.16,
            type=float_arg(min_value=0.0, max_value=1.0),
            help=(
                "minimum timing-overlap score from 0.0 to 1.0 used to form sync "
                "groups (default: 0.16)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--pause-length",
            default=3000,
            type=int_arg(min_value=1),
            help=(
                "pause length in milliseconds used to split subtitle blocks "
                "(default: 3000)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--sync",
            default=StackSyncMode.OFF,
            dest="sync_mode",
            metavar="{anchor-top,anchor-bottom,off}",
            type=enum_arg(StackSyncMode),
            help=(
                "pre-stack sync mode (options: anchor-top, anchor-bottom, off; "
                "default: off)"
            ),
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            type=output_file_arg(exist_ok=True),
            help="stacked subtitle outfile path (default: stdout)",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "stack"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        top_infile_path: Path | str,
        bottom_infile_path: Path | str,
        sync_cutoff: float,
        pause_length: int,
        sync_mode: StackSyncMode,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if top_infile_path == "-" and bottom_infile_path == "-":
            parser.error("--top-infile and --bottom-infile may not both be '-'")
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")

        # Read inputs
        top = read_series(parser, top_infile_path, allow_stdin=True)
        bottom = read_series(parser, bottom_infile_path, allow_stdin=True)

        # Perform operations
        try:
            timing_mode = StackTimingMode.OUTER
            if sync_mode == StackSyncMode.ANCHOR_TOP:
                stats = get_sync_offset_stats(
                    top,
                    bottom,
                    sync_cutoff=sync_cutoff,
                    pause_length=pause_length,
                )
                bottom = deepcopy(bottom)
                bottom.shift(ms=int(round(-stats.mean_ms)))
                timing_mode = StackTimingMode.TOP
                logger.info(f"Mean offset: {stats.mean_ms / 1000:+.3f} s")
            elif sync_mode == StackSyncMode.ANCHOR_BOTTOM:
                stats = get_sync_offset_stats(
                    bottom,
                    top,
                    sync_cutoff=sync_cutoff,
                    pause_length=pause_length,
                )
                top = deepcopy(top)
                top.shift(ms=int(round(-stats.mean_ms)))
                timing_mode = StackTimingMode.BOTTOM
                logger.info(f"Mean offset: {stats.mean_ms / 1000:+.3f} s")

            stacked = get_stacked_series(
                top,
                bottom,
                sync_cutoff=sync_cutoff,
                pause_length=pause_length,
                timing_mode=timing_mode,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write outputs
        write_series(
            parser,
            stacked,
            outfile_path if outfile_path is not None else "-",
            overwrite,
        )


if __name__ == "__main__":
    MultiStackCli.main()
