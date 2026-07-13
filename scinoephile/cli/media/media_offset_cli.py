#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for estimating visual media offset."""

from __future__ import annotations

from argparse import ArgumentParser
from math import nextafter
from pathlib import Path

from scinoephile.common.argument_parsing import (
    float_arg,
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.timing import format_time_ms
from scinoephile.media.offset.video import VideoOffsetResult
from scinoephile.media.offset.video.detection import get_video_offset
from scinoephile.media.offset.video.video_offset_window_result import (
    VideoOffsetWindowResult,
)

__all__ = ["MediaOffsetCli"]

MEDIA_OFFSET_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for estimating visual media offset": (
            "估计媒体视觉偏移的命令行界面"
        ),
        "Positive output means the target is later than the reference.": (
            "正数输出表示目标文件晚于参考文件。"
        ),
        "estimate visual offset between two media files": (
            "估计两个媒体文件之间的视觉偏移"
        ),
        "coarse search step in seconds (default: %(default)s)": (
            "粗略搜索步长，单位为秒（默认：%(default)s）"
        ),
        "duration to sample in seconds (default: %(default)s)": (
            "采样持续时间，单位为秒（默认：%(default)s）"
        ),
        "maximum absolute offset to search in seconds (default: %(default)s)": (
            "要搜索的最大绝对偏移，单位为秒（默认：%(default)s）"
        ),
        "reference video infile": "参考视频输入文件",
        "sample rate in frames per second (default: %(default)s)": (
            "采样率，单位为每秒帧数（默认：%(default)s）"
        ),
        "sample window count (default: %(default)s)": (
            "采样窗口数（默认：%(default)s）"
        ),
        "target video infile": "目标视频输入文件",
    },
    "zh-hant": {
        "command-line interface for estimating visual media offset": (
            "估計媒體視覺偏移的命令列介面"
        ),
        "Positive output means the target is later than the reference.": (
            "正數輸出表示目標檔晚於參考檔。"
        ),
        "estimate visual offset between two media files": (
            "估計兩個媒體檔之間的視覺偏移"
        ),
        "coarse search step in seconds (default: %(default)s)": (
            "粗略搜尋步長，單位為秒（預設：%(default)s）"
        ),
        "duration to sample in seconds (default: %(default)s)": (
            "取樣持續時間，單位為秒（預設：%(default)s）"
        ),
        "maximum absolute offset to search in seconds (default: %(default)s)": (
            "要搜尋的最大絕對偏移，單位為秒（預設：%(default)s）"
        ),
        "reference video infile": "參考影片輸入檔",
        "sample rate in frames per second (default: %(default)s)": (
            "取樣率，單位為每秒影格數（預設：%(default)s）"
        ),
        "sample window count (default: %(default)s)": (
            "取樣視窗數（預設：%(default)s）"
        ),
        "target video infile": "目標影片輸入檔",
    },
}
"""Localized help text keyed by locale and English source text."""


class MediaOffsetCli(ScinoephileCliBase):
    """Estimate visual offset between two media files.

    Positive output means the target is later than the reference.
    """

    localizations = MEDIA_OFFSET_LOCALIZATIONS
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
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--reference-infile",
            dest="reference_infile_path",
            required=True,
            type=input_file_arg(),
            help="reference video infile",
        )
        arg_groups["input arguments"].add_argument(
            "--target-infile",
            dest="target_infile_path",
            required=True,
            type=input_file_arg(),
            help="target video infile",
        )

        # Operation arguments
        positive_float_min = nextafter(0.0, 1.0)
        arg_groups["operation arguments"].add_argument(
            "--max-offset",
            default=10.0,
            type=float_arg(min_value=positive_float_min),
            help="maximum absolute offset to search in seconds (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--sample-rate",
            default=2.0,
            type=float_arg(min_value=positive_float_min),
            help="sample rate in frames per second (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--duration",
            default=300.0,
            type=float_arg(min_value=positive_float_min),
            help="duration to sample in seconds (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--coarse-step",
            default=0.25,
            type=float_arg(min_value=positive_float_min),
            help="coarse search step in seconds (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--sample-windows",
            default=4,
            type=int_arg(min_value=1),
            help="sample window count (default: %(default)s)",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "offset"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        reference_infile_path: Path,
        target_infile_path: Path,
        max_offset: float,
        sample_rate: float,
        duration: float,
        coarse_step: float,
        sample_windows: int,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        try:
            result = get_video_offset(
                reference_infile_path=reference_infile_path,
                target_infile_path=target_infile_path,
                max_offset=max_offset,
                sample_rate=sample_rate,
                duration=duration,
                coarse_step=coarse_step,
                sample_windows=sample_windows,
            )
            print(cls._get_result_description(result))
        except (ScinoephileError, ValueError) as exc:
            parser.error(str(exc))

    @staticmethod
    def _get_result_description(result: VideoOffsetResult) -> str:
        """Return a human-readable offset result.

        Arguments:
            result: video offset result
        Returns:
            human-readable result
        """
        if result.aggregate is not None:
            return MediaOffsetCli._get_window_result_description(result)

        lines = [
            f"Offset: {result.offset:+.6f} s",
            f"Frames: {result.offset_frames:+d}",
        ]
        lines.extend(
            [
                (
                    "Direction: "
                    f"{MediaOffsetCli._get_direction_description(result.offset)}"
                ),
                f"Confidence: {result.confidence}",
                f"Matched samples: {result.best.matched_count}",
                f"Best score: {result.best.score:.6f}",
            ]
        )
        if result.second_best is not None:
            lines.append(f"Next-best score: {result.second_best.score:.6f}")
        return "\n".join(lines)

    @staticmethod
    def _get_direction_description(offset: float) -> str:
        """Return a human-readable offset direction.

        Arguments:
            offset: target timestamp minus reference timestamp
        Returns:
            human-readable offset direction
        """
        if offset > 0:
            return f"target is {offset:.6f} s later than reference"
        if offset < 0:
            return f"target is {abs(offset):.6f} s earlier than reference"
        return "target is aligned with reference"

    @staticmethod
    def _get_window_result_description(result: VideoOffsetResult) -> str:
        """Return a human-readable multi-window offset result.

        Arguments:
            result: video offset result
        Returns:
            human-readable result
        """
        window_lines = [
            MediaOffsetCli._get_window_summary(index, window)
            for index, window in enumerate(result.windows, start=1)
        ]
        agg = result.aggregate
        if agg is None:
            return "\n".join(window_lines)

        aggregate_lines = [
            "",
            "Aggregate:",
            f"  Offset: {agg.offset_frames:+d} frames ({agg.offset:+.6f} s)",
            f"  Mean: {agg.mean_frames:+.2f} frames",
            f"  Median: {agg.median_frames:+d} frames",
            f"  Stdev: {agg.stdev_frames:.2f} frames",
            f"  Range: {agg.min_frames:+d} to {agg.max_frames:+d} frames",
            f"  Agreement: {agg.agreeing_count}/{agg.total_count} windows",
            f"  Confidence: {result.confidence}",
        ]
        return "\n".join([*window_lines, *aggregate_lines])

    @staticmethod
    def _get_window_summary(index: int, window: VideoOffsetWindowResult) -> str:
        """Return one formatted window result line.

        Arguments:
            index: 1-based window index
            window: video offset window result
        Returns:
            formatted window result
        """
        start = format_time_ms(int(round(window.start_time * 1000)))
        line = (
            f"Window {index}: start={start} "
            f"offset={window.offset_frames:+d} frames ({window.offset:+.6f} s), "
            f"confidence={window.confidence}, best={window.best.score:.6f}"
        )
        if window.second_best is not None:
            line = f"{line}, next={window.second_best.score:.6f}"
        return line
