#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Command-line interface for subtitle timing adjustment."""

from __future__ import annotations

from argparse import ArgumentParser
from pathlib import Path

from scinoephile.audio.speech_activity import WhisperSpeechActivityDetector
from scinoephile.audio.subtitles import AudioSeries
from scinoephile.audio.subtitles.timing_adjustment import (
    SubtitleTimingAdjustmentConfig,
    SubtitleTimingAdjustmentResult,
    get_series_timing_adjustment,
)
from scinoephile.cli.utility.cache.argument_types import cache_dir_path_arg
from scinoephile.common.argument_parsing import (
    get_arg_groups_by_name,
    input_file_arg,
    int_arg,
    output_file_arg,
    str_arg,
)
from scinoephile.core import ScinoephileError
from scinoephile.core.cli import ScinoephileCliBase

__all__ = ["MediaAdjustSubsCli"]

MEDIA_ADJUST_SUBS_LOCALIZATIONS: dict[str, dict[str, str]] = {
    "zh-hans": {
        "adjust subtitle timings using detected speech activity": (
            "使用检测到的语音活动调整字幕时间"
        ),
        (
            "media stream index of audio stream in media input "
            "(default: first audio stream)"
        ): "媒体输入中的音频媒体流索引（默认：第一个音频流）",
        "audio buffer around subtitle blocks in milliseconds (default: %(default)s)": (
            "字幕块前后的音频缓冲，单位为毫秒（默认：%(default)s）"
        ),
        (
            "cache directory for extracted audio and speech activity artifacts "
            "(default: %(default)s)"
        ): "提取音频和语音活动工件的缓存目录（默认：%(default)s）",
        "dry-run without writing adjusted subtitles": "试运行，不写入调整后的字幕",
        "input media file containing audio": "包含音频的媒体输入文件",
        "input subtitle file whose timings should be adjusted": (
            "需要调整时间的字幕输入文件"
        ),
        "maximum end expansion in milliseconds (default: %(default)s)": (
            "结束时间最大扩展量，单位为毫秒（默认：%(default)s）"
        ),
        "maximum start expansion in milliseconds (default: %(default)s)": (
            "开始时间最大提前量，单位为毫秒（默认：%(default)s）"
        ),
        "merge speech gaps at or below this length in milliseconds (default: "
        "%(default)s)": (
            "合并小于或等于此长度的语音间隔，单位为毫秒（默认：%(default)s）"
        ),
        "minimum speech interval duration in milliseconds (default: %(default)s)": (
            "最小语音区间时长，单位为毫秒（默认：%(default)s）"
        ),
        "output subtitle file for adjusted timings": "调整后字幕的输出文件",
        "print timing adjustment diagnostics": "打印时间调整诊断信息",
        "speech activity backend (default: %(default)s)": (
            "语音活动后端（默认：%(default)s）"
        ),
        "subtitle block pause length in milliseconds (default: %(default)s)": (
            "字幕块分隔停顿时长，单位为毫秒（默认：%(default)s）"
        ),
    },
    "zh-hant": {
        "adjust subtitle timings using detected speech activity": (
            "使用偵測到的語音活動調整字幕時間"
        ),
        (
            "media stream index of audio stream in media input "
            "(default: first audio stream)"
        ): "媒體輸入中的音訊媒體流索引（預設：第一個音訊流）",
        "audio buffer around subtitle blocks in milliseconds (default: %(default)s)": (
            "字幕區塊前後的音訊緩衝，單位為毫秒（預設：%(default)s）"
        ),
        (
            "cache directory for extracted audio and speech activity artifacts "
            "(default: %(default)s)"
        ): "提取音訊和語音活動工件的快取目錄（預設：%(default)s）",
        "dry-run without writing adjusted subtitles": "試執行，不寫入調整後的字幕",
        "input media file containing audio": "包含音訊的媒體輸入檔",
        "input subtitle file whose timings should be adjusted": (
            "需要調整時間的字幕輸入檔"
        ),
        "maximum end expansion in milliseconds (default: %(default)s)": (
            "結束時間最大延伸量，單位為毫秒（預設：%(default)s）"
        ),
        "maximum start expansion in milliseconds (default: %(default)s)": (
            "開始時間最大提前量，單位為毫秒（預設：%(default)s）"
        ),
        "merge speech gaps at or below this length in milliseconds (default: "
        "%(default)s)": (
            "合併小於或等於此長度的語音間隔，單位為毫秒（預設：%(default)s）"
        ),
        "minimum speech interval duration in milliseconds (default: %(default)s)": (
            "最小語音區間時長，單位為毫秒（預設：%(default)s）"
        ),
        "output subtitle file for adjusted timings": "調整後字幕的輸出檔",
        "print timing adjustment diagnostics": "列印時間調整診斷資訊",
        "speech activity backend (default: %(default)s)": (
            "語音活動後端（預設：%(default)s）"
        ),
        "subtitle block pause length in milliseconds (default: %(default)s)": (
            "字幕區塊分隔停頓時長，單位為毫秒（預設：%(default)s）"
        ),
    },
}
"""Localized help text keyed by locale and English source text."""


class MediaAdjustSubsCli(ScinoephileCliBase):
    """Adjust subtitle timings using detected speech activity."""

    localizations = MEDIA_ADJUST_SUBS_LOCALIZATIONS
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
            dest="media_infile_path",
            required=True,
            type=input_file_arg(),
            help="input media file containing audio",
        )
        arg_groups["input arguments"].add_argument(
            "--subtitle-infile",
            dest="subtitle_infile_path",
            required=True,
            type=input_file_arg(),
            help="input subtitle file whose timings should be adjusted",
        )
        arg_groups["input arguments"].add_argument(
            "--stream-index",
            default=None,
            type=int_arg(min_value=0),
            help=(
                "media stream index of audio stream in media input "
                "(default: first audio stream)"
            ),
        )

        # Operation arguments
        arg_groups["operation arguments"].add_argument(
            "--buffer",
            default=2000,
            type=int_arg(min_value=0),
            help=(
                "audio buffer around subtitle blocks in milliseconds "
                "(default: %(default)s)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--block-pause-length",
            default=3000,
            type=int_arg(min_value=1),
            help="subtitle block pause length in milliseconds (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--cache-dir",
            default=cache_dir_path_arg("media", "audio"),
            dest="cache_dir_path",
            type=cache_dir_path_arg,
            help=(
                "cache directory for extracted audio and speech activity artifacts "
                "(default: %(default)s)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--vad-backend",
            default="whisper",
            metavar="{whisper}",
            type=str_arg(options=["whisper"]),
            help="speech activity backend (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--max-start-expansion",
            default=750,
            type=int_arg(min_value=0),
            help="maximum start expansion in milliseconds (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--max-end-expansion",
            default=1500,
            type=int_arg(min_value=0),
            help="maximum end expansion in milliseconds (default: %(default)s)",
        )
        arg_groups["operation arguments"].add_argument(
            "--gap-merge-threshold",
            default=150,
            type=int_arg(min_value=0),
            help=(
                "merge speech gaps at or below this length in milliseconds "
                "(default: %(default)s)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--minimum-speech-duration",
            default=100,
            type=int_arg(min_value=0),
            help=(
                "minimum speech interval duration in milliseconds "
                "(default: %(default)s)"
            ),
        )
        arg_groups["operation arguments"].add_argument(
            "--dry-run",
            action="store_true",
            help="dry-run without writing adjusted subtitles",
        )
        arg_groups["operation arguments"].add_argument(
            "--diagnostics",
            action="store_true",
            help="print timing adjustment diagnostics",
        )

        # Output arguments
        arg_groups["output arguments"].add_argument(
            "-o",
            "--outfile",
            dest="outfile_path",
            required=True,
            type=output_file_arg(exist_ok=True),
            help="output subtitle file for adjusted timings",
        )
        parser.set_defaults(_parser=parser)

    @classmethod
    def name(cls) -> str:
        """Name of this tool used to define it when it is a subparser.

        Returns:
            subcommand name
        """
        return "adjust-subs"

    @classmethod
    def _main(
        cls,
        *,
        _parser: ArgumentParser | None = None,
        media_infile_path: Path,
        subtitle_infile_path: Path,
        stream_index: int | None,
        buffer: int,
        block_pause_length: int,
        cache_dir_path: Path,
        vad_backend: str,
        max_start_expansion: int,
        max_end_expansion: int,
        gap_merge_threshold: int,
        minimum_speech_duration: int,
        dry_run: bool,
        diagnostics: bool,
        outfile_path: Path,
    ):
        """Execute with provided keyword arguments."""
        parser = _parser or cls.argparser()
        try:
            series = AudioSeries.load_from_media(
                media_path=media_infile_path,
                subtitle_path=subtitle_infile_path,
                stream_index=stream_index,
                buffer=buffer,
                cache_dir_path=cache_dir_path,
            )
            speech_detector = cls._get_speech_detector(
                vad_backend=vad_backend,
                cache_dir_path=cache_dir_path / "speech",
                merge_gap_ms=gap_merge_threshold,
                min_duration_ms=minimum_speech_duration,
            )
            result = get_series_timing_adjustment(
                series,
                speech_detector=speech_detector,
                config=SubtitleTimingAdjustmentConfig(
                    block_pause_length_ms=block_pause_length,
                    block_audio_buffer_ms=buffer,
                    max_start_expansion_ms=max_start_expansion,
                    max_end_expansion_ms=max_end_expansion,
                    merge_gap_ms=gap_merge_threshold,
                    min_speech_duration_ms=minimum_speech_duration,
                ),
            )
            if dry_run or diagnostics:
                print(cls._get_diagnostics_description(result))
            if not dry_run:
                result.series.save(
                    outfile_path,
                    format_=cls._get_subtitle_output_format(
                        outfile_path=outfile_path,
                        subtitle_infile_path=subtitle_infile_path,
                    ),
                )
        except (ImportError, ScinoephileError, ValueError) as exc:
            parser.error(str(exc))

    @staticmethod
    def _get_diagnostics_description(result: SubtitleTimingAdjustmentResult) -> str:
        """Get human-readable diagnostics summary.

        Arguments:
            result: subtitle timing adjustment result
        Returns:
            human-readable diagnostics summary
        """
        cues = result.cues
        adjusted_count = sum(1 for cue in cues if not cue.unchanged)
        total_start_delta_ms = sum(cue.start_delta_ms for cue in cues)
        total_end_delta_ms = sum(cue.end_delta_ms for cue in cues)
        blocked_start_ms = sum(cue.blocked_start_expansion_ms for cue in cues)
        blocked_end_ms = sum(cue.blocked_end_expansion_ms for cue in cues)
        return "\n".join(
            [
                f"Adjusted cues: {adjusted_count}/{len(cues)}",
                f"Total start delta: {total_start_delta_ms / 1000:+.3f} s",
                f"Total end delta: {total_end_delta_ms / 1000:+.3f} s",
                (
                    "Blocked expansion: "
                    f"start {blocked_start_ms / 1000:+.3f} s, "
                    f"end {blocked_end_ms / 1000:+.3f} s"
                ),
            ]
        )

    @staticmethod
    def _get_speech_detector(
        *,
        vad_backend: str,
        cache_dir_path: Path,
        merge_gap_ms: int,
        min_duration_ms: int,
    ) -> WhisperSpeechActivityDetector:
        """Get the requested speech activity detector.

        Arguments:
            vad_backend: speech activity backend name
            cache_dir_path: cache directory for raw speech activity artifacts
            merge_gap_ms: merge speech intervals separated by at most this gap
            min_duration_ms: discard speech intervals shorter than this duration
        Returns:
            configured speech activity detector
        """
        if vad_backend == "whisper":
            return WhisperSpeechActivityDetector(
                cache_dir_path=cache_dir_path,
                merge_gap_ms=merge_gap_ms,
                min_duration_ms=min_duration_ms,
            )
        raise ValueError(f"Unsupported speech activity backend: {vad_backend}")

    @staticmethod
    def _get_subtitle_output_format(
        *,
        outfile_path: Path,
        subtitle_infile_path: Path,
    ) -> str:
        """Get the explicit subtitle format to pass when saving output.

        Arguments:
            outfile_path: output subtitle file path
            subtitle_infile_path: input subtitle file path
        Returns:
            subtitle format name
        """
        if outfile_path.suffix:
            return outfile_path.suffix.removeprefix(".").lower()
        if subtitle_infile_path.suffix:
            return subtitle_infile_path.suffix.removeprefix(".").lower()
        return "srt"


if __name__ == "__main__":
    MediaAdjustSubsCli.main()
