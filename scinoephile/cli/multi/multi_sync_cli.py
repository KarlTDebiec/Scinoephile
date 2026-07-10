#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for syncing subtitle timings by offset."""

from __future__ import annotations

from argparse import ArgumentParser
from copy import deepcopy
from logging import getLogger
from pathlib import Path

from scinoephile.cli.helpers.io import read_series, write_series
from scinoephile.common.argument_parsing import (
    float_arg,
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.synchronization import get_sync_offset_stats

__all__ = ["MultiSyncCli"]

logger = getLogger(__name__)

MULTI_SYNC_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "estimate subtitle offset and shift a mobile series to an anchor series": (
            "估计字幕偏移并将移动序列平移到锚定序列"
        ),
        "Positive offset means the mobile series is later than the anchor series.": (
            "正数偏移表示移动序列晚于锚定序列。"
        ),
        (
            "minimum timing-overlap score from 0.0 to 1.0 used to form sync "
            "groups (default: 0.16)"
        ): ("用于形成同步组的最小时间重叠分数，范围 0.0 到 1.0（默认：0.16）"),
        'anchor subtitle infile or "-" for stdin': (
            '锚定字幕输入文件，或使用 "-" 表示标准输入'
        ),
        'mobile subtitle infile to shift or "-" for stdin': (
            '要平移的移动字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "pause length in milliseconds used to split subtitle blocks (default: 3000)": (
            "用于分割字幕块的停顿时长，单位为毫秒（默认：3000）"
        ),
        "synced mobile subtitle outfile path (default: stdout)": (
            "同步后的移动字幕输出文件路径（默认：标准输出）"
        ),
    },
    "zh-hant": {
        "estimate subtitle offset and shift a mobile series to an anchor series": (
            "估計字幕偏移並將移動序列平移到錨定序列"
        ),
        "Positive offset means the mobile series is later than the anchor series.": (
            "正數偏移表示移動序列晚於錨定序列。"
        ),
        (
            "minimum timing-overlap score from 0.0 to 1.0 used to form sync "
            "groups (default: 0.16)"
        ): ("用於形成同步組的最小時間重疊分數，範圍 0.0 到 1.0（預設：0.16）"),
        'anchor subtitle infile or "-" for stdin': (
            '錨定字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        'mobile subtitle infile to shift or "-" for stdin': (
            '要平移的移動字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "pause length in milliseconds used to split subtitle blocks (default: 3000)": (
            "用於分割字幕區塊的停頓時長，單位為毫秒（預設：3000）"
        ),
        "synced mobile subtitle outfile path (default: stdout)": (
            "同步後的移動字幕輸出檔路徑（預設：標準輸出）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class MultiSyncCli(ScinoephileCliBase):
    """Estimate subtitle offset and shift a mobile series to an anchor series.

    Positive offset means the mobile series is later than the anchor series.
    """

    localizations = MULTI_SYNC_LOCALIZATIONS
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
            "--anchor-infile",
            dest="anchor_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='anchor subtitle infile or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--mobile-infile",
            dest="mobile_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='mobile subtitle infile to shift or "-" for stdin',
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

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            type=output_file_arg(exist_ok=True),
            help="synced mobile subtitle outfile path (default: stdout)",
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
        return "sync"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        anchor_infile_path: Path | str,
        mobile_infile_path: Path | str,
        sync_cutoff: float,
        pause_length: int,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if anchor_infile_path == "-" and mobile_infile_path == "-":
            parser.error("--anchor-infile and --mobile-infile may not both be '-'")
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")

        # Read inputs
        anchor = read_series(parser, anchor_infile_path, allow_stdin=True)
        mobile = read_series(parser, mobile_infile_path, allow_stdin=True)

        # Perform operations
        try:
            stats = get_sync_offset_stats(
                anchor,
                mobile,
                sync_cutoff=sync_cutoff,
                pause_length=pause_length,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))
        logger.info(f"Mean offset: {stats.mean_ms / 1000:+.3f} s")

        synced = deepcopy(mobile)
        synced.shift(ms=int(round(-stats.mean_ms)))

        # Write outputs
        write_series(
            parser,
            synced,
            outfile_path if outfile_path is not None else "-",
            overwrite,
        )


if __name__ == "__main__":
    MultiSyncCli.main()
