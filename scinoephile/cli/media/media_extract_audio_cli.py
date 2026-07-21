#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for extracting an audio stream from media."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.media.audio import extract_audio

__all__ = ["MediaExtractAudioCli"]

MEDIA_EXTRACT_AUDIO_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audio outfile path in WAV format": "WAV 格式的音频输出文件路径",
        "extract an audio stream from a media file": "从媒体文件提取音频流",
        "media infile containing audio streams": "包含音频流的媒体输入文件",
        "media stream index of audio stream (default: first audio stream)": (
            "音频媒体流的媒体流索引（默认：第一个音频流）"
        ),
        "overwrite audio outfile if it exists": "若音频输出文件已存在则覆盖",
    },
    "zh-hant": {
        "audio outfile path in WAV format": "WAV 格式的音訊輸出檔路徑",
        "extract an audio stream from a media file": "從媒體檔提取音訊流",
        "media infile containing audio streams": "包含音訊流的媒體輸入檔",
        "media stream index of audio stream (default: first audio stream)": (
            "音訊媒體流的媒體流索引（預設：第一個音訊流）"
        ),
        "overwrite audio outfile if it exists": "若音訊輸出檔已存在則覆寫",
    },
}
"""Localized help text keyed by locale and English source text."""


class MediaExtractAudioCli(ScinoephileCliBase):
    """Extract an audio stream from a media file."""

    localizations = MEDIA_EXTRACT_AUDIO_LOCALIZATIONS
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
        arg_groups["input arguments"].add_argument(
            "--infile",
            dest="infile_path",
            required=True,
            type=input_file_arg(),
            help="media infile containing audio streams",
        )
        arg_groups["operation arguments"].add_argument(
            "--stream-index",
            type=int_arg(min_value=0),
            help=("media stream index of audio stream (default: first audio stream)"),
        )
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            required=True,
            type=output_file_arg(exist_ok=True),
            help="audio outfile path in WAV format",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite audio outfile if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "extract-audio"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        infile_path: Path,
        stream_index: int | None,
        outfile_path: Path,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        try:
            stream = extract_audio(
                infile_path,
                outfile_path,
                stream_index=stream_index,
                overwrite=overwrite,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))
        print(f"Extracted audio: {stream.description} -> {outfile_path}")


if __name__ == "__main__":
    MediaExtractAudioCli.main()
