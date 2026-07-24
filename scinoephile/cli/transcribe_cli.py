#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for reference-guided subtitle transcription.

Transcribe audio using reference subtitles.
"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common.argument_parsing import (
    enum_arg,
    enum_metavar,
    enum_options_list_str,
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from scinoephile.common.exceptions import NotAFileError
from scinoephile.common.file import get_temp_file_path
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.lang.transcription.transcriber import (
    DemucsMode,
    TranscriptionBackend,
    VADMode,
)
from scinoephile.llms.providers.registry import get_provider
from scinoephile.workflows.transcription import transcribe_series_guided

from .helpers.blocks import (
    BLOCK_LOCALIZATIONS,
    add_block_range_args,
    get_block_range_indexes,
)
from .helpers.io import read_series, write_series
from .helpers.llms import (
    LLM_LOCALIZATIONS,
    LlmArguments,
    add_llm_provider_args,
    add_llm_test_case_json_arg,
    read_llm_additional_context,
)

__all__ = ["TranscribeCli"]

TRANSCRIBE_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "command-line interface for reference-guided subtitle transcription": (
            "参考字幕引导的字幕转写命令行界面"
        ),
        "Transcribe audio using reference subtitles.": "使用参考字幕转写音频。",
        "media infile used for transcription": "用于转写的媒体输入文件",
        (
            "media stream index of audio stream in media input "
            "(default: first audio stream)"
        ): "媒体输入中的音频媒体流索引（默认：第一个音频流）",
        'guide subtitle infile, or "-" for stdin': (
            '引导字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "transcription language": "转写语言",
        "guide language (detected from infile if omitted)": (
            "引导字幕语言（省略时从输入文件检测）"
        ),
        (
            f"transcription backend (options: "
            f"{enum_options_list_str(TranscriptionBackend)}; "
            "default: %(default)s)"
        ): "转写后端（选项：whisper 或 mlx-audio；默认：%(default)s）",
        (
            f"Demucs vocal-separation mode (options: "
            f"{enum_options_list_str(DemucsMode)}; default: %(default)s)"
        ): "Demucs 人声分离模式（选项：auto、on 或 off；默认：%(default)s）",
        (
            f"voice activity detection mode (options: "
            f"{enum_options_list_str(VADMode)}; default: %(default)s)"
        ): "语音活动检测模式（选项：auto、on 或 off；默认：%(default)s）",
        "transcription model identifier override (uses backend default if omitted)": (
            "转写模型标识符覆盖值（省略时使用后端默认值）"
        ),
        "delineation test-case JSON file to load and update": (
            "要加载和更新的断句测试用例 JSON 文件"
        ),
        "punctuation test-case JSON file to load and update": (
            "要加载和更新的标点测试用例 JSON 文件"
        ),
        "subtitle outfile path (default: stdout)": (
            "字幕输出文件路径（默认：标准输出）"
        ),
        "transcribe audio using reference subtitles": "使用参考字幕转写音频",
    },
    "zh-hant": {
        "command-line interface for reference-guided subtitle transcription": (
            "參考字幕引導的字幕轉寫命令列介面"
        ),
        "Transcribe audio using reference subtitles.": "使用參考字幕轉寫音訊。",
        "media infile used for transcription": "用於轉寫的媒體輸入檔",
        (
            "media stream index of audio stream in media input "
            "(default: first audio stream)"
        ): "媒體輸入中的音訊媒體流索引（預設：第一個音訊流）",
        'guide subtitle infile, or "-" for stdin': (
            '引導字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "transcription language": "轉寫語言",
        "guide language (detected from infile if omitted)": (
            "引導字幕語言（省略時從輸入檔偵測）"
        ),
        (
            f"transcription backend (options: "
            f"{enum_options_list_str(TranscriptionBackend)}; "
            "default: %(default)s)"
        ): "轉寫後端（選項：whisper 或 mlx-audio；預設：%(default)s）",
        (
            f"Demucs vocal-separation mode (options: "
            f"{enum_options_list_str(DemucsMode)}; default: %(default)s)"
        ): "Demucs 人聲分離模式（選項：auto、on 或 off；預設：%(default)s）",
        (
            f"voice activity detection mode (options: "
            f"{enum_options_list_str(VADMode)}; default: %(default)s)"
        ): "語音活動偵測模式（選項：auto、on 或 off；預設：%(default)s）",
        "transcription model identifier override (uses backend default if omitted)": (
            "轉寫模型識別碼覆寫值（省略時使用後端預設值）"
        ),
        "delineation test-case JSON file to load and update": (
            "要載入和更新的斷句測試案例 JSON 檔案"
        ),
        "punctuation test-case JSON file to load and update": (
            "要載入和更新的標點測試案例 JSON 檔案"
        ),
        "subtitle outfile path (default: stdout)": ("字幕輸出檔路徑（預設：標準輸出）"),
        "transcribe audio using reference subtitles": "使用參考字幕轉寫音訊",
    },
}
"""Localized help text keyed by locale and English source text."""


class TranscribeCli(ScinoephileCliBase):
    """Transcribe audio using reference subtitles."""

    localizations = merge_localizations(
        BLOCK_LOCALIZATIONS,
        LLM_LOCALIZATIONS,
        TRANSCRIBE_LOCALIZATIONS,
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
            "media_infile_path",
            metavar="MEDIA_INFILE",
            help="media infile used for transcription",
        )
        arg_groups["input arguments"].add_argument(
            "--guide-infile",
            dest="guide_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='guide subtitle infile, or "-" for stdin',
        )
        arg_groups["input arguments"].add_argument(
            "--stream-index",
            type=int_arg(min_value=0),
            help=(
                "media stream index of audio stream in media input "
                "(default: first audio stream)"
            ),
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--language",
            required=True,
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help="transcription language",
        )
        arg_groups["operation arguments"].add_argument(
            "--guide-language",
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help="guide language (detected from infile if omitted)",
        )
        add_block_range_args(arg_groups["operation arguments"])
        arg_groups["operation arguments"].add_argument(
            "--backend",
            default=TranscriptionBackend.WHISPER,
            metavar=enum_metavar(TranscriptionBackend),
            type=enum_arg(TranscriptionBackend),
            help=(
                f"transcription backend (options: "
                f"{enum_options_list_str(TranscriptionBackend)}; "
                "default: %(default)s)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--demucs",
            default=DemucsMode.AUTO,
            dest="demucs_mode",
            metavar=enum_metavar(DemucsMode),
            type=enum_arg(DemucsMode),
            help=(
                f"Demucs vocal-separation mode (options: "
                f"{enum_options_list_str(DemucsMode)}; default: %(default)s)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--vad",
            default=VADMode.AUTO,
            dest="vad_mode",
            metavar=enum_metavar(VADMode),
            type=enum_arg(VADMode),
            help=(
                f"voice activity detection mode (options: "
                f"{enum_options_list_str(VADMode)}; default: %(default)s)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--model",
            dest="model_name",
            help=(
                "transcription model identifier override "
                "(uses backend default if omitted)"
            ),
        )
        add_llm_provider_args(
            arg_groups["llm arguments"], arg_groups["additional help"]
        )
        add_llm_test_case_json_arg(
            arg_groups["llm arguments"],
            "--delineation-json",
            dest="delineation_json_path",
            help_text="delineation test-case JSON file to load and update",
        )
        add_llm_test_case_json_arg(
            arg_groups["llm arguments"],
            "--punctuation-json",
            dest="punctuation_json_path",
            help_text="punctuation test-case JSON file to load and update",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            type=output_file_arg(exist_ok=True),
            help="subtitle outfile path (default: stdout)",
        )
        arg_groups["output arguments"].add_argument(
            "--overwrite",
            action="store_true",
            help="overwrite outfile if it exists",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        media_infile_path: str,
        guide_infile_path: Path | str,
        stream_index: int | None,
        language: Language,
        guide_language: Language | None,
        first_block: int | None,
        last_block: int | None,
        backend: TranscriptionBackend,
        demucs_mode: DemucsMode,
        vad_mode: VADMode,
        model_name: str | None,
        llm_args: LlmArguments,
        delineation_json_path: Path | None,
        punctuation_json_path: Path | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if media_infile_path == "-" and guide_infile_path == "-":
            parser.error("MEDIA_INFILE and --guide-infile may not both be '-'")
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")

        # Read inputs
        guide = read_series(parser, guide_infile_path, allow_stdin=True)
        start_at_idx, stop_at_idx = get_block_range_indexes(
            parser,
            first_block,
            last_block,
            len(guide.blocks),
        )
        try:
            if guide_infile_path == "-":
                with get_temp_file_path(suffix=".srt") as temp_guide_path:
                    guide.save(temp_guide_path)
                    audio = AudioSeries.load_from_media(
                        media_path=media_infile_path,
                        subtitle_path=temp_guide_path,
                        stream_index=stream_index,
                    )
            else:
                audio = AudioSeries.load_from_media(
                    media_path=media_infile_path,
                    subtitle_path=guide_infile_path,
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

        # Perform operation
        try:
            output = transcribe_series_guided(
                audio,
                guide,
                language=language,
                reference_language=guide_language,
                model_name=model_name,
                backend=backend,
                demucs_mode=demucs_mode,
                vad_mode=vad_mode,
                provider=get_provider(
                    llm_args.provider_name,
                    model=llm_args.model_name,
                ),
                additional_context=read_llm_additional_context(
                    parser,
                    llm_args.additional_context_file_path,
                ),
                delineation_json_path=delineation_json_path,
                punctuation_json_path=punctuation_json_path,
                start_at_idx=start_at_idx,
                stop_at_idx=stop_at_idx,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        # Write output
        write_series(
            parser, output, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    TranscribeCli.main()
