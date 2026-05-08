#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for probing media streams."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Any

import ffmpeg

from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase

__all__ = ["MediaProbeCli"]


class MediaProbeCli(ScinoephileCliBase):
    """List media streams in a media file."""

    localizations = {
        "zh-hans": {
            "command-line interface for probing media streams": (
                "探测媒体流的命令行界面"
            ),
            "list media streams in a media file": "列出媒体文件中的媒体流",
            "video infile containing media streams": "包含媒体流的视频输入文件",
        },
        "zh-hant": {
            "command-line interface for probing media streams": (
                "探測媒體流的命令列介面"
            ),
            "list media streams in a media file": "列出媒體檔中的媒體流",
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
            optional_arguments_name="additional arguments",
        )

        arg_groups["input arguments"].add_argument(
            "--infile",
            dest="infile_path",
            required=True,
            type=input_file_arg(),
            help="video infile containing media streams",
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
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        try:
            probe = ffmpeg.probe(str(infile_path), count_packets=None)
            for stream in probe.get("streams", []):
                if isinstance(stream, dict):
                    print(_get_stream_description(stream))
        except ffmpeg.Error:
            parser.error(
                str(ScinoephileError(f"Could not probe media file {infile_path}"))
            )
        except ScinoephileError as exc:
            parser.error(str(exc))


def _get_stream_description(stream: dict[str, Any]) -> str:
    """Return a human-readable description of one ffprobe stream.

    Arguments:
        stream: ffprobe stream object
    Returns:
        human-readable stream description
    """
    index = stream.get("index", "?")
    codec_type = stream.get("codec_type", "unknown")
    codec_name = stream.get("codec_name", codec_type)

    tags = stream.get("tags")
    if not isinstance(tags, dict):
        tags = {}
    language = tags.get("language")
    if isinstance(language, str) and language:
        stream_id = f"#0:{index}({language})"
    else:
        stream_id = f"#0:{index}"

    details = _get_stream_details(stream, tags)
    description = f"Stream {stream_id}: {str(codec_type).title()}: {codec_name}"
    if details:
        description = f"{description} ({', '.join(details)})"
    return description


def _get_stream_details(stream: dict[str, Any], tags: dict[str, Any]) -> list[str]:
    """Return detail strings for one ffprobe stream.

    Arguments:
        stream: ffprobe stream object
        tags: ffprobe stream tags
    Returns:
        stream detail strings
    """
    details = []

    width = stream.get("width")
    height = stream.get("height")
    if isinstance(width, int) and isinstance(height, int):
        details.append(f"{width}x{height}")

    channels = stream.get("channels")
    if isinstance(channels, int):
        details.append(f"channels={channels}")

    title = tags.get("title")
    if isinstance(title, str) and title:
        details.append(f"title={title}")

    packet_count = stream.get("nb_read_packets")
    if isinstance(packet_count, int | str):
        details.append(f"packets={packet_count}")

    return details


if __name__ == "__main__":
    MediaProbeCli.main()
