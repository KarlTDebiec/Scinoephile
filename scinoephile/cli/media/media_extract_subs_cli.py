#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for extracting subtitle streams from media."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path
from shutil import copy2

from scinoephile.cli.cache.argument_types import cache_dir_path_arg
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_dir_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.argument_types import language_arg
from scinoephile.core.media import SubtitleStream
from scinoephile.image.subtitles import ImageSeries
from scinoephile.media.constants import DEFAULT_SUBTITLE_LANGUAGES
from scinoephile.media.probe import get_subtitle_streams
from scinoephile.media.subtitle_analysis import (
    cache_subtitle_stream_artifacts,
    with_stream_details,
)
from scinoephile.media.subtitle_analysis import (
    extract_subtitle_stream_from_cache as extract_subtitle_stream,
)

__all__ = ["MediaExtractSubsCli"]

logger = getLogger(__name__)


class MediaExtractSubsCli(ScinoephileCliBase):
    """Extract matching subtitle streams from a video file."""

    localizations = {
        "zh-hans": {
            "convert extracted SUP subtitle streams to image directories": (
                "将提取的 SUP 字幕流转换为图像目录"
            ),
            "cache directory (default: %(default)s)": ("缓存目录（默认：%(default)s）"),
            "directory to which matching subtitles will be extracted or mapped": (
                "匹配字幕将被提取或映射到的目录"
            ),
            "extract matching subtitle streams from a video file": (
                "从视频文件提取匹配的字幕流"
            ),
            "include additional subtitle stream details": "包含更多字幕流详细信息",
            "ISO 639 language codes to extract (default: chi eng yue zho)": (
                "要提取的 ISO 639 语言代码（默认：chi eng yue zho）"
            ),
            "overwrite extracted subtitle files if they exist": (
                "若提取的字幕文件已存在则覆盖"
            ),
            "video infile containing subtitle streams": "包含字幕流的视频输入文件",
        },
        "zh-hant": {
            "convert extracted SUP subtitle streams to image directories": (
                "將提取的 SUP 字幕流轉換為影像目錄"
            ),
            "cache directory (default: %(default)s)": ("快取目錄（預設：%(default)s）"),
            "directory to which matching subtitles will be extracted or mapped": (
                "匹配字幕將被提取或映射到的目錄"
            ),
            "extract matching subtitle streams from a video file": (
                "從影片檔提取匹配的字幕流"
            ),
            "include additional subtitle stream details": "包含更多字幕流詳細資訊",
            "ISO 639 language codes to extract (default: chi eng yue zho)": (
                "要提取的 ISO 639 語言代碼（預設：chi eng yue zho）"
            ),
            "overwrite extracted subtitle files if they exist": (
                "若提取的字幕檔已存在則覆寫"
            ),
            "video infile containing subtitle streams": "包含字幕流的影片輸入檔",
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
            "output arguments",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--infile",
            dest="infile_path",
            required=True,
            type=input_file_arg(),
            help="video infile containing subtitle streams",
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--languages",
            default=list(DEFAULT_SUBTITLE_LANGUAGES),
            nargs="+",
            type=language_arg,
            help=("ISO 639 language codes to extract (default: chi eng yue zho)"),
        )
        arg_groups["operation arguments"].add_argument(
            "--details",
            action="store_true",
            help="include additional subtitle stream details",
        )
        arg_groups["operation arguments"].add_argument(
            "--cache-dir",
            default=cache_dir_path_arg(None),
            dest="cache_dir_path",
            type=cache_dir_path_arg,
            help="cache directory (default: %(default)s)",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--output-dir",
            dest="output_dir_path",
            required=True,
            type=output_dir_arg(create=False),
            help="directory to which matching subtitles will be extracted or mapped",
        )
        arg_groups["output arguments"].add_argument(
            "--extract-sup",
            action="store_true",
            help="convert extracted SUP subtitle streams to image directories",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite extracted subtitle files if they exist",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "extract-subs"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        infile_path: Path,
        languages: list[str],
        details: bool,
        cache_dir_path: Path,
        extract_sup: bool,
        overwrite: bool,
        output_dir_path: Path,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if not output_dir_path.exists():
            output_dir_path.mkdir(parents=True)
            logger.info(f"Created subtitle output directory: {output_dir_path}")
        language_codes = set(languages)

        # Perform operations
        try:
            if infile_path.suffix.lower() == ".sup":
                streams = get_subtitle_streams(
                    infile_path,
                )
                if details:
                    streams = cls._with_stream_details(
                        infile_path,
                        streams,
                        cache_dir_path=cache_dir_path,
                    )
                if not streams:
                    raise ScinoephileError(
                        f"No subtitle streams found in {infile_path}"
                    )
                stream = streams[0]
                cls._handle_sup(
                    infile_path,
                    stream,
                    output_dir_path,
                    extract_sup,
                    overwrite,
                )
                return

            subtitle_streams = get_subtitle_streams(
                infile_path,
            )
            if details:
                subtitle_streams = cls._with_stream_details(
                    infile_path,
                    subtitle_streams,
                    cache_dir_path=cache_dir_path,
                )
            streams = []
            for stream in subtitle_streams:
                if _language_matches(stream.language, language_codes):
                    streams.append(stream)
            cache_subtitle_stream_artifacts(
                infile_path,
                streams,
                cache_dir_path=cache_dir_path,
            )

            for stream in streams:
                cls._handle_stream(
                    infile_path,
                    stream,
                    output_dir_path,
                    extract_sup,
                    overwrite,
                    cache_dir_path=cache_dir_path,
                )
        except ScinoephileError as exc:
            parser.error(str(exc))

    @staticmethod
    def _handle_stream(
        infile_path: Path,
        stream: SubtitleStream,
        output_dir_path: Path,
        extract_sup: bool,
        overwrite: bool,
        *,
        cache_dir_path: Path,
    ):
        """Handle one matching subtitle stream.

        Arguments:
            infile_path: media input file
            stream: subtitle stream to extract
            output_dir_path: output directory, if provided
            extract_sup: whether to extract SUP subtitles
            overwrite: whether to overwrite existing outputs
            cache_dir_path: cache directory path
        """
        # Determine output path
        outfile_path = output_dir_path / stream.outfile_filename

        # Output, if applicable
        if outfile_path.exists():
            if overwrite:
                extract_subtitle_stream(
                    infile_path,
                    stream,
                    outfile_path,
                    cache_dir_path=cache_dir_path,
                )
            description = _get_subtitle_stream_description(stream)
            print(f"[x] {description} -> {outfile_path}")
        else:
            description = _get_subtitle_stream_description(stream)
            print(f"[ ] {description} -> {outfile_path}")
            extract_subtitle_stream(
                infile_path,
                stream,
                outfile_path,
                cache_dir_path=cache_dir_path,
            )
            print(f"[x] {description} -> {outfile_path}")

        # Output directory, if applicable
        if stream.extension == "sup" and extract_sup:
            output_image_dir_path = outfile_path.with_suffix("")
            if output_image_dir_path.exists():
                if overwrite:
                    ImageSeries.load(outfile_path).save(output_image_dir_path)
                print(f"[ ] {description} -> {output_image_dir_path}")
            else:
                print(f"[ ] {description} -> {output_image_dir_path}")
                ImageSeries.load(outfile_path).save(output_image_dir_path)
                print(f"[x] {description} -> {output_image_dir_path}")

    @staticmethod
    def _handle_sup(
        infile_path: Path,
        stream: SubtitleStream,
        output_dir_path: Path,
        extract_sup: bool,
        overwrite: bool,
    ):
        """Handle sup file.

        Arguments:
            infile_path: media input file
            stream: subtitle stream to extract
            output_dir_path: output directory, if provided
            extract_sup: whether to extract SUP subtitles
            overwrite: whether to overwrite existing outputs
        """
        # Determine output path
        outfile_name = infile_path.name
        if stream.language is not None and "-" in stream.language:
            outfile_name = f"{stream.language}{infile_path.suffix}"
        outfile_path = output_dir_path / outfile_name
        outfile_is_infile = outfile_path.resolve() == infile_path.resolve()

        # Output, if applicable
        if outfile_path.exists():
            if overwrite and not outfile_is_infile:
                copy2(infile_path, outfile_path)
            description = _get_subtitle_stream_description(stream)
            print(f"[x] {description} -> {outfile_path}")
        else:
            description = _get_subtitle_stream_description(stream)
            print(f"[ ] {description} -> {outfile_path}")
            if not outfile_is_infile:
                copy2(infile_path, outfile_path)
                print(f"[x] {description} -> {outfile_path}")

        # Output directory, if applicable
        if stream.extension == "sup" and extract_sup:
            output_image_dir_path = output_dir_path / infile_path.stem
            if output_image_dir_path.exists():
                if overwrite:
                    ImageSeries.load(outfile_path).save(output_image_dir_path)
                print(f"[ ] {description} -> {output_image_dir_path}")
            else:
                print(f"[ ] {description} -> {output_image_dir_path}")
                ImageSeries.load(outfile_path).save(output_image_dir_path)
                print(f"[x] {description} -> {output_image_dir_path}")

    @staticmethod
    def _with_stream_details(
        infile_path: Path,
        streams: list[SubtitleStream],
        *,
        cache_dir_path: Path,
    ) -> list[SubtitleStream]:
        """Return subtitle streams enriched with details.

        Arguments:
            infile_path: media input file
            streams: subtitle streams to enrich
            cache_dir_path: cache directory path
        Returns:
            enriched subtitle streams
        """
        return [
            stream
            for stream in with_stream_details(
                infile_path,
                streams,
                cache_dir_path=cache_dir_path,
            )
            if isinstance(stream, SubtitleStream)
        ]


def _get_subtitle_stream_description(stream: SubtitleStream) -> str:
    """Return extraction-oriented subtitle stream description.

    Arguments:
        stream: subtitle stream
    Returns:
        subtitle stream description
    """
    description = f"Stream {stream.stream_id}: Subtitle: {stream.codec_name}"
    details = [f"extension={stream.extension}"]
    if stream.title is not None:
        details.append(f"title={stream.title}")
    if stream.forced:
        details.append("forced")
    if stream.sdh:
        details.append("sdh")
    if stream.subtitle_count is not None:
        details.append(f"subtitles={stream.subtitle_count}")
    if stream.span is not None:
        details.append(f"span={stream.span}")
    return f"{description} ({', '.join(details)})"


def _language_matches(language: str | None, language_codes: set[str]) -> bool:
    """Return whether a stream language matches requested language codes.

    Arguments:
        language: stream language tag, if available
        language_codes: requested base language codes
    Returns:
        whether the language tag matches
    """
    if language is None:
        return False
    return language.split("-", 1)[0] in language_codes


if __name__ == "__main__":
    MediaExtractSubsCli.main()
