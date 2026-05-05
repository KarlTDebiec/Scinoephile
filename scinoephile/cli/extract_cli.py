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
from scinoephile.core.media.subtitles import (
    extract_subtitle_stream,
    get_subtitle_streams,
)
from scinoephile.image.subtitles import ImageSeries

__all__ = ["ExtractCli"]


class ExtractCli(ScinoephileCliBase):
    """Extract matching subtitle streams from a video file."""

    localizations = {
        "zh-hans": {
            "extract matching subtitle streams from a video file": (
                "从视频文件提取匹配的字幕流"
            ),
        },
        "zh-hant": {
            "extract matching subtitle streams from a video file": (
                "從影片檔提取匹配的字幕流"
            ),
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
            help=("ISO 639 language codes to extract (default: chi eng zho yue)"),
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
            type=output_dir_arg(),
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
        language_codes = set(languages)

        # Perform operations
        try:
            if infile_path.suffix.lower() == ".sup":
                streams = get_subtitle_streams(infile_path, counts=details)
                if not streams:
                    raise ScinoephileError(
                        f"No subtitle streams found in {infile_path}"
                    )
                stream = streams[0]
                cls._handle_sup(
                    infile_path,
                    stream,
                    export,
                    output_dir_path,
                    extract_sup,
                    overwrite,
                )
                return

            for stream in get_subtitle_streams(infile_path, counts=details):
                if stream.language not in language_codes:
                    continue

                cls._handle_stream(
                    infile_path,
                    stream,
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
        outfile_path = output_dir_path / infile_path.name

        # Output, if applicable
        if outfile_path.exists():
            if overwrite:
                copy2(infile_path, outfile_path)
            print(f"[x] {stream.description} -> {outfile_path}")
        else:
            print(f"[ ] {stream.description} -> {outfile_path}")
            if export:
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
    ExtractCli.main()
