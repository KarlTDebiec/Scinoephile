#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for written Cantonese subtitle transcription."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.cli.helpers.io import read_series, write_series
from scinoephile.cli.helpers.llms import (
    LLM_LOCALIZATIONS,
    LlmArguments,
    add_llm_provider_args,
    read_llm_additional_context,
)
from scinoephile.common.argument_parsing import (
    enum_arg,
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
    str_arg,
)
from scinoephile.common.exceptions import NotAFileError
from scinoephile.common.file import get_temp_file_path
from scinoephile.core import Language
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.llms.providers.registry import get_provider
from scinoephile.multilang.transcription.processor import (
    DemucsMode,
    VADMode,
)
from scinoephile.multilang.yue_zho.transcription import (
    DEFAULT_YUE_WHISPER_MODEL_NAME,
)
from scinoephile.workflows.transcription import transcribe_series_guided

__all__ = ["YueTranscribeVsZhoCli"]

YUE_TRANSCRIBE_VS_ZHO_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        (
            "media stream index of audio stream in media input "
            "(default: first audio stream)"
        ): ("媒体输入中的音频媒体流索引（默认：第一个音频流）"),
        (
            "command-line interface for written Cantonese subtitle transcription"
        ): "书面粤语字幕转写命令行界面",
        "script used for transcription prompts (default: simplified)": (
            "转写提示词使用的字形（默认：简体）"
        ),
        "Demucs vocal-separation mode (options: on, off; default: off)": (
            "Demucs 人声分离模式（选项：on、off；默认：off）"
        ),
        (
            "Whisper voice activity detection mode "
            "(options: on, off, auto; default: auto)"
        ): "Whisper 语音活动检测模式（选项：on、off、auto；默认：auto）",
        "Whisper model identifier used for transcription (default: %(default)s)": (
            "用于转写的 Whisper 模型标识符（默认：%(default)s）"
        ),
        'standard Chinese subtitle infile, or "-" for stdin': (
            '标准中文字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "video or audio media input path used for transcription": (
            "用于转写的视频或音频输入路径"
        ),
        "Written Cantonese subtitle outfile path (default: stdout)": (
            "书面粤语字幕输出文件路径（默认：标准输出）"
        ),
        (
            "Transcribe subtitles from audio and revise using standard Chinese text"
        ): "从音频转录字幕，并使用标准中文文本修订",
    },
    "zh-hant": {
        (
            "media stream index of audio stream in media input "
            "(default: first audio stream)"
        ): ("媒體輸入中的音訊媒體流索引（預設：第一個音訊流）"),
        (
            "command-line interface for written Cantonese subtitle transcription"
        ): "書面粵語字幕轉寫命令列介面",
        "script used for transcription prompts (default: simplified)": (
            "轉寫提示詞使用的字形（預設：簡體）"
        ),
        "Demucs vocal-separation mode (options: on, off; default: off)": (
            "Demucs 人聲分離模式（選項：on、off；預設：off）"
        ),
        (
            "Whisper voice activity detection mode "
            "(options: on, off, auto; default: auto)"
        ): "Whisper 語音活動偵測模式（選項：on、off、auto；預設：auto）",
        "Whisper model identifier used for transcription (default: %(default)s)": (
            "用於轉寫的 Whisper 模型識別碼（預設：%(default)s）"
        ),
        'standard Chinese subtitle infile, or "-" for stdin': (
            '標準中文字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "video or audio media input path used for transcription": (
            "用於轉寫的視訊或音訊輸入路徑"
        ),
        "Written Cantonese subtitle outfile path (default: stdout)": (
            "書面粵語字幕輸出檔路徑（預設：標準輸出）"
        ),
        (
            "Transcribe subtitles from audio and revise using standard Chinese text"
        ): "從音訊轉錄字幕，並使用標準中文文字修訂",
    },
}
"""Localized help text keyed by locale and English source text."""


class YueTranscribeVsZhoCli(ScinoephileCliBase):
    """Transcribe subtitles from audio and revise using standard Chinese text."""

    localizations = merge_localizations(
        LLM_LOCALIZATIONS,
        YUE_TRANSCRIBE_VS_ZHO_LOCALIZATIONS,
    )
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
            "llm arguments",
            "output arguments",
            "additional help",
            optional_arguments_name="additional arguments",
        )

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--media-infile",
            dest="media_infile_path",
            required=True,
            type=str,
            help="video or audio media input path used for transcription",
        )
        arg_groups["input arguments"].add_argument(
            "--stream-index",
            type=int_arg(min_value=0),
            help=(
                "media stream index of audio stream in media input "
                "(default: first audio stream)"
            ),
        )
        arg_groups["input arguments"].add_argument(
            "--zho-infile",
            dest="zho_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='standard Chinese subtitle infile, or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--demucs",
            default=DemucsMode.OFF,
            metavar="{on,off}",
            type=enum_arg(DemucsMode),
            help="Demucs vocal-separation mode (options: on, off; default: off)",
        )
        arg_groups["operation arguments"].add_argument(
            "--vad",
            default=VADMode.AUTO,
            metavar="{auto,on,off}",
            type=enum_arg(VADMode),
            help=(
                "Whisper voice activity detection mode "
                "(options: on, off, auto; default: auto)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--whisper-model",
            default=DEFAULT_YUE_WHISPER_MODEL_NAME,
            dest="whisper_model_name",
            help=(
                "Whisper model identifier used for transcription (default: %(default)s)"
            ),
        )
        add_llm_provider_args(
            arg_groups["llm arguments"], arg_groups["additional help"]
        )
        arg_groups["operation arguments"].add_argument(
            "--script",
            default="simplified",
            metavar="{simplified,traditional}",
            type=str_arg(options=("simplified", "traditional")),
            help="script used for transcription prompts (default: simplified)",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            type=output_file_arg(exist_ok=True),
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
        return "transcribe-vs-zho"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        media_infile_path: str,
        zho_infile_path: Path | str,
        stream_index: int | None,
        script: str,
        llm_args: LlmArguments,
        demucs: DemucsMode,
        vad: VADMode,
        whisper_model_name: str,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if media_infile_path == "-" and zho_infile_path == "-":
            parser.error("--media-infile and --zho-infile may not both be '-'")
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")

        # Read inputs
        if zho_infile_path == "-":
            zhongwen = read_series(parser, "-", allow_stdin=True)
            try:
                with get_temp_file_path(suffix=".srt") as temp_zho_path:
                    zhongwen.save(temp_zho_path)
                    yuewen = AudioSeries.load_from_media(
                        media_path=media_infile_path,
                        subtitle_path=temp_zho_path,
                        stream_index=stream_index,
                    )
            except (
                FileNotFoundError,
                NotADirectoryError,
                NotAFileError,
                ScinoephileError,
                ValueError,
            ) as exc:
                parser.error(str(exc))
        else:
            zhongwen = read_series(parser, zho_infile_path, allow_stdin=True)
            try:
                yuewen = AudioSeries.load_from_media(
                    media_path=media_infile_path,
                    subtitle_path=zho_infile_path,
                    stream_index=stream_index,
                )
            except (
                FileNotFoundError,
                NotADirectoryError,
                NotAFileError,
                ScinoephileError,
                ValueError,
            ) as exc:
                parser.error(str(exc))

        # Perform operations
        additional_context = read_llm_additional_context(
            parser, llm_args.additional_context_file_path
        )
        provider = get_provider(llm_args.provider_name, model=llm_args.model_name)
        language = Language.yue_hans
        if script == "traditional":
            language = Language.yue_hant
        yuewen = transcribe_series_guided(
            yuewen,
            zhongwen,
            language=language,
            model_name=whisper_model_name,
            demucs_mode=demucs,
            vad_mode=vad,
            provider=provider,
            additional_context=additional_context,
        )

        # Write outputs
        write_series(
            parser, yuewen, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    YueTranscribeVsZhoCli.main()
