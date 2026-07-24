#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for reference-guided subtitle transcription.

Transcribe audio using reference subtitles.
"""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from shlex import split as split_command

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import (
    MIMO_MODEL_NAME,
    MimoRuntime,
)
from scinoephile.common.argument_parsing import (
    enum_arg,
    enum_metavar,
    float_arg,
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
    str_arg,
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
        'reference subtitle infile, or "-" for stdin': (
            '参考字幕输入文件，或使用 "-" 表示标准输入'
        ),
        "transcription language tag": "转写语言标签",
        "reference language tag (detected from infile if omitted)": (
            "参考语言标签（省略时从输入文件检测）"
        ),
        "transcription backend (options: whisper, mimo; default: whisper)": (
            "转写后端（选项：whisper、mimo；默认：whisper）"
        ),
        "Demucs vocal-separation mode (options: auto, on, off; default: auto)": (
            "Demucs 人声分离模式（选项：auto、on、off；默认：auto）"
        ),
        (
            "voice activity detection mode (options: on, off, auto; default: auto)"
        ): "语音活动检测模式（选项：on、off、auto；默认：auto）",
        (
            "Whisper model identifier override (uses language-pair default if omitted)"
        ): "Whisper 模型标识符覆盖值（省略时使用语言对默认值）",
        "MiMo runtime (options: auto, mlx; default: auto)": (
            "MiMo 运行时（选项：auto、mlx；默认：auto）"
        ),
        "MiMo transcription language metadata (default: yue)": (
            "MiMo 转写语言元数据（默认：yue）"
        ),
        "maximum MiMo generation tokens (default: runtime default)": (
            "MiMo 生成 token 上限（默认：运行时默认值）"
        ),
        "MiMo chunk duration in seconds; disabled by default": (
            "MiMo 分块时长（秒）；默认禁用"
        ),
        "MiMo chunk overlap in seconds (default: 1.0)": (
            "MiMo 分块重叠时长（秒）（默认：1.0）"
        ),
        (
            "MiMo model name or local model path "
            "(default: mlx-community/MiMo-V2.5-ASR-MLX)"
        ): "MiMo 模型名称或本地模型路径（默认：mlx-community/MiMo-V2.5-ASR-MLX）",
        (
            "optional command used to run MiMo in a subprocess, split like shell syntax"
        ): "用于在子进程中运行 MiMo 的可选命令，按 shell 语法拆分",
        "MiMo timestamp aligner backend (options: ctc, whisperx; default: ctc)": (
            "MiMo 时间戳对齐后端（选项：ctc、whisperx；默认：ctc）"
        ),
        "MiMo timestamp aligner language code (default: zh)": (
            "MiMo 时间戳对齐语言代码（默认：zh）"
        ),
        "MiMo timestamp aligner model name": "MiMo 时间戳对齐模型名称",
        (
            "command used to run the MiMo timestamp aligner worker, "
            "split like shell syntax"
        ): "运行 MiMo 时间戳对齐 worker 的命令，按 shell 语法拆分",
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
        'reference subtitle infile, or "-" for stdin': (
            '參考字幕輸入檔，或使用 "-" 代表標準輸入'
        ),
        "transcription language tag": "轉寫語言標籤",
        "reference language tag (detected from infile if omitted)": (
            "參考語言標籤（省略時從輸入檔偵測）"
        ),
        "transcription backend (options: whisper, mimo; default: whisper)": (
            "轉寫後端（選項：whisper、mimo；預設：whisper）"
        ),
        "Demucs vocal-separation mode (options: auto, on, off; default: auto)": (
            "Demucs 人聲分離模式（選項：auto、on、off；預設：auto）"
        ),
        (
            "voice activity detection mode (options: on, off, auto; default: auto)"
        ): "語音活動偵測模式（選項：on、off、auto；預設：auto）",
        (
            "Whisper model identifier override (uses language-pair default if omitted)"
        ): "Whisper 模型識別碼覆寫值（省略時使用語言對預設值）",
        "MiMo runtime (options: auto, mlx; default: auto)": (
            "MiMo 執行環境（選項：auto、mlx；預設：auto）"
        ),
        "MiMo transcription language metadata (default: yue)": (
            "MiMo 轉寫語言後設資料（預設：yue）"
        ),
        "maximum MiMo generation tokens (default: runtime default)": (
            "MiMo 產生 token 上限（預設：執行環境預設值）"
        ),
        "MiMo chunk duration in seconds; disabled by default": (
            "MiMo 分段長度（秒）；預設停用"
        ),
        "MiMo chunk overlap in seconds (default: 1.0)": (
            "MiMo 分段重疊長度（秒）（預設：1.0）"
        ),
        (
            "MiMo model name or local model path "
            "(default: mlx-community/MiMo-V2.5-ASR-MLX)"
        ): "MiMo 模型名稱或本機模型路徑（預設：mlx-community/MiMo-V2.5-ASR-MLX）",
        (
            "optional command used to run MiMo in a subprocess, split like shell syntax"
        ): "用於在子行程中執行 MiMo 的可選命令，依 shell 語法拆分",
        "MiMo timestamp aligner backend (options: ctc, whisperx; default: ctc)": (
            "MiMo 時間戳對齊後端（選項：ctc、whisperx；預設：ctc）"
        ),
        "MiMo timestamp aligner language code (default: zh)": (
            "MiMo 時間戳對齊語言代碼（預設：zh）"
        ),
        "MiMo timestamp aligner model name": "MiMo 時間戳對齊模型名稱",
        (
            "command used to run the MiMo timestamp aligner worker, "
            "split like shell syntax"
        ): "執行 MiMo 時間戳對齊 worker 的命令，依 shell 語法拆分",
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
            "--reference-infile",
            dest="reference_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='reference subtitle infile, or "-" for stdin',
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
            help="transcription language tag",
        )
        arg_groups["operation arguments"].add_argument(
            "--reference-language",
            metavar=enum_metavar(Language),
            type=enum_arg(Language),
            help="reference language tag (detected from infile if omitted)",
        )
        add_block_range_args(arg_groups["operation arguments"])
        arg_groups["operation arguments"].add_argument(
            "--backend",
            default=TranscriptionBackend.WHISPER,
            metavar="{whisper,mimo}",
            type=enum_arg(TranscriptionBackend),
            help=("transcription backend (options: whisper, mimo; default: whisper)"),
        )
        arg_groups["operation arguments"].add_argument(
            "--demucs",
            default=DemucsMode.AUTO,
            dest="demucs_mode",
            metavar="{auto,on,off}",
            type=enum_arg(DemucsMode),
            help=(
                "Demucs vocal-separation mode (options: auto, on, off; default: auto)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--vad",
            default=VADMode.AUTO,
            dest="vad_mode",
            metavar="{auto,on,off}",
            type=enum_arg(VADMode),
            help=(
                "voice activity detection mode (options: on, off, auto; default: auto)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--whisper-model",
            dest="model_name",
            help=(
                "Whisper model identifier override "
                "(uses language-pair default if omitted)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-runtime",
            default=MimoRuntime.AUTO,
            metavar="{auto,mlx}",
            type=enum_arg(MimoRuntime),
            help="MiMo runtime (options: auto, mlx; default: auto)",
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-language",
            default="yue",
            help="MiMo transcription language metadata (default: yue)",
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-max-tokens",
            type=int_arg(min_value=1),
            help="maximum MiMo generation tokens (default: runtime default)",
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-chunk-duration",
            dest="mimo_chunk_duration_seconds",
            type=float_arg(min_value=0.001),
            help="MiMo chunk duration in seconds; disabled by default",
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-chunk-overlap",
            default=1.0,
            dest="mimo_chunk_overlap_seconds",
            type=float_arg(min_value=0.0),
            help="MiMo chunk overlap in seconds (default: 1.0)",
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-model",
            default=MIMO_MODEL_NAME,
            dest="mimo_model_name",
            help=(
                "MiMo model name or local model path "
                "(default: mlx-community/MiMo-V2.5-ASR-MLX)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-worker-command",
            help=(
                "optional command used to run MiMo in a subprocess, "
                "split like shell syntax"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-aligner",
            default="ctc",
            dest="mimo_aligner_backend",
            metavar="{ctc,whisperx}",
            type=str_arg(options=("ctc", "whisperx")),
            help=(
                "MiMo timestamp aligner backend (options: ctc, whisperx; default: ctc)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-aligner-language",
            default="zh",
            help="MiMo timestamp aligner language code (default: zh)",
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-aligner-model",
            dest="mimo_aligner_model_name",
            help="MiMo timestamp aligner model name",
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-aligner-worker-command",
            help=(
                "command used to run the MiMo timestamp aligner worker, "
                "split like shell syntax"
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
        reference_infile_path: Path | str,
        stream_index: int | None,
        language: Language,
        reference_language: Language | None,
        first_block: int | None,
        last_block: int | None,
        backend: TranscriptionBackend,
        demucs_mode: DemucsMode,
        vad_mode: VADMode,
        model_name: str | None,
        mimo_runtime: MimoRuntime,
        mimo_language: str,
        mimo_max_tokens: int | None,
        mimo_chunk_duration_seconds: float | None,
        mimo_chunk_overlap_seconds: float,
        mimo_model_name: str,
        mimo_worker_command: str | None,
        mimo_aligner_backend: str,
        mimo_aligner_language: str,
        mimo_aligner_model_name: str | None,
        mimo_aligner_worker_command: str | None,
        llm_args: LlmArguments,
        delineation_json_path: Path | None,
        punctuation_json_path: Path | None,
        outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        # Validate arguments
        parser = _parser or cls.argparser()
        if media_infile_path == "-" and reference_infile_path == "-":
            parser.error("MEDIA_INFILE and --reference-infile may not both be '-'")
        if overwrite and outfile_path is None:
            parser.error("--overwrite may only be used with --outfile")

        # Read inputs
        reference = read_series(parser, reference_infile_path, allow_stdin=True)
        start_at_idx, stop_at_idx = get_block_range_indexes(
            parser,
            first_block,
            last_block,
            len(reference.blocks),
        )
        try:
            if reference_infile_path == "-":
                with get_temp_file_path(suffix=".srt") as temp_reference_path:
                    reference.save(temp_reference_path)
                    audio = AudioSeries.load_from_media(
                        media_path=media_infile_path,
                        subtitle_path=temp_reference_path,
                        stream_index=stream_index,
                    )
            else:
                audio = AudioSeries.load_from_media(
                    media_path=media_infile_path,
                    subtitle_path=reference_infile_path,
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
        parsed_mimo_worker_command = None
        if mimo_worker_command is not None:
            parsed_mimo_worker_command = split_command(mimo_worker_command)
        parsed_mimo_aligner_worker_command = None
        if mimo_aligner_worker_command is not None:
            parsed_mimo_aligner_worker_command = split_command(
                mimo_aligner_worker_command
            )
        try:
            output = transcribe_series_guided(
                audio,
                reference,
                language=language,
                reference_language=reference_language,
                model_name=model_name,
                backend=backend,
                demucs_mode=demucs_mode,
                vad_mode=vad_mode,
                mimo_model_name=mimo_model_name,
                mimo_runtime=mimo_runtime,
                mimo_language=mimo_language,
                mimo_max_tokens=mimo_max_tokens,
                mimo_chunk_duration_seconds=mimo_chunk_duration_seconds,
                mimo_chunk_overlap_seconds=mimo_chunk_overlap_seconds,
                mimo_worker_command=parsed_mimo_worker_command,
                mimo_aligner_backend=mimo_aligner_backend,
                mimo_aligner_language=mimo_aligner_language,
                mimo_aligner_model_name=mimo_aligner_model_name,
                mimo_aligner_worker_command=(parsed_mimo_aligner_worker_command),
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
