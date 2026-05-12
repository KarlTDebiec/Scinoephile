#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for estimating visual media offset."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.common.argument_parsing import (
    float_arg,
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.media.video_offset import VideoOffsetResult, get_video_offset

__all__ = ["MediaOffsetCli"]


class MediaOffsetCli(ScinoephileCliBase):
    """Estimate visual offset between two media files."""

    localizations = {
        "zh-hans": {
            "command-line interface for estimating visual media offset": (
                "估计媒体视觉偏移的命令行界面"
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
            "fine search step in seconds (default: %(default)s)": (
                "精细搜索步长，单位为秒（默认：%(default)s）"
            ),
            "maximum absolute offset to search in seconds (default: %(default)s)": (
                "要搜索的最大绝对偏移，单位为秒（默认：%(default)s）"
            ),
            "reference video infile": "参考视频输入文件",
            "sample rate in frames per second (default: %(default)s)": (
                "采样率，单位为每秒帧数（默认：%(default)s）"
            ),
            "start time for sampling in seconds (default: %(default)s)": (
                "采样开始时间，单位为秒（默认：%(default)s）"
            ),
            "target video infile": "目标视频输入文件",
        },
        "zh-hant": {
            "command-line interface for estimating visual media offset": (
                "估計媒體視覺偏移的命令列介面"
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
            "fine search step in seconds (default: %(default)s)": (
                "精細搜尋步長，單位為秒（預設：%(default)s）"
            ),
            "maximum absolute offset to search in seconds (default: %(default)s)": (
                "要搜尋的最大絕對偏移，單位為秒（預設：%(default)s）"
            ),
            "reference video infile": "參考影片輸入檔",
            "sample rate in frames per second (default: %(default)s)": (
                "取樣率，單位為每秒影格數（預設：%(default)s）"
            ),
            "start time for sampling in seconds (default: %(default)s)": (
                "取樣開始時間，單位為秒（預設：%(default)s）"
            ),
            "target video infile": "目標影片輸入檔",
        },
    }
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
        arg_groups["operation arguments"].add_argument(
            "--max-offset",
            default=10.0,
            type=float_arg(min_value=0.0),
            help="maximum absolute offset to search in seconds (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--sample-rate",
            default=2.0,
            type=float_arg(min_value=0.0),
            help="sample rate in frames per second (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--start-time",
            default=0.0,
            type=float_arg(min_value=0.0),
            help="start time for sampling in seconds (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--duration",
            default=300.0,
            type=float_arg(min_value=0.0),
            help="duration to sample in seconds (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--coarse-step",
            default=0.25,
            type=float_arg(min_value=0.0),
            help="coarse search step in seconds (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--fine-step",
            default=0.04,
            type=float_arg(min_value=0.0),
            help="fine search step in seconds (default: %(default)s)",
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
        start_time: float,
        duration: float,
        coarse_step: float,
        fine_step: float,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        try:
            result = get_video_offset(
                reference_infile_path=reference_infile_path,
                target_infile_path=target_infile_path,
                max_offset=max_offset,
                sample_rate=sample_rate,
                start_time=start_time,
                duration=duration,
                coarse_step=coarse_step,
                fine_step=fine_step,
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
        lines = [
            f"Offset: {result.offset:+.3f} s",
            f"Direction: {MediaOffsetCli._get_direction_description(result.offset)}",
            f"Confidence: {result.confidence}",
            f"Matched samples: {result.best.matched_count}",
            f"Best score: {result.best.score:.6f}",
        ]
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
            return f"target is {offset:.3f} s later than reference"
        if offset < 0:
            return f"target is {abs(offset):.3f} s earlier than reference"
        return "target is aligned with reference"
