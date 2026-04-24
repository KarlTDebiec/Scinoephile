#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for written Cantonese subtitle transcription."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from typing import Unpack

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common import CLIKwargs
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
    str_arg,
)
from scinoephile.common.exception import ArgumentConflictError, NotAFileError
from scinoephile.common.file import get_temp_file_path
from scinoephile.core.cli import ScinoephileCliBase, read_series, write_series
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.multilang.yue_zho.transcription import (
    DemucsMode,
    VADMode,
    get_yue_transcribed_vs_zho,
    get_yue_vs_zho_transcriber,
)
from scinoephile.multilang.yue_zho.transcription.deliniation import (
    YueZhoHansDeliniationPrompt,
    YueZhoHantDeliniationPrompt,
)
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YueZhoHansPunctuationPrompt,
    YueZhoHantPunctuationPrompt,
)

__all__ = ["YueTranscribeVsZhoCli"]


class YueTranscribeVsZhoCli(ScinoephileCliBase):
    """Transcribe subtitles from audio and revise using standard Chinese text."""

    localizations = {
        "zh-hans": {
            "command-line interface for written Cantonese subtitle transcription": (
                "书面粤语字幕转写命令行界面"
            ),
            "script for prompts and output conversion (default: simplified)": (
                "提示词和输出转换使用的字形（默认：简体）"
            ),
            "Demucs vocal-separation mode (default: off)": (
                "Demucs 人声分离模式（默认：off）"
            ),
            "Whisper voice activity detection mode (default: auto)": (
                "Whisper 语音活动检测模式（默认：auto）"
            ),
            'Standard Chinese subtitle infile or "-" for stdin': (
                '标准中文字幕输入文件，或使用 "-" 表示标准输入'
            ),
            "video or audio media input path used for transcription": (
                "用于转写的视频或音频输入路径"
            ),
            "Written Cantonese subtitle outfile path (default: stdout)": (
                "书面粤语字幕输出文件路径（默认：标准输出）"
            ),
        },
        "zh-hant": {
            "command-line interface for written Cantonese subtitle transcription": (
                "書面粵語字幕轉寫命令列介面"
            ),
            "script for prompts and output conversion (default: simplified)": (
                "提示詞與輸出轉換使用的字形（預設：簡體）"
            ),
            "Demucs vocal-separation mode (default: off)": (
                "Demucs 人聲分離模式（預設：off）"
            ),
            "Whisper voice activity detection mode (default: auto)": (
                "Whisper 語音活動偵測模式（預設：auto）"
            ),
            'Standard Chinese subtitle infile or "-" for stdin': (
                '標準中文字幕輸入檔，或使用 "-" 代表標準輸入'
            ),
            "video or audio media input path used for transcription": (
                "用於轉寫的視訊或音訊輸入路徑"
            ),
            "Written Cantonese subtitle outfile path (default: stdout)": (
                "書面粵語字幕輸出檔路徑（預設：標準輸出）"
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
            "--media-infile",
            required=True,
            type=str,
            help="video or audio media input path used for transcription",
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
            help='Standard Chinese subtitle infile or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--script",
            default="simplified",
            type=str_arg(options=("simplified", "traditional")),
            help="script for prompts and output conversion (default: simplified)",
        )
        arg_groups["operation arguments"].add_argument(
            "--demucs",
            default="off",
            type=str_arg(options=("on", "off")),
            help="Demucs vocal-separation mode (default: off)",
        )
        arg_groups["operation arguments"].add_argument(
            "--vad",
            default="auto",
            type=str_arg(options=("on", "off", "auto")),
            help="Whisper voice activity detection mode (default: auto)",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            default=None,
            type=output_file_arg(),
            help="Written Cantonese subtitle outfile path (default: stdout)",
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
    def _get_transcription_prompt_classes(
        cls, script: str
    ) -> tuple[type[YueZhoHansDeliniationPrompt], type[YueZhoHansPunctuationPrompt]]:
        """Get transcription prompt classes for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            deliniation and punctuation prompt classes
        """
        if script == "traditional":
            return YueZhoHantDeliniationPrompt, YueZhoHantPunctuationPrompt
        return YueZhoHansDeliniationPrompt, YueZhoHansPunctuationPrompt

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
        script = kwargs.pop("script")
        demucs_mode = DemucsMode(kwargs.pop("demucs"))
        vad_mode = VADMode(kwargs.pop("vad"))
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
        deliniation_prompt_cls, punctuation_prompt_cls = (
            cls._get_transcription_prompt_classes(script)
        )
        transcriber = get_yue_vs_zho_transcriber(
            demucs_mode=demucs_mode,
            vad_mode=vad_mode,
            deliniation_prompt_cls=deliniation_prompt_cls,
            punctuation_prompt_cls=punctuation_prompt_cls,
        )
        yuewen = get_yue_transcribed_vs_zho(
            yuewen=yuewen,
            zhongwen=zhongwen,
            transcriber=transcriber,
        )

        # Write outputs
        write_series(
            parser, yuewen, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    YueTranscribeVsZhoCli.main()
