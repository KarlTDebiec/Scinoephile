#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for probing media streams."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.cli.helpers.cache import (
    CACHE_LOCALIZATIONS,
    CacheArguments,
    add_cache_args,
)
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.core.media import SubtitleStream
from scinoephile.lang.zho.subtitles.analysis import analyze_zho_subtitle_stream_script
from scinoephile.lang.zho.subtitles.streams import get_zho_subtitle_streams
from scinoephile.media.probe import get_streams

__all__ = ["MediaProbeCli"]

MEDIA_PROBE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for probing media streams": "探测媒体流的命令行界面",
        "force Chinese script analysis for a standalone SUP infile": (
            "对独立 SUP 输入文件强制执行中文脚本分析"
        ),
        "list media streams in a media file": "列出媒体文件中的媒体流",
        "include additional stream details": "包含更多媒体流详细信息",
        "video infile containing media streams": "包含媒体流的视频输入文件",
    },
    "zh-hant": {
        "command-line interface for probing media streams": "探測媒體流的命令列介面",
        "force Chinese script analysis for a standalone SUP infile": (
            "對獨立 SUP 輸入檔強制執行中文腳本分析"
        ),
        "list media streams in a media file": "列出媒體檔中的媒體流",
        "include additional stream details": "包含更多媒體流詳細資訊",
        "video infile containing media streams": "包含媒體流的影片輸入檔",
    },
}
"""Localized help text keyed by locale and English source text."""


class MediaProbeCli(ScinoephileCliBase):
    """List media streams in a media file."""

    localizations = merge_localizations(CACHE_LOCALIZATIONS, MEDIA_PROBE_LOCALIZATIONS)
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
            "cache arguments",
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
            "--force-check-script",
            action="store_true",
            help="force Chinese script analysis for a standalone SUP infile",
        )

        # Cache arguments
        add_cache_args(arg_groups["cache arguments"])
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
        force_check_script: bool,
        cache_args: CacheArguments,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if force_check_script and infile_path.suffix.lower() != ".sup":
            parser.error("--force-check-script requires a SUP infile")

        # Perform operations
        try:
            if force_check_script:
                stream = SubtitleStream(
                    index=0,
                    codec_type="subtitle",
                    codec_name="hdmv_pgs_subtitle",
                    language="zho",
                )
                analysis = analyze_zho_subtitle_stream_script(
                    infile_path,
                    stream,
                    cache_dir_path=cache_args.dir_path,
                    overwrite_cache=cache_args.overwrite,
                )
                language = analysis.script
                if language is None:
                    language = "zho-Unknown"
                stream.language = language
                streams = [stream]
            else:
                streams = get_streams(infile_path)
                if details:
                    detailed_subtitle_streams_by_index = {
                        stream.index: stream
                        for stream in get_zho_subtitle_streams(
                            infile_path,
                            cache_dir_path=cache_args.dir_path,
                            overwrite_cache=cache_args.overwrite,
                            streams=streams,
                        )
                    }
                    for index, stream in enumerate(streams):
                        if isinstance(stream, SubtitleStream):
                            streams[index] = detailed_subtitle_streams_by_index.get(
                                stream.index,
                                stream,
                            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write outputs
        for stream in streams:
            print(stream.description)


if __name__ == "__main__":
    MediaProbeCli.main()
