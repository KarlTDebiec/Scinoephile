#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for written Cantonese transcription benchmarking."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path
from shlex import split as split_command

from scinoephile.analysis.character_error_rate import SeriesCER
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
from scinoephile.cli.yue.yue_transcribe_vs_zho_cli import (
    YUE_TRANSCRIBE_VS_ZHO_LOCALIZATIONS,
)
from scinoephile.common.argument_parsing import (
    enum_arg,
    float_arg,
    get_arg_groups_by_name,
    input_dir_arg,
    input_file_arg,
    int_arg,
    output_file_arg,
    str_arg,
)
from scinoephile.common.exceptions import NotAFileError
from scinoephile.core.cli import ScinoephileCliBase, read_series
from scinoephile.core.cli.localization import merge_localizations
from scinoephile.core.exceptions import ScinoephileError
from scinoephile.core.subtitles import Series
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

__all__ = ["YueBenchmarkTranscriptionCli"]

YUE_BENCHMARK_TRANSCRIPTION_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "Benchmark transcription from staged audio and calculate CER": (
            "从已暂存音频基准测试转写并计算 CER"
        ),
        (
            "command-line interface for written Cantonese transcription benchmarking"
        ): "书面粤语转写基准测试命令行界面",
        "staged AudioSeries input directory used for transcription": (
            "用于转写的已暂存 AudioSeries 输入目录"
        ),
        "standard Chinese subtitle infile used for alignment": (
            "用于对齐的标准中文字幕输入文件"
        ),
        "reference written Cantonese subtitle infile used for CER": (
            "用于 CER 的书面粤语参考字幕输入文件"
        ),
        "candidate written Cantonese subtitle outfile path": (
            "书面粤语候选字幕输出文件路径"
        ),
        "CER summary outfile path": "CER 摘要输出文件路径",
        "CER comparison window (options: block, time; default: block)": (
            "CER 比较范围（选项：block、time；默认：block）"
        ),
        "stop after processing this zero-based audio block index": (
            "处理到此从零开始的音频块索引后停止"
        ),
        "directory where transcription test cases are loaded and updated": (
            "载入并更新转写测试用例的目录"
        ),
    },
    "zh-hant": {
        "Benchmark transcription from staged audio and calculate CER": (
            "從已暫存音訊基準測試轉寫並計算 CER"
        ),
        (
            "command-line interface for written Cantonese transcription benchmarking"
        ): "書面粵語轉寫基準測試命令列介面",
        "staged AudioSeries input directory used for transcription": (
            "用於轉寫的已暫存 AudioSeries 輸入目錄"
        ),
        "standard Chinese subtitle infile used for alignment": (
            "用於對齊的標準中文字幕輸入檔"
        ),
        "reference written Cantonese subtitle infile used for CER": (
            "用於 CER 的書面粵語參考字幕輸入檔"
        ),
        "candidate written Cantonese subtitle outfile path": (
            "書面粵語候選字幕輸出檔路徑"
        ),
        "CER summary outfile path": "CER 摘要輸出檔路徑",
        "CER comparison window (options: block, time; default: block)": (
            "CER 比較範圍（選項：block、time；預設：block）"
        ),
        "stop after processing this zero-based audio block index": (
            "處理到此從零開始的音訊區塊索引後停止"
        ),
        "directory where transcription test cases are loaded and updated": (
            "載入並更新轉寫測試案例的目錄"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class YueBenchmarkTranscriptionCli(ScinoephileCliBase):
    """Benchmark transcription from staged audio and calculate CER."""

    localizations = merge_localizations(
        CONVERSION_LOCALIZATIONS,
        LLM_LOCALIZATIONS,
        YUE_TRANSCRIBE_VS_ZHO_LOCALIZATIONS,
        YUE_BENCHMARK_TRANSCRIPTION_LOCALIZATIONS,
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
            "--audio-series-indir",
            dest="audio_series_indir_path",
            required=True,
            type=input_dir_arg(),
            help="staged AudioSeries input directory used for transcription",
        )
        arg_groups["input arguments"].add_argument(
            "--zho-infile",
            dest="zho_infile_path",
            required=True,
            type=input_file_arg(),
            help="standard Chinese subtitle infile used for alignment",
        )
        arg_groups["input arguments"].add_argument(
            "--reference-infile",
            dest="reference_infile_path",
            required=True,
            type=input_file_arg(),
            help="reference written Cantonese subtitle infile used for CER",
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
        arg_groups["operation arguments"].add_argument(
            "--stop-at-idx",
            default=None,
            type=int_arg(min_value=0),
            help="stop after processing this zero-based audio block index",
        )
        arg_groups["operation arguments"].add_argument(
            "--cer-window",
            default="block",
            metavar="{block,time}",
            type=str_arg(options=("block", "time")),
            help="CER comparison window (options: block, time; default: block)",
        )
        arg_groups["operation arguments"].add_argument(
            "--test-case-directory",
            dest="test_case_directory_path",
            default=None,
            type=input_dir_arg(),
            help="directory where transcription test cases are loaded and updated",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "--candidate-outfile",
            dest="candidate_outfile_path",
            required=True,
            type=output_file_arg(exist_ok=True),
            help="candidate written Cantonese subtitle outfile path",
        )
        arg_groups["output arguments"].add_argument(
            "--cer-outfile",
            dest="cer_outfile_path",
            default=None,
            type=output_file_arg(exist_ok=True),
            help="CER summary outfile path",
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
        return "benchmark-transcription"

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
    def _get_series_through_stop_at_idx(
        cls,
        series: Series,
        stop_at_idx: int | None,
    ) -> Series:
        """Get series blocks through a stop index.

        Arguments:
            series: source subtitle series
            stop_at_idx: optional final block index to include
        Returns:
            subtitle series containing only included blocks
        """
        if stop_at_idx is None:
            return series
        if not series.events:
            return series

        end_idx = sum(len(block) for block in series.blocks[: stop_at_idx + 1])
        return series.slice(0, end_idx)

    @classmethod
    def _get_series_in_time_window(
        cls,
        series: Series,
        start_ms: int,
        end_ms: int,
    ) -> Series:
        """Get series events overlapping a time window.

        Arguments:
            series: source subtitle series
            start_ms: inclusive start time in milliseconds
            end_ms: exclusive end time in milliseconds
        Returns:
            subtitle series containing events overlapping the time window
        """
        return Series(
            [
                series.event_class(**event.as_dict())
                for event in series
                if event.end > start_ms and event.start < end_ms
            ]
        )

    @classmethod
    def _get_stop_at_idx_audio_window(
        cls,
        audio_series: AudioSeries,
        stop_at_idx: int | None,
    ) -> tuple[int, int] | None:
        """Get the audio time window through a stop block index.

        Arguments:
            audio_series: staged audio series
            stop_at_idx: optional final block index to include
        Returns:
            start and end times in milliseconds, or None for the full series
        """
        if stop_at_idx is None:
            return None
        blocks = audio_series.blocks[: stop_at_idx + 1]
        if not blocks:
            return None

        start_ms = blocks[0].buffered_start
        if start_ms is None:
            start_ms = blocks[0][0].start
        end_ms = blocks[-1].buffered_end
        if end_ms is None:
            end_ms = blocks[-1][-1].end
        return start_ms, end_ms

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        audio_series_indir_path: Path,
        zho_infile_path: Path,
        reference_infile_path: Path,
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
        convert: OpenCCConfig | None,
        llm_provider_name: str,
        llm_model_name: str | None,
        llm_additional_context_file_path: Path | None,
        script: str,
        stop_at_idx: int | None,
        cer_window: str,
        test_case_directory_path: Path | None,
        candidate_outfile_path: Path,
        cer_outfile_path: Path | None,
        overwrite: bool,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        reference = read_series(parser, reference_infile_path)
        audio_time_window = None
        if cer_window == "time":
            audio_time_window = cls._load_audio_time_window(
                parser,
                audio_series_indir_path,
                stop_at_idx,
            )
        if audio_time_window is None:
            cer_reference = cls._get_series_through_stop_at_idx(reference, stop_at_idx)
        else:
            cer_reference = cls._get_series_in_time_window(
                reference, *audio_time_window
            )

        if candidate_outfile_path.exists() and not overwrite:
            candidate = read_series(parser, candidate_outfile_path)
        else:
            candidate = cls._transcribe(
                parser=parser,
                audio_series_indir_path=audio_series_indir_path,
                zho_infile_path=zho_infile_path,
                backend=backend,
                demucs=demucs,
                vad=vad,
                mimo_model_name=mimo_model_name,
                mimo_tokenizer_name=mimo_tokenizer_name,
                mimo_runtime=mimo_runtime,
                mimo_language=mimo_language,
                mimo_max_tokens=mimo_max_tokens,
                mimo_chunk_duration_seconds=mimo_chunk_duration_seconds,
                mimo_chunk_overlap_seconds=mimo_chunk_overlap_seconds,
                mimo_worker_command=mimo_worker_command,
                mimo_aligner_backend=mimo_aligner_backend,
                mimo_aligner_language=mimo_aligner_language,
                mimo_aligner_model_name=mimo_aligner_model_name,
                mimo_aligner_worker_command=mimo_aligner_worker_command,
                mimo_fallback=mimo_fallback,
                convert=convert,
                llm_provider_name=llm_provider_name,
                llm_model_name=llm_model_name,
                llm_additional_context_file_path=llm_additional_context_file_path,
                script=script,
                stop_at_idx=stop_at_idx,
                test_case_directory_path=test_case_directory_path,
            )
            candidate.save(candidate_outfile_path)
        if audio_time_window is None:
            cer_candidate = cls._get_series_through_stop_at_idx(candidate, stop_at_idx)
        else:
            cer_candidate = cls._get_series_in_time_window(
                candidate, *audio_time_window
            )

        cer = SeriesCER(cer_reference, cer_candidate)
        cer_text = f"{cer}\n"
        print(cer)
        if cer_outfile_path is not None:
            if cer_outfile_path.exists() and not overwrite:
                parser.error(f"{cer_outfile_path} already exists")
            cer_outfile_path.write_text(cer_text, encoding="utf-8")

    @classmethod
    def _load_audio_time_window(
        cls,
        parser: ArgumentParser,
        audio_series_indir_path: Path,
        stop_at_idx: int | None,
    ) -> tuple[int, int] | None:
        """Load staged audio metadata and get the requested time window.

        Arguments:
            parser: parser used for user-facing error output
            audio_series_indir_path: staged AudioSeries directory
            stop_at_idx: optional final block index to include
        Returns:
            start and end times in milliseconds, or None for the full series
        """
        try:
            audio_series = AudioSeries.load(audio_series_indir_path)
        except (
            FileNotFoundError,
            NotADirectoryError,
            NotAFileError,
            ScinoephileError,
            ValueError,
        ) as exc:
            parser.error(str(exc))
        return cls._get_stop_at_idx_audio_window(audio_series, stop_at_idx)

    @classmethod
    def _transcribe(
        cls,
        *,
        parser: ArgumentParser,
        audio_series_indir_path: Path,
        zho_infile_path: Path,
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
        convert: OpenCCConfig | None,
        llm_provider_name: str,
        llm_model_name: str | None,
        llm_additional_context_file_path: Path | None,
        script: str,
        stop_at_idx: int | None,
        test_case_directory_path: Path | None,
    ) -> AudioSeries:
        """Transcribe staged audio and return the candidate series.

        Arguments:
            parser: parser used for user-facing error output
            audio_series_indir_path: staged AudioSeries directory
            zho_infile_path: standard Chinese subtitle path
            backend: ASR backend
            demucs: Demucs preprocessing mode
            vad: Whisper VAD mode
            mimo_model_name: MiMo model name or path
            mimo_tokenizer_name: MiMo tokenizer name or path
            mimo_runtime: MiMo runtime
            mimo_language: language metadata passed to MiMo
            mimo_max_tokens: optional maximum number of MiMo text tokens to generate
            mimo_chunk_duration_seconds: optional chunk duration for MiMo inference
            mimo_chunk_overlap_seconds: context overlap applied to each MiMo chunk
            mimo_worker_command: optional MiMo worker command
            mimo_aligner_backend: MiMo timestamp aligner backend
            mimo_aligner_language: MiMo timestamp aligner language
            mimo_aligner_model_name: optional MiMo timestamp aligner model
            mimo_aligner_worker_command: optional timestamp aligner worker command
            mimo_fallback: whether Whisper and MiMo may fall back to each other
            convert: OpenCC conversion configuration
            llm_provider_name: LLM provider name
            llm_model_name: optional LLM model name
            llm_additional_context_file_path: optional LLM context file path
            script: transcription prompt script
            stop_at_idx: optional final block index to process
            test_case_directory_path: optional transcription test-case directory
        Returns:
            transcribed written Cantonese series
        """
        try:
            yuewen = AudioSeries.load(audio_series_indir_path)
        except (
            FileNotFoundError,
            NotADirectoryError,
            NotAFileError,
            ScinoephileError,
            ValueError,
        ) as exc:
            parser.error(str(exc))
        zhongwen = read_series(parser, zho_infile_path)
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
            additional_context=additional_context,
            deliniation_prompt_cls=deliniation_prompt_cls,
            punctuation_prompt_cls=punctuation_prompt_cls,
            test_case_directory_path=test_case_directory_path,
        )
        return get_yue_transcribed_vs_zho(
            yuewen=yuewen,
            zhongwen=zhongwen,
            transcriber=transcriber,
            stop_at_idx=stop_at_idx,
        )


if __name__ == "__main__":
    YueBenchmarkTranscriptionCli.main()
