#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for extracting subtitle streams from media."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from shutil import copy2

from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_dir_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.argument_types import language_arg
from scinoephile.core.media import SubtitleStream
from scinoephile.core.media.constants import DEFAULT_SUBTITLE_LANGUAGES
from scinoephile.core.media.subtitle_analysis import (
    analyze_subtitle_stream_script,
    cache_subtitle_stream_artifacts,
)
from scinoephile.core.media.subtitle_analysis import (
    extract_subtitle_stream_from_cache as extract_subtitle_stream,
)
from scinoephile.core.media.subtitles import get_subtitle_streams
from scinoephile.image.subtitles import ImageSeries

__all__ = ["MediaExtractSubsCli"]


class MediaExtractSubsCli(ScinoephileCliBase):
    """Extract matching subtitle streams from a video file."""

    localizations = {
        "zh-hans": {
            "convert extracted SUP subtitle streams to image directories": (
                "将提取的 SUP 字幕流转换为图像目录"
            ),
            "directory to which matching subtitles will be extracted or mapped": (
                "匹配字幕将被提取或映射到的目录"
            ),
            "extract matching subtitle streams": "提取匹配的字幕流",
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
            "directory to which matching subtitles will be extracted or mapped": (
                "匹配字幕將被提取或映射到的目錄"
            ),
            "extract matching subtitle streams": "提取匹配的字幕流",
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

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "--export",
            action="store_true",
            help="extract matching subtitle streams",
        )
        arg_groups["output arguments"].add_argument(
            "-o",
            "--output-dir",
            dest="output_dir_path",
            default=None,
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
        export: bool,
        extract_sup: bool,
        overwrite: bool,
        output_dir_path: Path | None,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if export and output_dir_path is None:
            parser.error("--export requires --output-dir")
        if extract_sup and not export:
            parser.error("--extract-sup requires --export")
        if overwrite and not export:
            parser.error("--overwrite requires --export")
        if export and output_dir_path is not None:
            output_dir_path.mkdir(parents=True, exist_ok=True)
        language_codes = set(languages)

        # Perform operations
        try:
            if infile_path.suffix.lower() == ".sup":
                streams = get_subtitle_streams(infile_path, counts=False)
                if not streams:
                    raise ScinoephileError(
                        f"No subtitle streams found in {infile_path}"
                    )
                stream = streams[0]
                if details:
                    analysis = analyze_subtitle_stream_script(infile_path, stream)
                    stream = stream.with_script(analysis.script)
                cls._handle_sup(
                    infile_path,
                    stream,
                    export,
                    output_dir_path,
                    extract_sup,
                    overwrite,
                )
                return

            streams = [
                stream
                for stream in get_subtitle_streams(infile_path, counts=False)
                if stream.language in language_codes
            ]
            if export:
                cache_subtitle_stream_artifacts(infile_path, streams)
            elif details:
                cache_subtitle_stream_artifacts(
                    infile_path,
                    [stream for stream in streams if stream.is_chinese],
                )

            for stream in streams:
                handled_stream = stream
                if details:
                    analysis = analyze_subtitle_stream_script(infile_path, stream)
                    handled_stream = stream.with_script(analysis.script)
                cls._handle_stream(
                    infile_path,
                    handled_stream,
                    export,
                    output_dir_path,
                    extract_sup,
                    overwrite,
                )
        except ScinoephileError as exc:
            parser.error(str(exc))

    @staticmethod
    def _handle_stream(
        infile_path: Path,
        stream: SubtitleStream,
        export: bool,
        output_dir_path: Path | None,
        extract_sup: bool,
        overwrite: bool,
    ):
        """Handle one matching subtitle stream.

        Arguments:
            infile_path: media input file
            stream: subtitle stream to extract
            export: whether to extract subtitles
            output_dir_path: output directory, if provided
            extract_sup: whether to extract SUP subtitles
            overwrite: whether to overwrite existing outputs
        """
        # Not extracting anything
        if output_dir_path is None:
            print(f"[ ] {stream.description}")
            return

        # Determine output path
        outfile_path = output_dir_path / stream.outfile_filename

        # Output, if applicable
        if outfile_path.exists():
            if overwrite:
                extract_subtitle_stream(infile_path, stream, outfile_path)
            print(f"[x] {stream.description} -> {outfile_path}")
        else:
            print(f"[ ] {stream.description} -> {outfile_path}")
            if export:
                extract_subtitle_stream(infile_path, stream, outfile_path)
                print(f"[x] {stream.description} -> {outfile_path}")

        # Output directory, if applicable
        if stream.extension == "sup" and extract_sup:
            output_image_dir_path = outfile_path.with_suffix("")
            if output_image_dir_path.exists():
                if overwrite:
                    ImageSeries.load(outfile_path).save(output_image_dir_path)
                print(f"[ ] {stream.description} -> {output_image_dir_path}")
            else:
                print(f"[ ] {stream.description} -> {output_image_dir_path}")
                if export:
                    ImageSeries.load(outfile_path).save(output_image_dir_path)
                    print(f"[x] {stream.description} -> {output_image_dir_path}")

    @staticmethod
    def _handle_sup(
        infile_path: Path,
        stream: SubtitleStream,
        export: bool,
        output_dir_path: Path | None,
        extract_sup: bool,
        overwrite: bool,
    ):
        """Handle sup file.

        Arguments:
            infile_path: media input file
            stream: subtitle stream to extract
            export: whether to extract subtitles
            output_dir_path: output directory, if provided
            extract_sup: whether to extract SUP subtitles
            overwrite: whether to overwrite existing outputs
        """
        # Not extracting anything
        if output_dir_path is None:
            print(f"[ ] {stream.description}")
            return

        # Determine output path
        outfile_name = infile_path.name
        if stream.script is not None:
            outfile_name = f"{stream.script}{infile_path.suffix}"
        outfile_path = output_dir_path / outfile_name
        outfile_is_infile = outfile_path.resolve() == infile_path.resolve()

        # Output, if applicable
        if outfile_path.exists():
            if overwrite and not outfile_is_infile:
                copy2(infile_path, outfile_path)
            print(f"[x] {stream.description} -> {outfile_path}")
        else:
            print(f"[ ] {stream.description} -> {outfile_path}")
            if export and not outfile_is_infile:
                copy2(infile_path, outfile_path)
                print(f"[x] {stream.description} -> {outfile_path}")

        # Output directory, if applicable
        if stream.extension == "sup" and extract_sup:
            output_image_dir_path = output_dir_path / infile_path.stem
            if output_image_dir_path.exists():
                if overwrite:
                    ImageSeries.load(outfile_path).save(output_image_dir_path)
                print(f"[ ] {stream.description} -> {output_image_dir_path}")
            else:
                print(f"[ ] {stream.description} -> {output_image_dir_path}")
                if export:
                    ImageSeries.load(outfile_path).save(output_image_dir_path)
                    print(f"[x] {stream.description} -> {output_image_dir_path}")


if __name__ == "__main__":
    MediaExtractSubsCli.main()
