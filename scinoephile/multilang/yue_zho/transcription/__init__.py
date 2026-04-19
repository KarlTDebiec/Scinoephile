#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Cantonese transcription tooling for 粤文/中文 workflows."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict, Unpack
from warnings import catch_warnings, filterwarnings

import ffmpeg

from scinoephile.audio.subtitles import AudioSeries
from scinoephile.common import package_root
from scinoephile.common.file import get_temp_directory_path
from scinoephile.common.validation import val_input_path
from scinoephile.core import ScinoephileError
from scinoephile.core.llms import TestCase
from scinoephile.core.paths import get_runtime_cache_dir_path
from scinoephile.core.subtitles import Series
from scinoephile.llms.default_test_cases import (
    YUE_ZHO_TRANSCRIPTION_MERGING_JSON_PATHS,
    YUE_ZHO_TRANSCRIPTION_SHIFTING_JSON_PATHS,
    load_default_test_cases,
)
from scinoephile.llms.dual_pair import DualPairManager
from scinoephile.multilang.yue_zho.transcription.merging import (
    YueZhoHansMergingPrompt,
    YueZhoMergingManager,
)
from scinoephile.multilang.yue_zho.transcription.shifting import (
    YueZhoHansShiftingPrompt,
)

with catch_warnings():
    filterwarnings("ignore", category=SyntaxWarning)
    filterwarnings("ignore", category=RuntimeWarning)
    from pydub import AudioSegment

from .transcriber import YueTranscriber

__all__ = [
    "YueTranscriber",
    "YueZhoTranscriberKwargs",
    "YueZhoTranscriptionKwargs",
    "get_yue_audio_series_for_transcription",
    "get_yue_vs_zho_transcribed",
    "get_yue_vs_zho_transcriber",
]


class YueZhoTranscriptionKwargs(TypedDict, total=False):
    """Keyword arguments for YueTranscriber.process_all_blocks."""

    stop_at_idx: int | None


class YueZhoTranscriberKwargs(TypedDict, total=False):
    """Keyword arguments for default YueTranscriber construction."""

    test_case_directory_path: Path | None
    shifting_test_cases: list[TestCase] | None
    merging_test_cases: list[TestCase] | None


def get_yue_audio_series_for_transcription(
    zhongwen: Series,
    media_path: Path | str,
    stream_index: int = 0,
    buffer: int = 1000,
) -> AudioSeries:
    """Build an AudioSeries for transcription from subtitles and media input.

    Arguments:
        zhongwen: 中文字幕 subtitles with timing data
        media_path: path to video container or audio media file
        stream_index: audio stream index (zero-based)
        buffer: additional buffer to include before and after subtitles (ms)
    Returns:
        AudioSeries aligned to 中文字幕 timings
    """
    validated_media_path = val_input_path(media_path)

    try:
        probe = ffmpeg.probe(str(validated_media_path))
    except ffmpeg.Error as exc:
        raise ScinoephileError(
            f"Could not probe media file {validated_media_path}"
        ) from exc
    streams = probe.get("streams", [])
    audio_streams = [
        stream for stream in streams if stream.get("codec_type") == "audio"
    ]
    if not audio_streams:
        raise ScinoephileError(
            f"No audio streams found in media file {validated_media_path}"
        )
    if stream_index < 0 or stream_index >= len(audio_streams):
        raise ScinoephileError(
            f"Invalid audio stream index {stream_index} for {validated_media_path}; "
            f"found {len(audio_streams)} audio stream(s)."
        )

    stream = audio_streams[stream_index]
    channels = stream.get("channels")
    try:
        channel_count = int(channels)
    except (TypeError, ValueError) as exc:
        raise ScinoephileError(
            f"Audio stream {stream_index} in {validated_media_path} "
            "cannot be used for transcription."
        ) from exc

    with get_temp_directory_path() as temp_dir_path:
        full_audio_path = temp_dir_path / "full_audio.wav"
        try:
            AudioSeries.extract_audio_track(
                validated_media_path, full_audio_path, stream_index, channel_count
            )
            full_audio = AudioSegment.from_wav(full_audio_path)
        except ffmpeg.Error as exc:
            raise ScinoephileError(
                "Could not extract audio stream "
                f"{stream_index} from {validated_media_path}"
            ) from exc

    return AudioSeries.build_series(zhongwen, full_audio, buffer)


def get_yue_vs_zho_transcriber(
    shifting_test_cases: list[TestCase] | None = None,
    merging_test_cases: list[TestCase] | None = None,
    test_case_directory_path: Path | None = None,
) -> YueTranscriber:
    """Get YueTranscriber with default resources when available.

    Arguments:
        shifting_test_cases: optional shifting test cases
        merging_test_cases: optional merging test cases
        test_case_directory_path: optional directory where test cases are updated
    Returns:
        configured YueTranscriber
    """
    if shifting_test_cases is None:
        shifting_test_cases = list(
            load_default_test_cases(
                DualPairManager,
                YueZhoHansShiftingPrompt,
                YUE_ZHO_TRANSCRIPTION_SHIFTING_JSON_PATHS,
            )
        )
    if merging_test_cases is None:
        merging_test_cases = list(
            load_default_test_cases(
                YueZhoMergingManager,
                YueZhoHansMergingPrompt,
                YUE_ZHO_TRANSCRIPTION_MERGING_JSON_PATHS,
            )
        )
    if test_case_directory_path is None:
        default_test_data_dir_path = package_root.parent / "test" / "data" / "mlamd"
        if default_test_data_dir_path.is_dir():
            test_case_directory_path = default_test_data_dir_path
        else:
            test_case_directory_path = get_runtime_cache_dir_path("test_cases")
    return YueTranscriber(
        test_case_directory_path=test_case_directory_path,
        shifting_test_cases=shifting_test_cases,
        merging_test_cases=merging_test_cases,
    )


def get_yue_vs_zho_transcribed(
    zhongwen: Series,
    media_path: Path | str,
    stream_index: int = 0,
    transcriber: YueTranscriber | None = None,
    **kwargs: Unpack[YueZhoTranscriptionKwargs],
) -> AudioSeries:
    """Get initial 粤文 transcription aligned to 中文字幕.

    Arguments:
        zhongwen: 中文字幕 subtitle series
        media_path: path to video container or audio media file
        stream_index: audio stream index (zero-based)
        transcriber: transcriber to use
        **kwargs: additional keyword arguments for YueTranscriber.process_all_blocks
    Returns:
        transcribed 粤文 subtitle series
    """
    yuewen = get_yue_audio_series_for_transcription(
        zhongwen=zhongwen,
        media_path=media_path,
        stream_index=stream_index,
    )
    if transcriber is None:
        transcriber = get_yue_vs_zho_transcriber()
    return transcriber.process_all_blocks(yuewen, zhongwen, **kwargs)
