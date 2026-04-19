#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for 粤文 transcription."""

from __future__ import annotations

from argparse import ArgumentParser
from typing import Unpack

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common import CLIKwargs, CommandLineInterface
from scinoephile.common.argument_parsing import get_arg_groups_by_name, int_arg
from scinoephile.common.exception import NotAFileError
from scinoephile.common.validation import val_input_path
from scinoephile.core import ScinoephileError
from scinoephile.core.subtitles import Series
from scinoephile.multilang.yue_zho.transcription import get_yue_transcribed_vs_zho

from .subtitles_io import (
    parser_error_from_exception,
    write_subtitle_series,
)


class YueTranscribeCli(CommandLineInterface):
    """Command-line interface for 粤文 transcription."""

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

        arg_groups["input arguments"].add_argument(
            "media_infile",
            metavar="MEDIA_INFILE",
            type=str,
            help="video or audio media input path used for transcription",
        )
        arg_groups["input arguments"].add_argument(
            "zhongwen_infile",
            metavar="ZHONGWEN_INFILE",
            type=str,
            help="中文字幕 subtitle infile",
        )

        arg_groups["operation arguments"].add_argument(
            "--stream-index",
            metavar="N",
            type=int_arg(min_value=0),
            default=0,
            help="audio stream index in media input (default: 0)",
        )

        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            metavar="OUTFILE",
            default="-",
            type=str,
            help='粤文 subtitle outfile path or "-" for stdout',
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def _main(cls, **kwargs: Unpack[CLIKwargs]):
        """Execute with provided keyword arguments.

        Arguments:
            **kwargs: keyword arguments
        """
        parser = kwargs.pop("_parser", cls.argparser())
        media_infile_path = kwargs.pop("media_infile")
        zhongwen_infile_path = kwargs.pop("zhongwen_infile")
        stream_index = kwargs.pop("stream_index")
        outfile_path = kwargs.pop("outfile")
        overwrite = kwargs.pop("overwrite")

        try:
            validated_zhongwen_path = val_input_path(zhongwen_infile_path)
            zhongwen = Series.load(validated_zhongwen_path)
            yuewen = AudioSeries.load_from_media(
                media_path=media_infile_path,
                subtitle_path=validated_zhongwen_path,
                stream_index=stream_index,
            )
            yuewen = get_yue_transcribed_vs_zho(
                yuewen=yuewen,
                zhongwen=zhongwen,
            )
        except (FileNotFoundError, NotAFileError, ScinoephileError) as exc:
            parser_error_from_exception(parser, exc)
        write_subtitle_series(parser, yuewen, outfile_path, overwrite)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "transcribe"


if __name__ == "__main__":
    YueTranscribeCli.main()
