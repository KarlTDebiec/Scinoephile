#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for aligned multi-source audio transcription."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.analysis.transcription_alignment import SubtitleTimingSettings
from scinoephile.audio.diarization import DiarizationMode
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import DemucsMode, VADImplementation
from scinoephile.common.argument_parsing import (
    enum_arg,
    enum_metavar,
    enum_options_list_str,
    float_arg,
    get_arg_groups_by_name,
    int_arg,
    output_file_arg,
)
from scinoephile.common.exceptions import NotAFileError
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.llms.providers.registry import get_provider
from scinoephile.workflows.transcription import transcribe_series

from .helpers.blocks import (
    BLOCK_LOCALIZATIONS,
    add_block_range_args,
    get_block_range_indexes,
)
from .helpers.cache import CACHE_LOCALIZATIONS, CacheArguments, add_cache_args
from .helpers.io import write_series
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
        "command-line interface for aligned multi-source audio transcription": (
            "多来源对齐音频转写命令行界面"
        ),
        "Transcribe audio by aligning and merging equal-status ASR sources.": (
            "通过对齐并合并同等地位的语音识别来源来转写音频。"
        ),
        "media infile used for transcription": "用于转写的媒体输入文件",
        "media stream index (default: first audio stream)": (
            "媒体流索引（默认：第一个音频流）"
        ),
        "transcription language": "转写语言",
        (
            f"Demucs vocal-separation mode (options: "
            f"{enum_options_list_str(DemucsMode)}; default: %(default)s)"
        ): "Demucs 人声分离模式（默认：%(default)s）",
        (
            f"speaker diarization mode (options: "
            f"{enum_options_list_str(DiarizationMode)}; default: %(default)s)"
        ): "说话人分离模式（默认：%(default)s）",
        (
            f"ASR backend VAD implementation (options: "
            f"{enum_options_list_str(VADImplementation)}; default: %(default)s)"
        ): "语音识别后端 VAD 实现（默认：%(default)s）",
        (
            f"block-planning VAD implementation (options: "
            f"{enum_options_list_str(VADImplementation)}; default: %(default)s)"
        ): "区块规划 VAD 实现（默认：%(default)s）",
        "disable MiMo generation-token omission guard": ("停用 MiMo 生成词元遗漏保护"),
        "display lead-in seconds (default: %(default)s)": (
            "字幕提前显示秒数（默认：%(default)s）"
        ),
        "display lead-out seconds (default: %(default)s)": (
            "字幕延后隐藏秒数（默认：%(default)s）"
        ),
        "minimum subtitle display duration in seconds (default: %(default)s)": (
            "字幕最短显示秒数（默认：%(default)s）"
        ),
        "JSON file containing aligned merge test cases": (
            "包含对齐合并测试用例的 JSON 文件"
        ),
        "alignment artifact JSON outfile (default: derived from subtitle outfile)": (
            "对齐成品 JSON 输出文件（默认：从字幕输出文件推导）"
        ),
        "subtitle outfile path (default: stdout)": (
            "字幕输出文件路径（默认：标准输出）"
        ),
        "overwrite output files if they exist": "覆盖已存在的输出文件",
    },
    "zh-hant": {
        "command-line interface for aligned multi-source audio transcription": (
            "多來源對齊音訊轉寫命令列介面"
        ),
        "Transcribe audio by aligning and merging equal-status ASR sources.": (
            "透過對齊並合併同等地位的語音辨識來源來轉寫音訊。"
        ),
        "media infile used for transcription": "用於轉寫的媒體輸入檔",
        "media stream index (default: first audio stream)": (
            "媒體流索引（預設：第一個音訊流）"
        ),
        "transcription language": "轉寫語言",
        (
            f"Demucs vocal-separation mode (options: "
            f"{enum_options_list_str(DemucsMode)}; default: %(default)s)"
        ): "Demucs 人聲分離模式（預設：%(default)s）",
        (
            f"speaker diarization mode (options: "
            f"{enum_options_list_str(DiarizationMode)}; default: %(default)s)"
        ): "說話者分離模式（預設：%(default)s）",
        (
            f"ASR backend VAD implementation (options: "
            f"{enum_options_list_str(VADImplementation)}; default: %(default)s)"
        ): "語音辨識後端 VAD 實作（預設：%(default)s）",
        (
            f"block-planning VAD implementation (options: "
            f"{enum_options_list_str(VADImplementation)}; default: %(default)s)"
        ): "區塊規劃 VAD 實作（預設：%(default)s）",
        "disable MiMo generation-token omission guard": ("停用 MiMo 生成詞元遺漏保護"),
        "display lead-in seconds (default: %(default)s)": (
            "字幕提前顯示秒數（預設：%(default)s）"
        ),
        "display lead-out seconds (default: %(default)s)": (
            "字幕延後隱藏秒數（預設：%(default)s）"
        ),
        "minimum subtitle display duration in seconds (default: %(default)s)": (
            "字幕最短顯示秒數（預設：%(default)s）"
        ),
        "JSON file containing aligned merge test cases": (
            "包含對齊合併測試案例的 JSON 檔"
        ),
        "alignment artifact JSON outfile (default: derived from subtitle outfile)": (
            "對齊成品 JSON 輸出檔（預設：從字幕輸出檔推導）"
        ),
        "subtitle outfile path (default: stdout)": ("字幕輸出檔路徑（預設：標準輸出）"),
        "overwrite output files if they exist": "覆寫已存在的輸出檔",
    },
}
"""Localized help text keyed by locale and English source text."""


class TranscribeCli(ScinoephileCliBase):
    """Transcribe audio by aligning and merging equal-status ASR sources."""

    localizations = merge_localizations(
        BLOCK_LOCALIZATIONS,
        CACHE_LOCALIZATIONS,
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
            "cache arguments",
            "output arguments",
            "additional help",
            optional_arguments_name="additional arguments",
        )
        arg_groups["input arguments"].add_argument(
            "--media-infile",
            dest="media_infile_path",
            required=True,
            help="media infile used for transcription",
        )
        arg_groups["input arguments"].add_argument(
            "--stream-index",
            type=int_arg(min_value=0),
            help="media stream index (default: first audio stream)",
        )

        operation_group = arg_groups["operation arguments"]
        operation_group.add_argument(
            "--language",
            required=True,
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help="transcription language",
        )
        add_block_range_args(operation_group)
        operation_group.add_argument(
            "--demucs",
            default=DemucsMode.OFF,
            dest="demucs_mode",
            metavar=enum_metavar(DemucsMode),
            type=enum_arg(DemucsMode),
            help=(
                f"Demucs vocal-separation mode (options: "
                f"{enum_options_list_str(DemucsMode)}; default: %(default)s)"
            ),
        )
        operation_group.add_argument(
            "--diarization",
            default=DiarizationMode.AUTO,
            dest="diarization_mode",
            metavar=enum_metavar(DiarizationMode),
            type=enum_arg(DiarizationMode),
            help=(
                f"speaker diarization mode (options: "
                f"{enum_options_list_str(DiarizationMode)}; default: %(default)s)"
            ),
        )
        operation_group.add_argument(
            "--vad-implementation",
            default=VADImplementation.SILERO,
            metavar=enum_metavar(VADImplementation),
            type=enum_arg(VADImplementation),
            help=(
                f"ASR backend VAD implementation (options: "
                f"{enum_options_list_str(VADImplementation)}; default: %(default)s)"
            ),
        )
        operation_group.add_argument(
            "--block-vad-implementation",
            default=VADImplementation.PYANNOTE,
            metavar=enum_metavar(VADImplementation),
            type=enum_arg(VADImplementation),
            help=(
                f"block-planning VAD implementation (options: "
                f"{enum_options_list_str(VADImplementation)}; default: %(default)s)"
            ),
        )
        operation_group.add_argument(
            "--no-mlx-audio-token-limit-guard",
            action="store_false",
            dest="mlx_audio_token_limit_guard",
            help="disable MiMo generation-token omission guard",
        )
        operation_group.add_argument(
            "--lead-in",
            default=0.0,
            dest="lead_in_seconds",
            type=float_arg(min_value=0.0),
            help="display lead-in seconds (default: %(default)s)",
        )
        operation_group.add_argument(
            "--lead-out",
            default=0.0,
            dest="lead_out_seconds",
            type=float_arg(min_value=0.0),
            help="display lead-out seconds (default: %(default)s)",
        )
        operation_group.add_argument(
            "--minimum-duration",
            default=0.75,
            dest="minimum_duration_seconds",
            type=float_arg(min_value=0.001),
            help="minimum subtitle display duration in seconds (default: %(default)s)",
        )

        add_llm_provider_args(
            arg_groups["llm arguments"], arg_groups["additional help"]
        )
        add_llm_test_case_json_arg(
            arg_groups["llm arguments"],
            "--aligned-merge-json",
            dest="aligned_merge_json_path",
            help_text="JSON file containing aligned merge test cases",
        )
        add_cache_args(arg_groups["cache arguments"])

        arg_groups["output arguments"].add_argument(
            "--alignment-outfile",
            dest="alignment_outfile_path",
            type=output_file_arg(exist_ok=True),
            help=(
                "alignment artifact JSON outfile "
                "(default: derived from subtitle outfile)"
            ),
        )
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
            help="overwrite output files if they exist",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        media_infile_path: str,
        stream_index: int | None,
        language: Language,
        first_block: int | None,
        last_block: int | None,
        demucs_mode: DemucsMode,
        diarization_mode: DiarizationMode,
        vad_implementation: VADImplementation,
        block_vad_implementation: VADImplementation,
        mlx_audio_token_limit_guard: bool,
        lead_in_seconds: float,
        lead_out_seconds: float,
        minimum_duration_seconds: float,
        llm_args: LlmArguments,
        cache_args: CacheArguments,
        aligned_merge_json_path: Path | None,
        alignment_outfile_path: Path | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        if overwrite and outfile_path is None and alignment_outfile_path is None:
            parser.error("--overwrite requires an output file")
        if alignment_outfile_path is None and outfile_path is not None:
            alignment_outfile_path = outfile_path.with_suffix(".alignment.json")
        for output_path in (outfile_path, alignment_outfile_path):
            if output_path is not None and output_path.exists() and not overwrite:
                parser.error(f"{output_path} already exists")

        start_at_idx, stop_at_idx = get_block_range_indexes(
            parser, first_block, last_block
        )
        try:
            audio = AudioSeries.load_audio_from_media(
                media_path=media_infile_path, stream_index=stream_index
            )
        except (
            FileNotFoundError,
            NotADirectoryError,
            NotAFileError,
            ScinoephileError,
            ValueError,
        ) as exc:
            parser.error(str(exc))

        try:
            output = transcribe_series(
                audio,
                language=language,
                demucs_mode=demucs_mode,
                diarization_mode=diarization_mode,
                vad_implementation=vad_implementation,
                block_vad_implementation=block_vad_implementation,
                mlx_audio_token_limit_guard=mlx_audio_token_limit_guard,
                cache_root_path=cache_args.root_path,
                overwrite_cache=cache_args.overwrite,
                provider=get_provider(
                    llm_args.provider_name, model=llm_args.model_name
                ),
                additional_context=read_llm_additional_context(
                    parser, llm_args.additional_context_file_path
                ),
                no_op=llm_args.no_op,
                aligned_merge_json_path=aligned_merge_json_path,
                alignment_json_path=alignment_outfile_path,
                timing_settings=SubtitleTimingSettings(
                    lead_in_seconds=lead_in_seconds,
                    lead_out_seconds=lead_out_seconds,
                    minimum_duration_seconds=minimum_duration_seconds,
                ),
                start_at_idx=start_at_idx,
                stop_at_idx=stop_at_idx,
            )
        except ScinoephileError as exc:
            parser.error(str(exc))
        write_series(
            parser, output, outfile_path if outfile_path is not None else "-", overwrite
        )


if __name__ == "__main__":
    TranscribeCli.main()
