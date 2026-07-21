#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for media operations."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Any

from scinoephile.common import CommandLineInterface
from scinoephile.core.cli import ScinoephileCliBase

from .media_extract_audio_cli import MediaExtractAudioCli
from .media_extract_subs_cli import MediaExtractSubsCli
from .media_offset_cli import MediaOffsetCli
from .media_probe_cli import MediaProbeCli

__all__ = ["MediaCli"]

MEDIA_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for media operations": "媒体操作命令行界面",
        "extract matching subtitle streams from a video file": (
            "从视频文件提取匹配的字幕流"
        ),
        "extract an audio stream from a media file": "从媒体文件提取音频流",
        "estimate visual offset between two media files": (
            "估计两个媒体文件之间的视觉偏移"
        ),
        "inspect and extract media streams": "检查并提取媒体流",
        "list media streams in a media file": "列出媒体文件中的媒体流",
    },
    "zh-hant": {
        "command-line interface for media operations": "媒體操作命令列介面",
        "extract matching subtitle streams from a video file": (
            "從影片檔提取匹配的字幕流"
        ),
        "extract an audio stream from a media file": "從媒體檔提取音訊流",
        "estimate visual offset between two media files": (
            "估計兩個媒體檔之間的視覺偏移"
        ),
        "inspect and extract media streams": "檢查並提取媒體流",
        "list media streams in a media file": "列出媒體檔中的媒體流",
    },
}
"""Localized help text keyed by locale and English source text."""


class MediaCli(ScinoephileCliBase):
    """Inspect and extract media streams."""

    localizations = MEDIA_LOCALIZATIONS
    """Localized help text keyed by locale and English source text."""

    @classmethod
    def add_arguments_to_argparser(cls, parser: ArgumentParser):
        """Add arguments to a nascent argument parser.

        Arguments:
            parser: nascent argument parser
        """
        super().add_arguments_to_argparser(parser)

        subparsers = parser.add_subparsers(
            dest="media_subcommand_name",
            help="subcommand",
            required=True,
        )
        subcommands = cls.subcommands()
        for name in sorted(subcommands):
            subcommands[name].argparser(subparsers=subparsers)

    @classmethod
    def subcommands(cls) -> dict[str, type[CommandLineInterface]]:
        """Names and types of tools wrapped by command-line interface.

        Returns:
            mapping of subcommand names to CLI classes
        """
        return {
            MediaExtractAudioCli.name(): MediaExtractAudioCli,
            MediaExtractSubsCli.name(): MediaExtractSubsCli,
            MediaOffsetCli.name(): MediaOffsetCli,
            MediaProbeCli.name(): MediaProbeCli,
        }

    @classmethod
    def _main(
        cls,
        *,
        media_subcommand_name: str,
        **kwargs: Any,
    ):
        """Execute with provided keyword arguments."""
        cls.subcommands()[media_subcommand_name]._main(**kwargs)


if __name__ == "__main__":
    MediaCli.main()
