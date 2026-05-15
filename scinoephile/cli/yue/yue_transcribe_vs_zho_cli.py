#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for written Cantonese subtitle transcription."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.cli.conversion import (
    CONVERSION_LOCALIZATIONS,
    add_opencc_convert_argument,
)
from scinoephile.cli.llms import LLM_LOCALIZATIONS, add_llm_provider_arguments
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
from scinoephile.core.cli import ScinoephileCliBase, read_series, write_series
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.lang.zho.script.conversion import OpenCCConfig
from scinoephile.llms.providers.registry import get_provider
from scinoephile.multilang.yue_zho.transcription import (
    DemucsMode,
    VADMode,
    get_yue_transcribed_vs_zho,
    get_yue_vs_zho_transcriber,
)
from scinoephile.multilang.yue_zho.transcription.deliniation import (
    YueVsZhoDeliniationPromptYueHans,
    YueVsZhoDeliniationPromptYueHant,
)
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YueVsZhoPunctuationPromptYueHans,
    YueVsZhoPunctuationPromptYueHant,
)

__all__ = ["YueTranscribeVsZhoCli"]

YUE_TRANSCRIBE_VS_ZHO_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audio stream index in media input (default: 0)": (
            "媒体输入中的音频流索引（默认：0）"
        ),
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
        'Standard Chinese subtitle infile or "-" for stdin': (
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
        "audio stream index in media input (default: 0)": (
            "媒體輸入中的音訊流索引（預設：0）"
        ),
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
        'Standard Chinese subtitle infile or "-" for stdin': (
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
        CONVERSION_LOCALIZATIONS,
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
            default=0,
            help="audio stream index in media input (default: 0)",
        )
        arg_groups["input arguments"].add_argument(
            "--zhongwen-infile",
            dest="zhongwen_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='Standard Chinese subtitle infile or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--demucs",
            default=DemucsMode.OFF,
            type=enum_arg(DemucsMode),
            help="Demucs vocal-separation mode (options: on, off; default: off)",
        )
        arg_groups["operation arguments"].add_argument(
            "--vad",
            default=VADMode.AUTO,
            type=enum_arg(VADMode),
            help=(
                "Whisper voice activity detection mode "
                "(options: on, off, auto; default: auto)"
            ),
        )
        add_opencc_convert_argument(
            arg_groups["operation arguments"], arg_groups["additional help"]
        )
        add_llm_provider_arguments(
            arg_groups["operation arguments"], arg_groups["additional help"]
        )
        arg_groups["operation arguments"].add_argument(
            "--script",
            default="simplified",
            type=str_arg(options=("simplified", "traditional")),
            help="script used for transcription prompts (default: simplified)",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            default=None,
            dest="outfile_path",
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
        return "transcribe-vs-zho"

    @classmethod
    def _get_transcription_prompt_classes(
        cls, script: str
    ) -> tuple[
        type[YueVsZhoDeliniationPromptYueHans], type[YueVsZhoPunctuationPromptYueHans]
    ]:
        """Get transcription prompt classes for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            deliniation and punctuation prompt classes
        """
        if script == "traditional":
            return YueVsZhoDeliniationPromptYueHant, YueVsZhoPunctuationPromptYueHant
        return YueVsZhoDeliniationPromptYueHans, YueVsZhoPunctuationPromptYueHans

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        media_infile_path: str,
        zhongwen_infile_path: Path | str,
        stream_index: int,
        script: str,
        convert: OpenCCConfig | None,
        llm_provider_name: str,
        llm_model_name: str | None,
        demucs: DemucsMode,
        vad: VADMode,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if media_infile_path == "-" and zhongwen_infile_path == "-":
            parser.error("--media-infile and --zhongwen-infile may not both be '-'")
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")

        # Read inputs
        if zhongwen_infile_path == "-":
            zhongwen = read_series(parser, "-", allow_stdin=True)
            try:
                with get_temp_file_path(suffix=".srt") as temp_zhongwen_path:
                    zhongwen.save(temp_zhongwen_path)
                    yuewen = AudioSeries.load_from_media(
                        media_path=media_infile_path,
                        subtitle_path=temp_zhongwen_path,
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
            zhongwen = read_series(parser, zhongwen_infile_path, allow_stdin=True)
            try:
                yuewen = AudioSeries.load_from_media(
                    media_path=media_infile_path,
                    subtitle_path=zhongwen_infile_path,
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
        deliniation_prompt_cls, punctuation_prompt_cls = (
            cls._get_transcription_prompt_classes(script)
        )
        provider = get_provider(llm_provider_name, model=llm_model_name)
        transcriber = get_yue_vs_zho_transcriber(
            demucs_mode=demucs,
            vad_mode=vad,
            provider=provider,
            convert=convert,
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
