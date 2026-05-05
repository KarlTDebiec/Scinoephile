#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for extracting subtitle streams from media."""

from __future__ import annotations

from argparse import ArgumentParser
from logging import getLogger
from pathlib import Path

from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    output_dir_arg,
)
from scinoephile.common.exception import ArgumentConflictError
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.argument_types import language_arg
from scinoephile.core.media import SubtitleStream
from scinoephile.core.media.constants import DEFAULT_SUBTITLE_LANGUAGES
from scinoephile.core.media.subtitles import (
    extract_subtitle_stream,
    get_subtitle_output_path,
    get_subtitle_streams,
)

__all__ = ["ExtractCli"]

logger = getLogger(__name__)


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
            "--overwrite",
            action="store_true",
            help="overwrite extracted subtitle files if they exist",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "--details",
            action="store_true",
            help="include additional subtitle stream details",
        )
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
        overwrite: bool,
        output_dir_path: Path | None,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if export and output_dir_path is None:
            try:
                raise ArgumentConflictError("--export requires --output-dir")
            except ArgumentConflictError as exc:
                parser.error(str(exc))
        if overwrite and not export:
            try:
                raise ArgumentConflictError("--overwrite requires --export")
            except ArgumentConflictError as exc:
                parser.error(str(exc))
        language_codes = {language.lower() for language in languages}

        # Perform operations
        try:
            for stream in get_subtitle_streams(infile_path, counts=details):
                # Stream language is missing or not requested
                if (
                    stream.language is None
                    or stream.language.lower() not in language_codes
                ):
                    continue

                details_text = cls._get_details_text(stream) if details else ""
                if output_dir_path is None:
                    logger.info(
                        f"[o] Stream #0:{stream.index}({stream.language}): "
                        f"Subtitle: {stream.codec_name}{details_text}"
                    )
                    continue

                outfile_path = get_subtitle_output_path(output_dir_path, stream)
                # Matching stream was already extracted
                if outfile_path.exists() and not overwrite:
                    logger.info(
                        f"[x] Stream #0:{stream.index}({stream.language}): "
                        f"Subtitle: {stream.codec_name}{details_text} -> "
                        f"{outfile_path}"
                    )
                    continue

                # Matching stream should be extracted
                logger.info(
                    f"[o] Stream #0:{stream.index}({stream.language}): Subtitle: "
                    f"{stream.codec_name}{details_text} -> {outfile_path}"
                )
                if export:
                    extract_subtitle_stream(
                        infile_path,
                        stream,
                        outfile_path,
                    )
        except ScinoephileError as exc:
            parser.error(str(exc))

    @staticmethod
    def _get_details_text(stream: SubtitleStream) -> str:
        """Format additional stream details for list output.

        Arguments:
            stream: subtitle stream to describe
        Returns:
            formatted detail suffix
        """
        details = [f"extension={stream.extension}"]
        if stream.title is not None:
            details.append(f"title={stream.title}")
        if stream.forced:
            details.append("forced")
        if stream.sdh:
            details.append("sdh")
        if stream.subtitle_count is None:
            details.append("subtitles=unavailable")
        else:
            details.append(f"subtitles={stream.subtitle_count}")
        return f" ({', '.join(details)})"


if __name__ == "__main__":
    ExtractCli.main()
