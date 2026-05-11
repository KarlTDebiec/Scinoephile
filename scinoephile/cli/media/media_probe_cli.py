#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for probing media streams."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.cache.argument_types import cache_dir_path_arg
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.media.probe import get_streams
from scinoephile.media.subtitles.details import with_stream_details

__all__ = ["MediaProbeCli"]


class MediaProbeCli(ScinoephileCliBase):
    """List media streams in a media file."""

    localizations = {
        "zh-hans": {
            "command-line interface for probing media streams": (
                "探测媒体流的命令行界面"
            ),
            "cache directory (default: %(default)s)": ("缓存目录（默认：%(default)s）"),
            "list media streams in a media file": "列出媒体文件中的媒体流",
            "include additional stream details": "包含更多媒体流详细信息",
            "video infile containing media streams": "包含媒体流的视频输入文件",
        },
        "zh-hant": {
            "command-line interface for probing media streams": (
                "探測媒體流的命令列介面"
            ),
            "cache directory (default: %(default)s)": ("快取目錄（預設：%(default)s）"),
            "list media streams in a media file": "列出媒體檔中的媒體流",
            "include additional stream details": "包含更多媒體流詳細資訊",
            "video infile containing media streams": "包含媒體流的影片輸入檔",
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
            "--infile",
            dest="infile_path",
            required=True,
            type=input_file_arg(),
            help="video infile containing media streams",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--details",
            action="store_true",
            help="include additional stream details",
        )
        arg_groups["operation arguments"].add_argument(
            "--cache-dir",
            default=cache_dir_path_arg(None),
            dest="cache_dir_path",
            type=cache_dir_path_arg,
            help="cache directory (default: %(default)s)",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "probe"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        infile_path: Path,
        details: bool,
        cache_dir_path: Path,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        try:
            streams = get_streams(infile_path)
            if details:
                streams = with_stream_details(
                    infile_path,
                    streams,
                    cache_dir_path=cache_dir_path,
                )
            for stream in streams:
                print(stream.description)
        except ScinoephileError as exc:
            parser.error(str(exc))


if __name__ == "__main__":
    MediaProbeCli.main()
