#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for guided and unguided subtitle transcription.

Transcribe audio with optional reference subtitle guidance.
"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.audio.diarization import DiarizationMode
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import DemucsMode, VADImplementation, VADMode
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
from scinoephile.lang.transcription import TranscriptionBackend
from scinoephile.llms.providers.registry import get_provider
from scinoephile.workflows.transcription import (
    transcribe_series_guided,
    transcribe_series_unguided,
)

from .helpers.blocks import (
    BLOCK_LOCALIZATIONS,
    add_block_range_args,
    get_block_range_indexes,
)
from .helpers.cache import CACHE_LOCALIZATIONS, CacheArguments, add_cache_args
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
        "command-line interface for guided and unguided subtitle transcription": (
            "引导及无引导字幕转写命令行界面"
        ),
        "Transcribe audio with optional reference subtitle guidance.": (
            "使用可选参考字幕引导转写音频。"
        ),
        "media infile used for transcription": "用于转写的媒体输入文件",
        (
            "media stream index of audio stream in media input "
            "(default: first audio stream)"
        ): "媒体输入中的音频媒体流索引（默认：第一个音频流）",
        'guide subtitle infile, or "-" for stdin (required unless unguided)': (
            '引导字幕输入文件，或使用 "-" 表示标准输入（无引导模式除外）'
        ),
        "transcribe and delineate without reference subtitles": (
            "无需参考字幕进行转写及断句"
        ),
        "merge Whisper, MiMo, and Qwen before unguided delineation": (
            "在无引导断句前合并 Whisper、MiMo 和 Qwen"
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
        (
            f"speaker diarization mode (options: "
            f"{enum_options_list_str(DiarizationMode)}; default: %(default)s)"
        ): "说话人分离模式（选项：auto、on 或 off；默认：%(default)s）",
        (
            f"voice activity detection implementation (options: "
            f"{enum_options_list_str(VADImplementation)}; default: %(default)s)"
        ): "语音活动检测实现（选项：silero、ten 或 pyannote；默认：%(default)s）",
        (
            f"unguided block-planning VAD implementation (options: "
            f"{enum_options_list_str(VADImplementation)}; default: pyannote)"
        ): "无引导区块规划 VAD 实现（选项：silero、ten 或 pyannote；默认：pyannote）",
        "transcription model (default: backend default)": (
            "转写模型（默认：后端默认值）"
        ),
        "guard constrained MLX-Audio models against generation-token omissions": (
            "防止受限的 MLX-Audio 模型因生成词元限制而遗漏内容"
        ),
        "JSON file containing delineation test cases": ("包含断句测试用例的 JSON 文件"),
        "JSON file containing punctuation test cases": ("包含标点测试用例的 JSON 文件"),
        "subtitle outfile path (default: stdout)": (
            "字幕输出文件路径（默认：标准输出）"
        ),
        "transcribe audio using reference subtitles": "使用参考字幕转写音频",
    },
    "zh-hant": {
        "command-line interface for guided and unguided subtitle transcription": (
            "引導及無引導字幕轉寫命令列介面"
        ),
        "Transcribe audio with optional reference subtitle guidance.": (
            "使用可選參考字幕引導轉寫音訊。"
        ),
        "media infile used for transcription": "用於轉寫的媒體輸入檔",
        (
            "media stream index of audio stream in media input "
            "(default: first audio stream)"
        ): "媒體輸入中的音訊媒體流索引（預設：第一個音訊流）",
        'guide subtitle infile, or "-" for stdin (required unless unguided)': (
            '引導字幕輸入檔，或使用 "-" 代表標準輸入（無引導模式除外）'
        ),
        "transcribe and delineate without reference subtitles": (
            "無需參考字幕進行轉寫及斷句"
        ),
        "merge Whisper, MiMo, and Qwen before unguided delineation": (
            "在無引導斷句前合併 Whisper、MiMo 和 Qwen"
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
        (
            f"speaker diarization mode (options: "
            f"{enum_options_list_str(DiarizationMode)}; default: %(default)s)"
        ): "說話者分離模式（選項：auto、on 或 off；預設：%(default)s）",
        (
            f"voice activity detection implementation (options: "
            f"{enum_options_list_str(VADImplementation)}; default: %(default)s)"
        ): "語音活動偵測實作（選項：silero、ten 或 pyannote；預設：%(default)s）",
        (
            f"unguided block-planning VAD implementation (options: "
            f"{enum_options_list_str(VADImplementation)}; default: pyannote)"
        ): "無引導區塊規劃 VAD 實作（選項：silero、ten 或 pyannote；預設：pyannote）",
        "transcription model (default: backend default)": (
            "轉寫模型（預設：後端預設值）"
        ),
        "guard constrained MLX-Audio models against generation-token omissions": (
            "防止受限的 MLX-Audio 模型因生成詞元限制而遺漏內容"
        ),
        "JSON file containing delineation test cases": ("包含斷句測試案例的 JSON 檔"),
        "JSON file containing punctuation test cases": ("包含標點測試案例的 JSON 檔"),
        "subtitle outfile path (default: stdout)": ("字幕輸出檔路徑（預設：標準輸出）"),
        "transcribe audio using reference subtitles": "使用參考字幕轉寫音訊",
    },
}
"""Localized help text keyed by locale and English source text."""


class TranscribeCli(ScinoephileCliBase):
    """Transcribe audio with optional reference subtitle guidance."""

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
            help="media infile used for transcription",
        )
        arg_groups["input arguments"].add_argument(
            "--guide-infile",
            dest="guide_infile_path",
            type=input_file_arg(allow_stdin=True),
            help=('guide subtitle infile, or "-" for stdin (required unless unguided)'),
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
            "--unguided",
            action="store_true",
            help="transcribe and delineate without reference subtitles",
        )
        arg_groups["operation arguments"].add_argument(
            "--multi-source",
            action="store_true",
            help="merge Whisper, MiMo, and Qwen before unguided delineation",
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
            default=DemucsMode.OFF,
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
            default=VADMode.OFF,
            dest="vad_mode",
            metavar=enum_metavar(VADMode),
            type=enum_arg(VADMode),
            help=(
                f"voice activity detection mode (options: "
                f"{enum_options_list_str(VADMode)}; default: %(default)s)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--diarization",
            default=DiarizationMode.OFF,
            dest="diarization_mode",
            metavar=enum_metavar(DiarizationMode),
            type=enum_arg(DiarizationMode),
            help=(
                f"speaker diarization mode (options: "
                f"{enum_options_list_str(DiarizationMode)}; default: %(default)s)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--vad-implementation",
            default=VADImplementation.SILERO,
            metavar=enum_metavar(VADImplementation),
            type=enum_arg(VADImplementation),
            help=(
                f"voice activity detection implementation (options: "
                f"{enum_options_list_str(VADImplementation)}; default: %(default)s)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--block-vad-implementation",
            metavar=enum_metavar(VADImplementation),
            type=enum_arg(VADImplementation),
            help=(
                f"unguided block-planning VAD implementation (options: "
                f"{enum_options_list_str(VADImplementation)}; default: pyannote)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--model",
            dest="model_name",
            help="transcription model (default: backend default)",
        )
        arg_groups["operation arguments"].add_argument(
            "--mlx-audio-token-limit-guard",
            action="store_true",
            help=(
                "guard constrained MLX-Audio models against generation-token omissions"
            ),
        )
        add_llm_provider_args(
            arg_groups["llm arguments"], arg_groups["additional help"]
        )
        add_llm_test_case_json_arg(
            arg_groups["llm arguments"],
            "--delineation-json",
            dest="delineation_json_path",
            help_text="JSON file containing delineation test cases",
        )
        add_llm_test_case_json_arg(
            arg_groups["llm arguments"],
            "--punctuation-json",
            dest="punctuation_json_path",
            help_text="JSON file containing punctuation test cases",
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
            "--overwrite", action="store_true", help="overwrite outfile if it exists"
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        media_infile_path: str,
        guide_infile_path: Path | str | None,
        stream_index: int | None,
        language: Language,
        unguided: bool,
        multi_source: bool,
        guide_language: Language | None,
        first_block: int | None,
        last_block: int | None,
        backend: TranscriptionBackend,
        demucs_mode: DemucsMode,
        vad_mode: VADMode,
        diarization_mode: DiarizationMode,
        vad_implementation: VADImplementation,
        block_vad_implementation: VADImplementation | None,
        model_name: str | None,
        mlx_audio_token_limit_guard: bool,
        llm_args: LlmArguments,
        cache_args: CacheArguments,
        delineation_json_path: Path | None,
        punctuation_json_path: Path | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        cls._validate_mode_arguments(
            parser,
            media_infile_path=media_infile_path,
            guide_infile_path=guide_infile_path,
            guide_language=guide_language,
            first_block=first_block,
            last_block=last_block,
            block_vad_implementation=block_vad_implementation,
            unguided=unguided,
            multi_source=multi_source,
            backend=backend,
            model_name=model_name,
            delineation_json_path=delineation_json_path,
            punctuation_json_path=punctuation_json_path,
            outfile_path=outfile_path,
            overwrite=overwrite,
        )

        # Read complete audio directly in unguided mode
        if unguided:
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
            multi_source_provider = None
            multi_source_additional_context = None
            try:
                if multi_source:
                    multi_source_provider = get_provider(
                        llm_args.provider_name, model=llm_args.model_name
                    )
                    multi_source_additional_context = read_llm_additional_context(
                        parser, llm_args.additional_context_file_path
                    )
                output = transcribe_series_unguided(
                    audio,
                    language=language,
                    multi_source=multi_source,
                    model_name=model_name,
                    backend=backend,
                    demucs_mode=demucs_mode,
                    vad_mode=vad_mode,
                    diarization_mode=diarization_mode,
                    vad_implementation=vad_implementation,
                    block_vad_implementation=(
                        block_vad_implementation or VADImplementation.PYANNOTE
                    ),
                    mlx_audio_token_limit_guard=mlx_audio_token_limit_guard,
                    cache_root_path=cache_args.root_path,
                    overwrite_cache=cache_args.overwrite,
                    provider=multi_source_provider,
                    additional_context=multi_source_additional_context,
                    no_op=llm_args.no_op,
                    start_at_idx=start_at_idx,
                    stop_at_idx=stop_at_idx,
                )
            except ScinoephileError as exc:
                parser.error(str(exc))
            write_series(
                parser,
                output,
                outfile_path if outfile_path is not None else "-",
                overwrite,
            )
            return

        # Read guided inputs
        assert guide_infile_path is not None
        guide = read_series(parser, guide_infile_path, allow_stdin=True)
        start_at_idx, stop_at_idx = get_block_range_indexes(
            parser, first_block, last_block, len(guide.blocks)
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
                guide_language=guide_language,
                model_name=model_name,
                backend=backend,
                demucs_mode=demucs_mode,
                vad_mode=vad_mode,
                mlx_audio_token_limit_guard=mlx_audio_token_limit_guard,
                diarization_mode=diarization_mode,
                vad_implementation=vad_implementation,
                cache_root_path=cache_args.root_path,
                overwrite_cache=cache_args.overwrite,
                provider=get_provider(
                    llm_args.provider_name, model=llm_args.model_name
                ),
                additional_context=read_llm_additional_context(
                    parser, llm_args.additional_context_file_path
                ),
                no_op=llm_args.no_op,
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

    @staticmethod
    def _validate_mode_arguments(
        parser: ArgumentParser,
        *,
        media_infile_path: str,
        guide_infile_path: Path | str | None,
        guide_language: Language | None,
        first_block: int | None,
        last_block: int | None,
        block_vad_implementation: VADImplementation | None,
        unguided: bool,
        multi_source: bool,
        backend: TranscriptionBackend,
        model_name: str | None,
        delineation_json_path: Path | None,
        punctuation_json_path: Path | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Validate arguments that depend on guided or unguided mode.

        Arguments:
            parser: active argument parser
            media_infile_path: media input file path or standard-input marker
            guide_infile_path: guide subtitle path or standard-input marker
            guide_language: explicit guide language
            first_block: first selected guided block
            last_block: last selected guided block
            block_vad_implementation: explicitly selected unguided block VAD
            unguided: whether reference-free transcription is selected
            multi_source: whether to merge three ASR sources before delineation
            backend: selected single-source transcription backend
            model_name: selected single-source model override
            delineation_json_path: guided delineation test-case path
            punctuation_json_path: guided punctuation test-case path
            outfile_path: subtitle output path
            overwrite: whether an existing output may be replaced
        """
        if not unguided and guide_infile_path is None:
            parser.error("--guide-infile is required unless --unguided is used")
        if unguided and guide_infile_path is not None:
            parser.error("--guide-infile cannot be used with --unguided")
        if unguided and guide_language is not None:
            parser.error("--guide-language cannot be used with --unguided")
        if not unguided and block_vad_implementation is not None:
            parser.error("--block-vad-implementation requires --unguided")
        if multi_source and not unguided:
            parser.error("--multi-source requires --unguided")
        if multi_source and backend is not TranscriptionBackend.WHISPER:
            parser.error("--backend cannot be changed with --multi-source")
        if multi_source and model_name is not None:
            parser.error("--model cannot be used with --multi-source")
        if unguided and (
            delineation_json_path is not None or punctuation_json_path is not None
        ):
            parser.error("guided LLM test-case files cannot be used with --unguided")
        if media_infile_path == "-" and guide_infile_path == "-":
            parser.error("--media-infile and --guide-infile may not both be '-'")
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")


if __name__ == "__main__":
    TranscribeCli.main()
