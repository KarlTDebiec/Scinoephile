#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for 粤文 subtitle transcription."""

from __future__ import annotations

from argparse import ArgumentParser
from contextlib import ExitStack
from pathlib import Path
from sys import stdin
from typing import Unpack

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    int_arg,
    output_file_arg,
)
from scinoephile.common.exception import ArgumentConflictError, NotAFileError
from scinoephile.common.file import get_temp_file_path
from scinoephile.common.validation import val_input_path
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import read_series, write_series
from scinoephile.core.subtitles import Series
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
            metavar="MEDIA_INFILE",
            required=True,
            type=str,
            help=(
                "video or audio media input path used for transcription or '-' "
                "for stdin"
            ),
        )
        arg_groups["input arguments"].add_argument(
            "--zhongwen-infile",
            metavar="ZHONGWEN_INFILE",
            required=True,
            type=str,
            help='中文字幕 subtitle infile or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--stream-index",
            metavar="N",
            type=int_arg(min_value=0),
            default=0,
            help="audio stream index in media input (default: 0)",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            metavar="OUTFILE",
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

        with ExitStack() as exit_stack:
            try:
                if zhongwen_infile_path == "-":
                    zhongwen = read_series(parser, "-", allow_stdin=True)
                    validated_zhongwen_path = exit_stack.enter_context(
                        get_temp_file_path(".srt")
                    )
                    zhongwen.save(validated_zhongwen_path)
                else:
                    validated_zhongwen_path = val_input_path(zhongwen_infile_path)
                    zhongwen = Series.load(validated_zhongwen_path)

                if media_infile_path == "-":
                    media_infile_temp_path = exit_stack.enter_context(
                        get_temp_file_path(".media")
                    )
                    media_stdin = getattr(stdin, "buffer", stdin)
                    media_bytes = media_stdin.read()
                    if isinstance(media_bytes, str):
                        media_bytes = media_bytes.encode()
                    Path(media_infile_temp_path).write_bytes(media_bytes)
                    validated_media_path = media_infile_temp_path
                else:
                    validated_media_path = media_infile_path

                yuewen = AudioSeries.load_from_media(
                    media_path=validated_media_path,
                    subtitle_path=validated_zhongwen_path,
                    stream_index=stream_index,
                )
                yuewen = get_yue_transcribed_vs_zho(
                    yuewen=yuewen,
                    zhongwen=zhongwen,
                )
            except (FileNotFoundError, NotAFileError, ScinoephileError) as exc:
                parser.error(str(exc))

        # Write outputs
        write_series(
            parser, yuewen, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    YueTranscribeCli.main()
