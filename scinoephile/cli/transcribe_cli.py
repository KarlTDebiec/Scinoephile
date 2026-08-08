#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for aligned multi-source audio transcription."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.analysis.transcription import TimingSettings
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import DemucsMode
from scinoephile.audio.vad import VadImplementation
from scinoephile.common.argument_parsing import (
    enum_arg,
    enum_metavar,
    enum_options_list_str,
    float_arg,
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
)
from scinoephile.core import Language, ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.llms.providers.registry import get_provider
from scinoephile.workflows.transcription import transcribe_series
from scinoephile.workflows.transcription_pipeline import AudioAnalysisMode

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
        "transcribe audio by aligning and merging ASR sources": (
            "通过对齐并合并语音识别来源来转写音频"
        ),
        "media infile used for transcription": "用于转写的媒体输入文件",
        "media stream index (default: first audio stream)": (
            "媒体流索引（默认：第一个音频流）"
        ),
        "transcription language": "转写语言",
        "first 1-indexed block to process, inclusive": (
            "要处理的第一个区块（从 1 开始，包含该区块）"
        ),
        "last 1-indexed block to process, inclusive": (
            "要处理的最后一个区块（从 1 开始，包含该区块）"
        ),
        (
            f"Demucs vocal-separation mode (options: "
            f"{enum_options_list_str(DemucsMode)}; default: %(default)s)"
        ): "Demucs 人声分离模式（默认：%(default)s）",
        (
            f"speaker diarization mode (options: "
            f"{enum_options_list_str(AudioAnalysisMode)}; default: %(default)s)"
        ): "说话人分离模式（默认：%(default)s）",
        (
            f"spoken-language identification mode (options: "
            f"{enum_options_list_str(AudioAnalysisMode)}; default: %(default)s)"
        ): "口语语言识别模式（默认：%(default)s）",
        (
            f"speech, singing, and music detection mode (options: "
            f"{enum_options_list_str(AudioAnalysisMode)}; default: %(default)s)"
        ): "语音、歌唱和音乐检测模式（默认：%(default)s）",
        (
            f"block-planning VAD implementation (options: "
            f"{enum_options_list_str(VadImplementation)}; default: %(default)s)"
        ): "区块规划 VAD 实现（默认：%(default)s）",
        "display lead-in seconds (default: %(default)s)": (
            "字幕提前显示秒数（默认：%(default)s）"
        ),
        "display lead-out seconds (default: %(default)s)": (
            "字幕延后隐藏秒数（默认：%(default)s）"
        ),
        "minimum subtitle display duration in seconds (default: %(default)s)": (
            "字幕最短显示秒数（默认：%(default)s）"
        ),
        "JSON file containing transcription test cases": (
            "包含转写测试用例的 JSON 文件"
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
        "transcribe audio by aligning and merging ASR sources": (
            "透過對齊並合併語音辨識來源來轉寫音訊"
        ),
        "media infile used for transcription": "用於轉寫的媒體輸入檔",
        "media stream index (default: first audio stream)": (
            "媒體流索引（預設：第一個音訊流）"
        ),
        "transcription language": "轉寫語言",
        "first 1-indexed block to process, inclusive": (
            "要處理的第一個區塊（從 1 開始，包含該區塊）"
        ),
        "last 1-indexed block to process, inclusive": (
            "要處理的最後一個區塊（從 1 開始，包含該區塊）"
        ),
        (
            f"Demucs vocal-separation mode (options: "
            f"{enum_options_list_str(DemucsMode)}; default: %(default)s)"
        ): "Demucs 人聲分離模式（預設：%(default)s）",
        (
            f"speaker diarization mode (options: "
            f"{enum_options_list_str(AudioAnalysisMode)}; default: %(default)s)"
        ): "說話者分離模式（預設：%(default)s）",
        (
            f"spoken-language identification mode (options: "
            f"{enum_options_list_str(AudioAnalysisMode)}; default: %(default)s)"
        ): "口語語言識別模式（預設：%(default)s）",
        (
            f"speech, singing, and music detection mode (options: "
            f"{enum_options_list_str(AudioAnalysisMode)}; default: %(default)s)"
        ): "語音、歌唱和音樂偵測模式（預設：%(default)s）",
        (
            f"block-planning VAD implementation (options: "
            f"{enum_options_list_str(VadImplementation)}; default: %(default)s)"
        ): "區塊規劃 VAD 實作（預設：%(default)s）",
        "display lead-in seconds (default: %(default)s)": (
            "字幕提前顯示秒數（預設：%(default)s）"
        ),
        "display lead-out seconds (default: %(default)s)": (
            "字幕延後隱藏秒數（預設：%(default)s）"
        ),
        "minimum subtitle display duration in seconds (default: %(default)s)": (
            "字幕最短顯示秒數（預設：%(default)s）"
        ),
        "JSON file containing transcription test cases": ("包含轉寫測試案例的 JSON 檔"),
        "subtitle outfile path (default: stdout)": ("字幕輸出檔路徑（預設：標準輸出）"),
        "overwrite output files if they exist": "覆寫已存在的輸出檔",
    },
}
"""Localized help text keyed by locale and English source text."""


class TranscribeCli(ScinoephileCliBase):
    """Transcribe audio by aligning and merging ASR sources."""

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

        # Input arguments
        arg_groups["input arguments"].add_argument(
            "--media-infile",
            dest="media_infile_path",
            required=True,
            type=input_file_arg(),
            help="media infile used for transcription",
        )
        arg_groups["input arguments"].add_argument(
            "--stream-index",
            type=int_arg(min_value=0),
            help="media stream index (default: first audio stream)",
        )

        # Operation arguments
        operation_group = arg_groups["operation arguments"]
        operation_group.add_argument(
            "--language",
            required=True,
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help="transcription language",
        )
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
            default=AudioAnalysisMode.AUTO,
            dest="diarization_mode",
            metavar=enum_metavar(AudioAnalysisMode),
            type=enum_arg(AudioAnalysisMode),
            help=(
                f"speaker diarization mode (options: "
                f"{enum_options_list_str(AudioAnalysisMode)}; "
                "default: %(default)s)"
            ),
        )
        operation_group.add_argument(
            "--language-identification",
            default=AudioAnalysisMode.AUTO,
            dest="language_identification_mode",
            metavar=enum_metavar(AudioAnalysisMode),
            type=enum_arg(AudioAnalysisMode),
            help=(
                f"spoken-language identification mode (options: "
                f"{enum_options_list_str(AudioAnalysisMode)}; "
                "default: %(default)s)"
            ),
        )
        operation_group.add_argument(
            "--audio-events",
            default=AudioAnalysisMode.AUTO,
            dest="audio_event_mode",
            metavar=enum_metavar(AudioAnalysisMode),
            type=enum_arg(AudioAnalysisMode),
            help=(
                f"speech, singing, and music detection mode (options: "
                f"{enum_options_list_str(AudioAnalysisMode)}; "
                "default: %(default)s)"
            ),
        )
        operation_group.add_argument(
            "--block-vad-implementation",
            default=VadImplementation.PYANNOTE,
            metavar=enum_metavar(VadImplementation),
            type=enum_arg(VadImplementation),
            help=(
                f"block-planning VAD implementation (options: "
                f"{enum_options_list_str(VadImplementation)}; default: %(default)s)"
            ),
        )
        timing_defaults = TimingSettings()
        operation_group.add_argument(
            "--lead-in",
            default=timing_defaults.lead_in_seconds,
            dest="lead_in_seconds",
            type=float_arg(min_value=0.0),
            help="display lead-in seconds (default: %(default)s)",
        )
        operation_group.add_argument(
            "--lead-out",
            default=timing_defaults.lead_out_seconds,
            dest="lead_out_seconds",
            type=float_arg(min_value=0.0),
            help="display lead-out seconds (default: %(default)s)",
        )
        operation_group.add_argument(
            "--minimum-duration",
            default=timing_defaults.minimum_duration_seconds,
            dest="minimum_duration_seconds",
            type=float_arg(min_value=0.001),
            help="minimum subtitle display duration in seconds (default: %(default)s)",
        )
        add_block_range_args(
            operation_group,
            first_help="first 1-indexed block to process, inclusive",
            last_help="last 1-indexed block to process, inclusive",
        )

        # LLM arguments
        add_llm_provider_args(
            arg_groups["llm arguments"], arg_groups["additional help"]
        )
        add_llm_test_case_json_arg(
            arg_groups["llm arguments"],
            help_text="JSON file containing transcription test cases",
        )

        # Cache arguments
        add_cache_args(arg_groups["cache arguments"])

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
            help="overwrite output files if they exist",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        media_infile_path: Path,
        stream_index: int | None,
        language: Language,
        first_block: int | None,
        last_block: int | None,
        demucs_mode: DemucsMode,
        diarization_mode: AudioAnalysisMode,
        language_identification_mode: AudioAnalysisMode,
        audio_event_mode: AudioAnalysisMode,
        block_vad_implementation: VadImplementation,
        lead_in_seconds: float,
        lead_out_seconds: float,
        minimum_duration_seconds: float,
        llm_args: LlmArguments,
        cache_args: CacheArguments,
        json_path: Path | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments.

        Arguments:
            _parser: parser used to report user-facing errors
            media_infile_path: media input file path
            stream_index: optional audio stream index
            language: transcription and output language
            first_block: first included one-based block
            last_block: last included one-based block
            demucs_mode: vocal-separation mode
            diarization_mode: speaker diarization mode
            language_identification_mode: spoken-language identification mode
            audio_event_mode: speech, singing, and music detection mode
            block_vad_implementation: block-planning VAD implementation
            lead_in_seconds: preferred display time before speech begins
            lead_out_seconds: preferred display time after speech ends
            minimum_duration_seconds: preferred minimum subtitle display duration
            llm_args: LLM provider arguments
            cache_args: cache arguments
            json_path: transcription test-case JSON path
            outfile_path: subtitle output path
            overwrite: whether to overwrite existing output files
        """
        parser = _parser or cls.argparser()
        if overwrite and outfile_path is None:
            parser.error("--overwrite requires an output file")
        alignment_outfile_path = None
        run_manifest_outfile_path = None
        if outfile_path is not None:
            alignment_outfile_path = outfile_path.with_suffix(".alignment.json")
            run_manifest_outfile_path = outfile_path.with_suffix(".run.json")
        for output_path in (
            outfile_path,
            alignment_outfile_path,
            run_manifest_outfile_path,
        ):
            if output_path is not None and output_path.exists() and not overwrite:
                parser.error(f"{output_path} already exists")

        start_at_idx, stop_at_idx = get_block_range_indexes(
            parser, first_block, last_block
        )
        try:
            audio = AudioSeries.load_from_media(
                media_path=media_infile_path, stream_index=stream_index
            )
        except ScinoephileError as exc:
            parser.error(str(exc))

        try:
            output = transcribe_series(
                audio,
                language=language,
                audio_event_mode=audio_event_mode,
                demucs_mode=demucs_mode,
                diarization_mode=diarization_mode,
                language_identification_mode=language_identification_mode,
                block_vad_implementation=block_vad_implementation,
                cache_root_path=cache_args.root_path,
                overwrite_cache=cache_args.overwrite,
                provider=get_provider(
                    llm_args.provider_name, model=llm_args.model_name
                ),
                additional_context=read_llm_additional_context(
                    parser, llm_args.additional_context_file_path
                ),
                no_op=llm_args.no_op,
                current_test_cases_path=json_path,
                alignment_outfile_path=alignment_outfile_path,
                run_manifest_outfile_path=run_manifest_outfile_path,
                timing_settings=TimingSettings(
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
