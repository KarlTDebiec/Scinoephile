#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for written Cantonese subtitle transcription."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from shlex import split as split_command

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.transcription import MIMO_MODEL_NAME, MIMO_TOKENIZER_NAME
from scinoephile.cli.conversion import (
    CONVERSION_LOCALIZATIONS,
    add_opencc_convert_argument,
)
from scinoephile.cli.llms import (
    LLM_LOCALIZATIONS,
    add_llm_provider_arguments,
    read_llm_additional_context,
)
from scinoephile.common.argument_parsing import (
    enum_arg,
    float_arg,
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
    MimoRuntime,
    TranscriptionBackend,
    VADMode,
    get_yue_transcribed_vs_zho,
    get_yue_vs_zho_transcriber,
)
from scinoephile.multilang.yue_zho.transcription.deliniation import (
    YueDeliniationVsZhoPromptYueHans,
    YueDeliniationVsZhoPromptYueHant,
)
from scinoephile.multilang.yue_zho.transcription.punctuation import (
    YuePunctuationVsZhoPromptYueHans,
    YuePunctuationVsZhoPromptYueHant,
)

__all__ = ["YueTranscribeVsZhoCli"]

YUE_TRANSCRIBE_VS_ZHO_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "audio stream index in media input (default: 0)": (
            "媒体输入中的音频流索引（默认：0）"
        ),
        "ASR backend (options: whisper, mimo; default: whisper)": (
            "ASR 后端（选项：whisper、mimo；默认：whisper）"
        ),
        (
            "command-line interface for written Cantonese subtitle transcription"
        ): "书面粤语字幕转写命令行界面",
        (
            "optional command used to run MiMo in a subprocess, split like shell syntax"
        ): ("用于在子进程中运行 MiMo 的可选命令，按 shell 语法拆分"),
        "disable fallback between Whisper and MiMo backends": (
            "禁用 Whisper 与 MiMo 后端之间的回退"
        ),
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
        (
            "MiMo audio tokenizer name or local path "
            "(default: XiaomiMiMo/MiMo-Audio-Tokenizer)"
        ): (
            "MiMo 音频 tokenizer 名称或本地路径"
            "（默认：XiaomiMiMo/MiMo-Audio-Tokenizer）"
        ),
        (
            "MiMo model name or local model path "
            "(default: mlx-community/MiMo-V2.5-ASR-MLX)"
        ): "MiMo 模型名称或本地模型路径（默认：mlx-community/MiMo-V2.5-ASR-MLX）",
        (
            "MiMo timestamp aligner backend (options: whisperx, ctc; default: whisperx)"
        ): "MiMo 时间戳对齐后端（选项：whisperx、ctc；默认：whisperx）",
        "MiMo timestamp aligner language code (default: zh)": (
            "MiMo 时间戳对齐语言代码（默认：zh）"
        ),
        "MiMo timestamp aligner model name": "MiMo 时间戳对齐模型名称",
        (
            "command used to run the MiMo timestamp aligner worker, "
            "split like shell syntax"
        ): ("运行 MiMo 时间戳对齐 worker 的命令，按 shell 语法拆分"),
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
        "audio stream index in media input (default: 0)": (
            "媒體輸入中的音訊流索引（預設：0）"
        ),
        "ASR backend (options: whisper, mimo; default: whisper)": (
            "ASR 後端（選項：whisper、mimo；預設：whisper）"
        ),
        (
            "command-line interface for written Cantonese subtitle transcription"
        ): "書面粵語字幕轉寫命令列介面",
        (
            "optional command used to run MiMo in a subprocess, split like shell syntax"
        ): ("用於在子行程中執行 MiMo 的可選命令，依 shell 語法拆分"),
        "disable fallback between Whisper and MiMo backends": (
            "停用 Whisper 與 MiMo 後端之間的回退"
        ),
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
        (
            "MiMo audio tokenizer name or local path "
            "(default: XiaomiMiMo/MiMo-Audio-Tokenizer)"
        ): (
            "MiMo 音訊 tokenizer 名稱或本機路徑"
            "（預設：XiaomiMiMo/MiMo-Audio-Tokenizer）"
        ),
        (
            "MiMo model name or local model path "
            "(default: mlx-community/MiMo-V2.5-ASR-MLX)"
        ): "MiMo 模型名稱或本機模型路徑（預設：mlx-community/MiMo-V2.5-ASR-MLX）",
        (
            "MiMo timestamp aligner backend (options: whisperx, ctc; default: whisperx)"
        ): "MiMo 時間戳對齊後端（選項：whisperx、ctc；預設：whisperx）",
        "MiMo timestamp aligner language code (default: zh)": (
            "MiMo 時間戳對齊語言代碼（預設：zh）"
        ),
        "MiMo timestamp aligner model name": "MiMo 時間戳對齊模型名稱",
        (
            "command used to run the MiMo timestamp aligner worker, "
            "split like shell syntax"
        ): ("執行 MiMo 時間戳對齊 worker 的命令，依 shell 語法拆分"),
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
            "--zho-infile",
            dest="zho_infile_path",
            required=True,
            type=input_file_arg(allow_stdin=True),
            help='standard Chinese subtitle infile, or "-" for stdin',
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--asr-backend",
            dest="backend",
            default=TranscriptionBackend.WHISPER,
            metavar="{whisper,mimo}",
            type=enum_arg(TranscriptionBackend),
            help="ASR backend (options: whisper, mimo; default: whisper)",
        )
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
            "--mimo-model-name",
            default=MIMO_MODEL_NAME,
            help=(
                "MiMo model name or local model path "
                "(default: mlx-community/MiMo-V2.5-ASR-MLX)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-tokenizer-name",
            default=MIMO_TOKENIZER_NAME,
            help=(
                "MiMo audio tokenizer name or local path "
                "(default: XiaomiMiMo/MiMo-Audio-Tokenizer)"
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
            "--mimo-worker-command",
            default=None,
            help=(
                "optional command used to run MiMo in a subprocess, "
                "split like shell syntax"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-language",
            default="yue",
            help="MiMo transcription language metadata (default: yue)",
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-max-tokens",
            default=None,
            type=int_arg(min_value=1),
            help="maximum MiMo generation tokens (default: runtime default)",
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-chunk-duration",
            dest="mimo_chunk_duration_seconds",
            default=None,
            type=float_arg(min_value=0.001),
            help="MiMo chunk duration in seconds; disabled by default",
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-chunk-overlap",
            dest="mimo_chunk_overlap_seconds",
            default=1.0,
            type=float_arg(min_value=0.0),
            help="MiMo chunk overlap in seconds (default: 1.0)",
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-aligner",
            dest="mimo_aligner_backend",
            default="whisperx",
            metavar="{whisperx,ctc}",
            type=str_arg(options=("whisperx", "ctc")),
            help=(
                "MiMo timestamp aligner backend (options: whisperx, ctc; "
                "default: whisperx)"
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
            default=None,
            help="MiMo timestamp aligner model name",
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-aligner-worker-command",
            default=None,
            help=(
                "command used to run the MiMo timestamp aligner worker, "
                "split like shell syntax"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--mimo-no-fallback",
            action="store_false",
            default=True,
            dest="mimo_fallback",
            help="disable fallback between Whisper and MiMo backends",
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
            metavar="{simplified,traditional}",
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
        type[YueDeliniationVsZhoPromptYueHans], type[YuePunctuationVsZhoPromptYueHans]
    ]:
        """Get transcription prompt classes for the selected script.

        Arguments:
            script: selected script identifier
        Returns:
            deliniation and punctuation prompt classes
        """
        if script == "traditional":
            return YueDeliniationVsZhoPromptYueHant, YuePunctuationVsZhoPromptYueHant
        return YueDeliniationVsZhoPromptYueHans, YuePunctuationVsZhoPromptYueHans

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        media_infile_path: str,
        zho_infile_path: Path | str,
        stream_index: int,
        script: str,
        convert: OpenCCConfig | None,
        llm_provider_name: str,
        llm_model_name: str | None,
        llm_additional_context_file_path: Path | None,
        backend: TranscriptionBackend,
        demucs: DemucsMode,
        vad: VADMode,
        mimo_model_name: str,
        mimo_tokenizer_name: str,
        mimo_runtime: MimoRuntime,
        mimo_language: str,
        mimo_max_tokens: int | None,
        mimo_chunk_duration_seconds: float | None,
        mimo_chunk_overlap_seconds: float,
        mimo_worker_command: str | None,
        mimo_aligner_backend: str,
        mimo_aligner_language: str,
        mimo_aligner_model_name: str | None,
        mimo_aligner_worker_command: str | None,
        mimo_fallback: bool,
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
        deliniation_prompt_cls, punctuation_prompt_cls = (
            cls._get_transcription_prompt_classes(script)
        )
        additional_context = read_llm_additional_context(
            parser, llm_additional_context_file_path
        )
        provider = get_provider(llm_provider_name, model=llm_model_name)
        parsed_mimo_worker_command = None
        if mimo_worker_command is not None:
            parsed_mimo_worker_command = split_command(mimo_worker_command)
        parsed_mimo_aligner_worker_command = None
        if mimo_aligner_worker_command is not None:
            parsed_mimo_aligner_worker_command = split_command(
                mimo_aligner_worker_command
            )
        transcriber = get_yue_vs_zho_transcriber(
            backend=backend,
            demucs_mode=demucs,
            vad_mode=vad,
            mimo_model_name=mimo_model_name,
            mimo_tokenizer_name=mimo_tokenizer_name,
            mimo_runtime=mimo_runtime,
            mimo_language=mimo_language,
            mimo_max_tokens=mimo_max_tokens,
            mimo_chunk_duration_seconds=mimo_chunk_duration_seconds,
            mimo_chunk_overlap_seconds=mimo_chunk_overlap_seconds,
            mimo_worker_command=parsed_mimo_worker_command,
            mimo_aligner_backend=mimo_aligner_backend,
            mimo_aligner_language=mimo_aligner_language,
            mimo_aligner_model_name=mimo_aligner_model_name,
            mimo_aligner_worker_command=parsed_mimo_aligner_worker_command,
            mimo_fallback=mimo_fallback,
            provider=provider,
            convert=convert,
            deliniation_prompt_cls=deliniation_prompt_cls,
            punctuation_prompt_cls=punctuation_prompt_cls,
            additional_context=additional_context,
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
