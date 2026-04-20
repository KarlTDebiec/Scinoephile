#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for 粤文 subtitle transcription."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Unpack

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from scinoephile.common.exception import ArgumentConflictError, NotAFileError
from scinoephile.common.file import get_temp_file_path
from scinoephile.core.cli import read_series, write_series
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.multilang.yue_zho.transcription import get_yue_transcribed_vs_zho


class YueTranscribeCli(CommandLineInterface):
    """Command-line interface for 粤文 subtitle transcription."""

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
            "--media-infile",
            required=True,
            type=str,
            help=(
                "video or audio media input path used for transcription or '-' "
                "for stdin"
            ),
        )
        arg_groups["input arguments"].add_argument(
            "--stream-index",
            type=int_arg(min_value=0),
            default=0,
            help="audio stream index in media input (default: 0)",
        )
        arg_groups["input arguments"].add_argument(
            "--zhongwen-infile",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='中文 subtitle infile or "-" for stdin',
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            default=None,
            type=output_file_arg(),
            help="粤文 subtitle outfile path (default: stdout)",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "transcribe"

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        # Validate arguments
        parser = kwargs.pop("_parser", cls.argparser())
        media_infile_path = kwargs.pop("media_infile")
        zhongwen_infile_path = kwargs.pop("zhongwen_infile")
        stream_index = kwargs.pop("stream_index")
        outfile_path: Path | None = kwargs.pop("outfile")
        overwrite = kwargs.pop("overwrite")
        if media_infile_path == "-" and zhongwen_infile_path == "-":
            try:
                raise ArgumentConflictError(
                    "--media-infile and --zhongwen-infile may not both be '-'"
                )
            except ArgumentConflictError as exc:
                parser.error(str(exc))
        if overwrite and outfile_path is None:
            try:
                raise ArgumentConflictError(
                    "--overwrite may only be used with --outfile"
                )
            except ArgumentConflictError as exc:
                parser.error(str(exc))

        # Read inputs
        if zhongwen_infile_path == "-":
            zhongwen = read_series(parser, "-", allow_stdin=True)
            with get_temp_file_path(suffix=".srt") as temp_zhongwen_path:
                zhongwen.save(temp_zhongwen_path)
                try:
                    yuewen = AudioSeries.load_from_media(
                        media_path=media_infile_path,
                        subtitle_path=temp_zhongwen_path,
                        stream_index=stream_index,
                    )
                except (FileNotFoundError, NotAFileError, ScinoephileError) as exc:
                    parser.error(str(exc))
        else:
            zhongwen = read_series(parser, zhongwen_infile_path, allow_stdin=True)
            try:
                yuewen = AudioSeries.load_from_media(
                    media_path=media_infile_path,
                    subtitle_path=zhongwen_infile_path,
                    stream_index=stream_index,
                )
            except (FileNotFoundError, NotAFileError, ScinoephileError) as exc:
                parser.error(str(exc))

        # Perform operations
        yuewen = get_yue_transcribed_vs_zho(yuewen=yuewen, zhongwen=zhongwen)

        # Write outputs
        write_series(
            parser, yuewen, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    YueTranscribeCli.main()
